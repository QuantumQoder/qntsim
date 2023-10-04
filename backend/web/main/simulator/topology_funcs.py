"""
This module contains pre-built protocols displayed on the UI, as well as, helper functions.
Specifically contains:
    eve_e91
    e91
    e2e
    ghz
    ip1
    qsdc1
    teleportation
    qsdc_teleportation
"""

import importlib
import logging
import os
import time
from copy import deepcopy
from random import randint, shuffle
from tokenize import String
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
# from qntsim.communication.interface import Interface
from qntsim.communication.network import Network
from qntsim.communication.protocol import ProtocolPipeline
from qntsim.components.photon import Photon
from qntsim.kernel.circuit import Circuit
from qntsim.topology.topology import Topology
from qntsim.utils import log
from tabulate import tabulate

from .app.e2e import *
from .app.e91 import *
from .app.ghz import *
from .app.ip1 import *
from .app.ping_pong import ping_pong
from .app.qsdc1 import *
from .app.qsdc_teleportation import *
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

logger = log.logger

print("topology_funcs.py")
print(logger.handlers)

def eve_e91(network_config, sender, receiver, keyLength):
    if keyLength < 1 or keyLength > 30: raise Exception("keyLength must be within 0 and 30 .Retry Again")
    start_time = time.time()
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
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
    else: Exception("Couldn't generate required length.Retry Again")
    end_time = time.time()
    execution_time = end_time-start_time
    report = determine_performance(network_topo, source_node_list, {"application": results})
    report["performance"]["execution_time"] = execution_time
    print(report)
    return report

def e91(network_config, sender, receiver, keyLength, noise: Dict[str, List[float]] = {}):
    logger.info("E91 Quantum Key Distribution")
    print('In e91 network config', network_config)
    if keyLength < 1 or keyLength > 30: raise Exception("keyLength must be within 0 and 30 .Retry Again")
    start_time = time.time()
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
    print('network topo', network_topo)
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
    else: raise Exception("Couldn't generate required length.Retry Again")
    end_time = time.time()
    execution_time = end_time-start_time
    report = determine_performance(network_topo, source_node_list, {"application": results})
    report["performance"]["execution_time"] = execution_time
    print(report)
    return report

def e2e(network_config, sender, receiver, startTime, size, priority, targetFidelity, timeout):
    logger.info("End-to-End Bell Pair Distribution")
    print("E2E")
    # TODO: Integrate Network Graphs
    req_pairs = []
    print('network config', network_config)
    network_config_json, tl, network_topo = load_topology(network_config, "Qiskit")
    tm = network_topo.nodes[sender].transport_manager
    nm = network_topo.nodes[sender].network_manager
    logger.info('Creating request...')
    start_time = time.time()
    tm.request(receiver, float(startTime), int(size), 20e12,
               int(priority), float(targetFidelity), float(timeout))
    req_pairs.append((sender, receiver))
    tl.init()
    tl.run()
    end_time = time.time()
    execution_time = end_time-start_time
    results, source_node_list = get_res(network_topo, req_pairs)
    report = determine_performance(network_topo, source_node_list, {"application": results})
    report["performance"]["execution_time"] = float("{:.2f}".format(execution_time))
    print(report)
    return report

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
    end_time = time.time()
    execution_time = end_time-start_time
    results = {k: display_quantum_state(state) for k, state in results.items()}
    report = determine_performance(network_topo, source_node_list, {"application": results})
    report["performance"]["execution_time"] = execution_time
    print(report)
    return report

def ip1(network_config, sender, receiver, message):
    start_time = time.time()
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
    alice = network_topo.nodes[sender]
    bob = network_topo.nodes[receiver]
    ip1 = IP1()
    alice, bob, source_node_list = ip1.roles(alice, bob, n=50)
    tl.init()
    tl.run()
    results = ip1.run(alice, bob, message)
    end_time = time.time()
    execution_time = end_time-start_time
    report = determine_performance(network_topo, source_node_list, {"application": results})
    report["performance"]["execution_time"] = execution_time
    print(report)
    return report

def qsdc1(network_config, sender, receiver, sequenceLength, key, noise: Dict[str, List[float]] = {}):
    logger.info("Seminal QSDC")
    start_time = time.time()
    network_config_json, tl, network_topo = load_topology(network_config, "Qutip")
    if len(key) != 0: raise Exception("key length must be even.")
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
    end_time = time.time()
    execution_time = end_time-start_time
    report = determine_performance(network_topo, source_node_list, {"application": results})
    report["performance"]["execution_time"] = execution_time
    print(report)
    return report

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
    end_time = time.time()
    execution_time = end_time-start_time
    results["alice_bob_entanglement"] = display_quantum_state(results["alice_bob_entanglement"])
    results["random_qubit"] = display_quantum_state(results["random_qubit"])
    results["bob_initial_state"] = display_quantum_state(results["bob_initial_state"])
    results["bob_final_state"] = display_quantum_state(results["bob_final_state"])
    report = determine_performance(network_topo, source_node_list, {"application": results})
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
    response: Dict[str, Any] = {"input_message": message,
                                "output_message": list(received_messages.values())[0],
                                "attack": attack,
                                "error": avg_err}
    print(f"generated response: {response}\n")
    json_response = determine_performance(network._net_topo, [sender], {"application": response})
    json_response["performance"]["execution_time"] = execution_time
    print(f"final json_response: {json_response}\n")
    return json_response

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

def test_direct_transmission():
    network_config = {"nodes":[{"Name":"n1","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n2","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n3","Type":"service","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99},{"Name":"n4","Type":"end","noOfMemory":500,"memory":{"frequency":80000000,"expiry":-1,"efficiency":1,"fidelity":0.93},"swap_success_rate":1,"swap_degradation":0.99}],"quantum_connections":[{"Nodes":["n1","n2"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n2","n3"],"Attenuation":0.0001,"Distance":70},{"Nodes":["n3","n4"],"Attenuation":0.0001,"Distance":70}],"classical_connections":[{"Nodes":["n1","n1"],"Delay":0,"Distance":0},{"Nodes":["n1","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n1","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n2"],"Delay":0,"Distance":0},{"Nodes":["n2","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n2","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n3","n3"],"Delay":0,"Distance":0},{"Nodes":["n3","n4"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n1"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n2"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n3"],"Delay":1000000000,"Distance":1000},{"Nodes":["n4","n4"],"Delay":0,"Distance":0}]}
    src = "n1"
    dst = "n4"
    start_time = time.time()
    print('network config', network_config)
    network_config_json, tl, network_topo = load_topology(network_config, "Qiskit")
    node_s = network_topo.nodes[src]
    node_d = network_topo.nodes[dst]
    logger.info('Sending qubit...')
    node_s.send_qubit(dst, Photon('dummy_photon'))
    tl.init()
    tl.run()
    print(f'Buffer at destination node: {node_d.name}:{node_d.qubit_buffer}')
    print(f'Buffer at n1:{network_topo.nodes["n1"].qubit_buffer}')
    print(f'Buffer at n2:{network_topo.nodes["n2"].qubit_buffer}')
    print(f'Buffer at n3:{network_topo.nodes["n3"].qubit_buffer}')
    print(f'Buffer at n4:{network_topo.nodes["n4"].qubit_buffer}')

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

if __name__ == "__main__":
    test_e91()
    test_e2e()
    test_direct_transmission()