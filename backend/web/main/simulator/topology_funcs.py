import importlib
import logging
import os
import time
from copy import deepcopy
from random import randint, shuffle
from statistics import mean
from tokenize import String
from typing import Any, Dict, List, Literal, Optional, Tuple, TypeAlias, Union

import numpy as np
import pandas as pd
# from qntsim.communication.interface import Interface
from qntsim.communication.network import Network
from qntsim.communication.protocol import ProtocolPipeline
from qntsim.components.photon import Photon
from qntsim.kernel.circuit import BaseCircuit
from qntsim.topology.topology import Topology
from tabulate import tabulate

from .app.e2e import *
from .app.e91 import *
from .app.ghz import *
from .app.ip1 import *
from .app.ping_pong import ping_pong
from .app.qsdc1 import *
from .app.teleportation import *
from .app.utils import *
from .helpers import *

# from contextlib import nullcontext
# from pprint import pprint

# Do Not Remove the following commented imports - this is for local testing purpose
# from app.e2e import *
# from app.e91 import *
# from app.ghz import *
# from app.ip1 import *
# from app.mdi_qsdc import *
# from app.ping_pong import *
# from app.qsdc1 import *
# from app.qsdc_teleportation import *
# from app.single_photon_qd import *
# from app.teleportation import *
# from app.utils import *
# from helpers import *
# from pyvis.network import Network
# from qntsim.library.protocol_handler.protocol_handler import Protocol
# from qntsim.library.protocol_handler.protocol_handler import Protocol

logger = logging.getLogger("main_logger." + "topology_funs")
print("TOPP")
print(logger.handlers)

__local_circuit_json_type: TypeAlias = Dict[str, List[Dict[str, Union[str, Dict[str, Dict[str, Any]]]]]]
__global_circuit_json_type: TypeAlias = Dict[str, __local_circuit_json_type]

# def custom_executor(appParams: Dict[str, Dict[str, str]],
#                     circuit: __global_circuit_json_type,
#                     topology: Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]]):
#     senders = [node for node, msgParams in appParams.items() if msgParams.get("message") != ""]
#     messages = {(sender, *[node for node in appParams if node != sender]): appParams.get(sender).get("message") for sender in senders}
#     interface = Interface(topology=topology, messages=messages, require_entanglement=not should_transmit(circuit))
#     quantum_circuits = {node_name: create_circuit_object(circuit=circuit) for node_name, circuit in circuit.items()}
#     node_map = {}
#     qubit_num = -1
#     for node_name, cirq in circuit.items():
#         qubits = []
#         for _ in cirq:
#             qubit_num += 1
#             qubits.append(qubit_num)
#         node_map.update({node_name: qubits})

# def should_transmit(circuit_json: __global_circuit_json_type) -> bool:
#     for local_circuit in circuit_json.values():
#         for gates in local_circuit.values():
#             for gate in gates:
#                 if gate.get("value") == "transmit": return True
#     return False

# def generate_full_circuit(circuit_json: __global_circuit_json_type,
#                           circuit_obj_type: Literal["qiskit", "qutip"] = "qiskit") -> BaseCircuit:
#     circuit: BaseCircuit = BaseCircuit(circuit_obj_type, sum(len(cirq) for cirq in circuit_json.values()))
#     qubit_pos = -1
#     for cirq in circuit_json.values():
#         local_circuit: BaseCircuit = create_circuit_object(cirq, circuit_obj_type)
#         qubit_map: Dict[int, int] = {}
#         for i in range(local_circuit.num_qubits):
#             qubit_pos += 1
#             qubit_map.update({i: qubit_pos})
#         circuit.combine_circuit(local_circuit, qubit_map)
#     return circuit

# def create_circuit_object(circuit: __local_circuit_json_type,
#                           circuit_obj_type: Literal["qiskit", "qutip"] = "qiskit") -> BaseCircuit:
#     circuit: BaseCircuit = BaseCircuit(circuit_obj_type, len(circuit))
#     qubit_num = -1
#     for gates in circuit.values():
#         qubit_num += 1
#         qubits = [qubit_num]
#         for gate_index, gate in enumerate(gates):
#             angles = []
#             match gate.get("value"):
#                 case "i": continue
#                 case "control": gate, qubits = get_controlled_gate(circuit, gate_index)
#                 case "swap": gate, qubits = get_swap_partner(circuit, qubit_num, gate_index)
#                 case str() if "params" in gate: angles = [float(angle.get("value", 0)) for angle in gate.get("params", {}).values()]
#             gate = gate.get("value")
#             circuit.apply_gate(gate, qubits, angles)
#     return circuit

# def get_controlled_gate(circuit_json: Union[__global_circuit_json_type, __local_circuit_json_type],
#                         layer_index: int) -> Tuple[Dict[str, str], List[int]]:
#     gate_name = ""
#     qubit_pos = -1
#     qubits = []
#     for cirq in circuit_json.values():
#         for gates in cirq.values():
#             qubit_pos += 1
#             gate = gates[layer_index].get("value")
#             if gate != "i":
#                 gate_name += gate[0]
#                 qubits.append(qubit_pos)
#                 gates[layer_index]["value"] = "i"
#     return {"value": gate_name}, qubits

# def get_swap_partner(circuit_json: Union[__global_circuit_json_type, __local_circuit_json_type],
#                      qubit_index: int, layer_index: int) -> Tuple[Dict[str, str], List[int]]:
#     qubit_pos = -1
#     qubits = [qubit_index]
#     for cirq in circuit_json.values():
#         for gates in cirq.values():
#             qubit_pos += 1
#             gate = gates[layer_index].get("value")
#             if gate == "swap":
#                 gates[layer_index]["value"] = "i"
#                 if qubit_pos not in qubits:
#                     qubits.append(qubit_pos)
#                     return {"value": "swap"}, qubits

def display_quantum_state(state_vector):
    """
    Converts a quantum state vector to Dirac notation and returns it as a string.

    Parameters:
    state_vector (numpy.ndarray): An array representing a quantum state vector.

    Returns:
    str: A string representing the input state vector in Dirac notation.
    """

    # Normalize the state vector to ensure its Euclidean norm is equal to 1.
    norm = np.linalg.norm(state_vector)
    if norm < 1e-15:
        return "Invalid state: zero norm"
    normalized_state = state_vector / norm

    # Determine the number of qubits required to represent the state vector.
    dim = len(normalized_state)
    num_digits = int(np.ceil(np.log2(dim)))

    # Generate a list of all possible basis states and initialize the output string.
    basis_states = [format(i, f"0{num_digits}b") for i in range(dim)]
    output_str = ""

    # Iterate over the basis states and add their contribution to the output string.
    for i in range(dim):
        coeff = normalized_state[i]
        if abs(coeff) > 1e-15:  # Ignore small coefficients that round to 0.
            if abs(coeff.imag) > 1e-15:  # Handle complex coefficients.
                output_str += (f"({coeff.real:.2f}" if coeff.real > 0 else "(") + (
                    "+" if coeff.real > 0 and coeff.imag > 0 else "") + f"{coeff.imag:.2f}j)|"
            else:
                output_str += f"({coeff.real:.2f})|"
            output_str += basis_states[i] + "> + "
    output_str = output_str[:-3]  # Remove the trailing " + " at the end.

    return output_str


def graph_topology(network_config_json):

    network_config_json, tl, network_topo = load_topology(
        network_config_json, "Qiskit")
    print(f'Making graph')
    graph = network_topo.get_virtual_graph()
    print(network_topo)
    return graph


def network_graph(network_topo, source_node_list, report):

    performance = {}
    t = 0
    timel, fidelityl, latencyl, fc_throughl, pc_throughl, nc_throughl = [], [], [], [], [], []

    while t < 20:  # Pass endtime of simulation instead of 20

        fidelityl = calcfidelity(network_topo, source_node_list, t, fidelityl)
        latencyl = calclatency(network_topo, source_node_list, t, latencyl)
        fc_throughl, pc_throughl, nc_throughl = throughput(
            network_topo, source_node_list, t, fc_throughl, pc_throughl, nc_throughl)
        t = t+1
        timel.append(t)
    latency, fidelity, through = 0, 0, 100
    for i in latencyl:
        if i > 0:
            latency = i
    for i in fidelityl:
        if i > 0:
            fidelity = i
    for i in fc_throughl:
        if i > 0:
            through = i
    execution_time = 3
    performance["latency"] = latency
    performance["fidelity"] = fidelity
    performance["throughput"] = through

    # graph["throughput"]["fully_complete"]= fc_throughl
    # graph["throughput"]["partially_complete"]= pc_throughl
    # graph["throughput"]["rejected"]= nc_throughl        #{fc_throughl,pc_throughl,nc_throughl}
    # graph["time"] = timel
    report["performance"] = performance
    print(report)
    return report


def eve_e91(network_config, sender, receiver, keyLength):
    network_config_json, tl, network_topo = load_topology(
        network_config, "Qutip")
    trials = 4
    while (trials > 0):
        if keyLength <= 0 or keyLength > 30:
            return {"Error_Msg": "keyLength Should be Greater than 0 and less than 30 .Retry Again"}
        if keyLength <= 30 and keyLength > 0:
            # n=int((9*key_length)/2)
            n = int(8*keyLength)
            alice = network_topo.nodes[sender]
            bob = network_topo.nodes[receiver]
            e91 = E91()
            alice, bob, source_node_list = e91.roles(alice, bob, n)
            tl.init()
            tl.run()
            results = e91.eve_run(alice, bob, n)
            if keyLength < len(results["sender_keys"]):
                results["sender_keys"] = results["sender_keys"][:keyLength]
                results["receiver_keys"] = results["receiver_keys"][:keyLength]
                results["sifted_keylength"] = keyLength
            report = {}
            report["application"] = results
            report = network_graph(network_topo, source_node_list, report)
            print(report)
            return report
        trials = trials-1
    return {"Error_Msg": "Couldn't generate required length.Retry Again"}


def e91(network_config, sender, receiver, keyLength, noise: Dict[str, List[float]] = {}):
    logger.info("E91 Quantum Key Distribution")
    print('In e91 network config', network_config)
    start_time = time.time()
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
    print('network topo', network_topo)
    trials = 4
    while (trials > 0):
        if keyLength <= 0 or keyLength > 30:
            return {"Error_Msg": "keyLength Should be Greater than 0 and less than 30 .Retry Again"}

        if keyLength <= 30 and keyLength > 0:
            # n=int((9*key_length)/2)
            n = int(8*keyLength)
            alice = network_topo.nodes[sender]
            bob = network_topo.nodes[receiver]
            e91 = E91()
            alice, bob, source_node_list = e91.roles(alice, bob, n)
            tl.init()
            tl.run()
            results = e91.run(alice, bob, n, noise)
            if keyLength < len(results["sender_keys"]):
                results["sender_keys"] = results["sender_keys"][:keyLength]
                results["receiver_keys"] = results["receiver_keys"][:keyLength]
                results["sifted_keylength"] = keyLength
            report = {}
            report["application"] = results
            end_time = time.time()
            execution_time = end_time-start_time
            report = network_graph(network_topo, source_node_list, report)
            report["performance"]["execution_time"] = execution_time
            print(report)
            return report
        trials = trials-1

    return {"Error_Msg": "Couldn't generate required length.Retry Again"}

def test_e91():
    # network_config = {"nodes":[{"Name":"n1","Type":"service","noOfMemory":500,"memory":{"frequency":2000,"expiry":2000,"efficiency":1,"fidelity":0.93}},{"Name":"n2","Type":"end","noOfMemory":500,"memory":{"frequency":2000,"expiry":2000,"efficiency":1,"fidelity":0.93}}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.00001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":1000},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":1000}]}
    # network_config = {"nodes":[{"Name":"n1","Type":"end","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}},{"Name":"n2","Type":"service","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}},{"Name":"n3","Type":"service","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}},{"Name":"n4","Type":"end","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n2","n3"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n3","n4"],"Attenuation":0.0001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":0},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":0},{"Nodes":["n2","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n3"],"Delay":0,"Distance":0},{"Nodes":["n3","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n4"],"Delay":0,"Distance":0}]}
    network_config = {"nodes":[{"Name":"n1","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n2","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n3","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n4","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n2","n3"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n3","n4"],"Attenuation":0.0001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":0},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":0},{"Nodes":["n2","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n3"],"Delay":0,"Distance":0},{"Nodes":["n3","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n4"],"Delay":0,"Distance":0}]}
    sender = "n1"
    receiver = "n4"
    startTime = 1e12
    size = 6
    priority = 0
    targetFidelity = 0.95
    timeout = 1.2e12
    key_length = 2
    report = e91(network_config, sender, receiver, key_length)
    print(report)

# test_e91()

def e2e(network_config, sender, receiver, startTime, size, priority, targetFidelity, timeout):
    logger.info("End-to-End Bell Pair Distribution")
    print("E2E")
    # TODO: Integrate Network Graphs
    req_pairs = []
    start_time = time.time()
    print('network config', network_config)
    network_config_json, tl, network_topo = load_topology(network_config, "Qiskit")
    tm = network_topo.nodes[sender].transport_manager
    nm = network_topo.nodes[sender].network_manager
    logger.info('Creating request...')
    tm.request(receiver, float(startTime), int(size), 20e12,
               int(priority), float(targetFidelity), float(timeout))
    req_pairs.append((sender, receiver))
    # tl.stop_time=30e12
    tl.init()
    tl.run()

    results, source_node_list = get_res(network_topo, req_pairs)
    report = {}
    report["application"] = results
    end_time = time.time()
    execution_time = end_time-start_time
    
    report = network_graph(network_topo, source_node_list, report)
    report["performance"]["execution_time"] = float("{:.2f}".format(execution_time))
    # report["performance"]["transport"] = {
    #     "retrials": tm.transportprotocolmap[0].retry,
    # }
    # report["performance"]["network"]["retrials"] = nm
    print(report)
    return report
    # graph = network_topo.get_virtual_graph()

    """results={
        "parameter":network_config_json,
        "graph":graph,
        "results":results
    }"""
    return results

def test_e2e():
    # network_config = {"nodes":[{"Name":"n1","Type":"service","noOfMemory":500,"memory":{"frequency":2000,"expiry":2000,"efficiency":1,"fidelity":0.93}},{"Name":"n2","Type":"end","noOfMemory":500,"memory":{"frequency":2000,"expiry":2000,"efficiency":1,"fidelity":0.93}}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.00001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":1000},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":1000}]}
    # network_config = {"nodes":[{"Name":"n1","Type":"end","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}},{"Name":"n2","Type":"service","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}},{"Name":"n3","Type":"service","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}},{"Name":"n4","Type":"end","noOfMemory":500,"memory":{"frequency":80e6,"expiry":-1,"efficiency":1,"fidelity":0.93}}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n2","n3"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n3","n4"],"Attenuation":0.0001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":0},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":0},{"Nodes":["n2","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n3"],"Delay":0,"Distance":0},{"Nodes":["n3","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n4"],"Delay":0,"Distance":0}]}
    network_config = {"nodes":[{"Name":"n1","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n2","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n3","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n4","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n2","n3"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n3","n4"],"Attenuation":0.0001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":0},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":0},{"Nodes":["n2","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n3"],"Delay":0,"Distance":0},{"Nodes":["n3","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n4"],"Delay":0,"Distance":0}]}
    sender = "n1"
    receiver = "n2"
    startTime = 1e12
    size = 5
    priority = 0
    targetFidelity = 0.97
    timeout = 5e12
    report = e2e(network_config, sender, receiver, startTime, size, priority, targetFidelity, timeout)
    print(report)

# test_e2e()

def test_direct_transmission():
    network_config = {"nodes":[{"Name":"n1","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n2","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n3","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n4","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n2","n3"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n3","n4"],"Attenuation":0.0001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":0},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":0},{"Nodes":["n2","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n3"],"Delay":0,"Distance":0},{"Nodes":["n3","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n4"],"Delay":0,"Distance":0}]}
    src = "n1"
    dst = "n4"

    start_time = time.time()
    print('network config', network_config)
    network_config_json, tl, network_topo = load_topology(
        network_config, "Qiskit")
    node_s = network_topo.nodes[src]
    node_d = network_topo.nodes[dst]
    logger.info('Sending qubit...')
    # tl.stop_time=30e12
    node_s.send_qubit(dst, Photon('dummy_photon'))
    tl.init()
    tl.run()
    print(f'Buffer at destination node: {node_d.name}:{node_d.qubit_buffer}')
    print(f'Buffer at n1:{network_topo.nodes["n1"].qubit_buffer}')
    print(f'Buffer at n2:{network_topo.nodes["n2"].qubit_buffer}')
    print(f'Buffer at n3:{network_topo.nodes["n3"].qubit_buffer}')
    print(f'Buffer at n4:{network_topo.nodes["n4"].qubit_buffer}')

# test_direct_transmission()

def ghz(network_config, endnode1, endnode2, endnode3, middlenode, noise: Dict[str, List[float]] = {}):
    logger.info("End-to-End GHZ Generation")

    start_time = time.time()
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
    alice = network_topo.nodes[endnode1]
    bob = network_topo.nodes[endnode2]
    charlie = network_topo.nodes[endnode3]
    middlenode = network_topo.nodes[middlenode]
    ghz = GHZ()
    alice, bob, charlie, middlenode, source_node_list = ghz.roles(alice, bob, charlie, middlenode)
    tl.init()
    tl.run()
    results = ghz.run(alice, bob, charlie, middlenode, deepcopy(noise))
    results = {k: display_quantum_state(state) for k, state in results.items()}
    report = {}
    report["application"] = results
    end_time = time.time()
    execution_time = end_time-start_time
    report = network_graph(network_topo, source_node_list, report)
    report["performance"]["execution_time"] = execution_time
    print(report)
    return report


# def ip1(network_config, sender, receiver, message):
#     start_time = time.time()
#     network_config_json, tl, network_topo = load_topology(
#         network_config, "Qutip")
#     alice = network_topo.nodes[sender]
#     bob = network_topo.nodes[receiver]
#     ip1 = IP1()
#     alice, bob, source_node_list = ip1.roles(alice, bob, n=50)
#     tl.init()
#     tl.run()
#     results = ip1.run(alice, bob, message)
#     report = {}
#     report["application"] = results
#     end_time = time.time()
#     execution_time = end_time-start_time
#     report = network_graph(network_topo, source_node_list, report)
#     report["performance"]["execution_time"] = execution_time
#     print(report)
#     return report


# def ping_pong(network_config, sender, receiver, sequenceLength, message):
#     logger.info("PingPong QSDC")
#     start_time = time.time()
#     network_config_json, tl, network_topo = load_topology(
#         network_config, "Qutip")
#     if len(message) <= 9:
#         n = int(sequenceLength*len(message))
#         alice = network_topo.nodes[sender]
#         bob = network_topo.nodes[receiver]
#         pp = PingPong()
#         alice, bob, source_node_list = pp.roles(alice, bob, n)
#         tl.init()
#         tl.run()
#         pp.create_key_lists(alice, bob)
#         results = pp.run(sequenceLength, message)
#         report = {}
#         report["application"] = results
#         end_time = time.time()
#         execution_time = end_time-start_time
#         report = network_graph(network_topo, source_node_list, report)
#         report["performance"]["execution_time"] = execution_time
#         print(report)
#         return report
#     else:
#         print("message should be less than or equal to 9")
#         return None


def qsdc1(network_config, sender, receiver, sequenceLength, key, noise: Dict[str, List[float]] = {}):
    logger.info("Seminal QSDC")
    start_time = time.time()
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
    if (len(key) % 2 == 0):
        n = int(sequenceLength*len(key))
        alice = network_topo.nodes[sender]
        bob = network_topo.nodes[receiver]
        print('alice bob', alice, bob, n)
        qsdc1 = QSDC1()
        alice, bob, source_node_list = qsdc1.roles(alice, bob, n)
        print("alice,bob,source_node_list", alice, bob, source_node_list)
        tl.init()
        tl.run()
        print('init and run', network_config_json)
        results = qsdc1.run(alice, bob, sequenceLength, key, deepcopy(noise))
        report = {}
        report["application"] = results
        end_time = time.time()
        execution_time = end_time-start_time
        report = network_graph(network_topo, source_node_list, report)
        report["performance"]["execution_time"] = execution_time
        print(report)
        return report
    else:
        print("key should have even no of digits")
        return None


def teleportation(network_config, sender, receiver, amplitude1, amplitude2, noise: Dict[str, List[float]] = {}):
    print("Quantum Teleportation...")
    logger.info("Quantum Teleportation")
    start_time = time.time()
    # TODO: Integrate Network Graphs
    print("teleportation running")
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
    print(network_config_json)

    alice = network_topo.nodes[sender]
    bob = network_topo.nodes[receiver]
    tel = Teleportation()
    alice, bob, source_node_list = tel.roles(alice, bob)
    print('source node', source_node_list)
    tl.init()
    tl.run()
    results = tel.run(alice, bob, amplitude1, amplitude2, deepcopy(noise))
    report = {}
    results["alice_bob_entanglement"] = display_quantum_state(results["alice_bob_entanglement"])
    results["random_qubit"] = display_quantum_state(results["random_qubit"])
    results["bob_initial_state"] = display_quantum_state(results["bob_initial_state"])
    results["bob_final_state"] = display_quantum_state(results["bob_final_state"])
    report["application"] = results

    end_time = time.time()
    execution_time = end_time-start_time
    report = network_graph(network_topo, source_node_list, report)
    report["performance"]["execution_time"] = execution_time
    print(report)
    return report

def qsdc_teleportation(topology: Dict, sender: str, receiver: str, message: str, attack: Optional[str] = None, noise: Dict[str, List[float]] = {}):
    print("QSDC_TELEPORTATION\n")
    print(f"topology map: {topology}\n")
    print(f"sender: {sender}, receiver: {receiver}, message: {message}, attack: {attack}\n")
    start_time = time.time()
    network = Network(topology=topology, messages={(sender, receiver): message}, noise = deepcopy(noise))
    network.teleport(None)
    if attack in ["DoS", "EM", "IR"]:
        from qntsim.communication.attack import ATTACK_TYPE, Attack
        Attack.implement(network, None, ATTACK_TYPE[attack].value)
    network.measure(None)
    received_messages = network._decode(None)
    print(f"strings in network: {network._strings}\n")
    print(f"messages received after decode: {received_messages}\n")
    from qntsim.communication.error_analyzer import ErrorAnalyzer
    print(f"returns from ErrorAnalyzer: {ErrorAnalyzer._analyse(network)}\n")
    _, _, avg_err, _, _, _ = ErrorAnalyzer._analyse(network)
    execution_time: float = time.time() - start_time
    response: Dict[str, Any] = {}
    response["input_message"] = message
    response["output_message"] = list(received_messages.values())[0]
    response["attack"] = attack
    response["error"] = avg_err
    print(f"generated response: {response}\n")
    json_response = network_graph(network._net_topo, [sender], {})
    json_response["performance"]["execution_time"] = execution_time
    json_response["application"] = response
    print(f"final json_response: {json_response}\n")
    return json_response

def single_photon_qd(network_config, sender, receiver, message1, message2, attack):
    logger.info("Single Photon QD")
    start_time = time.time()
    print('sender, receiver, message1, message2',
          sender, receiver, message1, message2, attack)
    messages = {(sender, receiver): message1, (receiver, sender): message2}
    network_config_json, tl, network_topo = load_topology(
        network_config, "Qutip")
    tl.init()
    # topo_json = json_topo(network_config_json)
    # print('network config json', network_topo)
    # with open("topology.json", "w") as outfile:
    #     json.dump(topo_json, outfile)
    # messages = {(1, 2):'hello', (2, 1):'world'}
    # attack=None
    topology = '/code/web/configs/singlenode.json'
    print('topology', topology)
    protocol = ProtocolPipeline(name='qd_sp', messages_list=[messages], attack=attack)
    protocol(topology=topology)

    print("protocol.recv_msgs_list", protocol.recv_msgs_list[-1])
    print("mean(protocol.mean_list)", mean(protocol.mean_list))
    res = {}
    result = list(protocol.recv_msgs_list[-1].values())

    res["input_message1"] = message1
    res["input_message2"] = message2
    res["output_message1"] = result[0]
    res["output_message2"] = result[1]
    res["attack"] = attack
    res["error"] = protocol.mean_list[-1]
    report = {}
    end_time = time.time()
    execution_time = end_time-start_time
    source_node_list = [sender]

    report = network_graph(network_topo, source_node_list, report)
    report["performance"]["execution_time"] = execution_time

    # report["performance"]["execution_time"] = execution_time
    report["application"] = res
    protocol = None
    return report
    # return protocol.recv_msgs_list, mean(protocol.mean_list)

    # topology = json_topo(network_config)
    # with open('network_topo.json','w') as fp:
    #     json.dump(topology,fp, indent=4)
    # topo = '/code/web/singlenode.json'
    # message = [message1,message2]
    # print('message', message)
    # protocol = ProtocolPipeline(platform='qntsim',
    #                 messages_list=[message],
    #                 topology=topo,
    #                 backend='Qutip',
    #                 attack=attack)

    # # This should be on results page
    # print('Received messages:', protocol.recv_msgs[0][1],protocol.recv_msgs[0].keys())
    # print('Error:', mean(protocol.mean_list))
    # error = mean(protocol.mean_list)
    # res ={}
    # res["input_message1"] = message1
    # res["input_message2"] = message2
    # res["output_message1"] = protocol.recv_msgs[0][1]
    # res["output_message2"] = protocol.recv_msgs[0][2]
    # res["attack"] = attack
    # res["error"] = error
    # report = {}
    # report["application"] = res

    # return report


def random_encode_photons(network: Network):
    print('inside random encode')
    node = network._net_topo.nodes['n1']
    manager = network.manager
    basis = {}
    for info in node.resource_manager.memory_manager:
        if info.state == 'RAW':
            key = info.memory.qstate_key
            base = randint(4)
            basis.update({key: base})
            q, r = divmod(base, 2)
            qtc = QutipCircuit(1)
            if r:
                qtc.x(0)
            if q:
                qtc.h(0)
            manager.run_circuit(qtc, [key])
        if info.index == 2*(network.size+75):
            break

    print('output', network, basis)
    return network, basis


def authenticate_party(network: Network):
    manager = network.manager
    node = network._net_topo.nodes['n1']
    keys = [info.memory.qstate_key for info in node.resource_manager.memory_manager[:2*network.size+150]]
    keys1 = keys[network.size-25:network.size]
    keys1.extend(keys[2*network.size:2*network.size+75])
    shuffle(keys1)
    keys2 = keys[2*network.size-25:2*network.size]
    keys2.extend(keys[2*network.size+75:])
    shuffle(keys2)
    # print(keys1)
    # print(keys2)
    all_keys = []
    outputs = []
    for keys in zip(keys1, keys2):
        all_keys.append(keys)
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.h(0)
        qtc.measure(0)
        qtc.measure(1)
        outputs.append(manager.run_circuit(qtc, list(keys)))
    err, counter = 0, 0
    for output in outputs:
        (key1, key2) = tuple(output.keys())
        base1 = basis.get(key1)
        base2 = basis.get(key2)
        out1 = output.get(key1)
        out2 = output.get(key2)
        if base1 != None != base2 and base1//2 == base2//2:
            counter += 1
            if (out1 if base1//2 else out2) != (base1 % 2) ^ (base2 % 2):
                err += 1
    print(err/counter*100)

    return network, err/counter*100


def swap_entanglement(network: Network):
    node = network._net_topo.nodes['n1']
    manager = network.manager
    e_keys = []
    for info0, info1 in zip(node.resource_manager.memory_manager[:network.size-25],
                            node.resource_manager.memory_manager[network.size:2*network.size-25]):
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.h(0)
        qtc.measure(0)
        qtc.measure(1)
        keys = [info0.memory.qstate_key, info1.memory.qstate_key]
        print(keys)
        e_key = [k for key in keys for k in manager.get(key).keys if k != key]
        output = manager.run_circuit(qtc, keys)
        c1, c2 = True, False
        for e_k, value in zip(e_key, output.values()):
            qtc = QutipCircuit(1)
            if c1 and value:
                qtc.x(0)
                c1, c2 = False, True
            elif c2 and value:
                qtc.z(0)
                c1, c2 = True, False
            manager.run_circuit(qtc, [e_k])
        e_keys.append(e_key)

    return e_keys


def mdi_qsdc(network_config, sender, receiver, message, attack):
    logger.info("MDI QSDC with user Authentication")
    # network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    # # print('network config json', network_config_json)
    # mdi_qsdc = MdiQSDC()
    # mdi_qsdc.random_encode_photons()
    # # print("network Config", network_config)
    # topo = json_topo(network_config)
    # print("topo",topo)
    # results = mdi_qsdc.run(topo,message,attack)
    # print('results',results)
    topology = json_topo(network_config)
    print('pwd', os.getcwd())
    with open('network_topo.json', 'w') as fp:
        json.dump(topology, fp, indent=4)
    # f = open('/code/web/network_topo.json')
    topo = '/code/web/network_topo.json'
    # topo = code/backend/web/network_topo.json
    print("topo", topo)
    network = Network(topology=topo,
                      messages=[message],
                      label='00',
                      size=lambda x: len(x[0])+100)

    print('network', network)
    network, basis = random_encode_photons(network=network)
    # network, err_prct = authenticate_party(network=network)
    network.dump('n1')
    print('network', network, basis)


# def ip2(network_config, alice_attrs, bob_id, threshold, num_decoy):
#     report = {}
#     start_time = time.time()
#     # print("input_messages,ids,num_check_bits,num_decoy",input_messages,ids,num_check_bits,num_decoy)
#     network_config_json, tl, network_topo = load_topology(
#         network_config, "Qutip")
#     tl.init()
#     topo_json = json_topo(network_config_json)
#     print('network config json', network_topo)
#     with open("topology.json", "w") as outfile:
#         json.dump(topo_json, outfile)
#     topology = '/code/web/topology.json'
#     sender = alice_attrs["sender"]
#     receiver = alice_attrs["receiver"]
#     input_message = alice_attrs["message"]
#     print('sender, receievre', sender, receiver)
#     # network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
#     # tl.init()
#     # topo_json = json_topo(network_config_json)
#     # print('network config json', network_topo)
#     # with open("topology.json", "w") as outfile:
#     #     json.dump(topo_json, outfile)
#     alice_attrs.update({'message': {(sender, receiver): input_message},
#                    'id': '1011',
#                    'check_bits': 4})
#     bob_id = '0111'
#     num_decoy_photons = 4
#     threshold = 0.2  # error threshold
#     attack = (None, None)
#     # topology = '/code/web/configs/2n_linear.json'
#     network, recv_msgs, err_tup = ip2_run(topology=network_config,
#                                           alice_attrs=alice_attrs,
#                                           bob_id=bob_id,
#                                           num_decoy_photons=num_decoy_photons,
#                                           threshold=threshold,
#                                           attack=attack)
#     # results=ip2_run(topology,input_messages,ids,num_check_bits,num_decoy,attack)
#     # report["application"]=results
#     # return report
#     # print('results', results[1][0])
#     res = {}
#     res["input_message"] = input_message
#     res["alice_id"] = alice_attrs["id"]
#     res["alice_check_bits"] = alice_attrs["check_bits"]
#     res["bob_id"] = bob_id
#     res["threshold"] = threshold
#     res["num_decoy"] = num_decoy
#     res["output_msg"] = recv_msgs
#     res["avg_error"] = err_tup[0]
#     res["standard_deviation"] = err_tup[1]
#     res["info_leaked"] = err_tup[2]
#     res["msg_fidelity"] = err_tup[3]
#     # report = {}
#     report["application"] = res
#     end_time = time.time()
#     report = network_graph(network._net_topo, [sender], report)
#     execution_time = end_time-start_time
#     report["performance"]["execution_time"] = execution_time
#     # execution_time = end_time-start_time
#     # report["performance"]["execution_time"] = execution_time
#     print('report', report)
#     return report
