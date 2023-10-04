import logging
import string
from statistics import mean
from typing import Any, Dict, List, TypeAlias, Union, overload

import numpy as np
from qntsim.kernel.timeline import Timeline
from qntsim.topology.topology import Topology
from qntsim.utils import log

from .constants import *

# Do Not Remove the following commented imports - this is for local testing purpose
# from constants import *

logger = logging.getLogger("main." + "helpers")

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

    network_config_json, tl, network_topo = load_topology(network_config_json, "Qiskit")
    print(f'Making graph')
    graph = network_topo.get_virtual_graph()
    print(network_topo)
    return graph

@overload
def determine_performance(topology: Topology, nodes: List[str]) -> Dict[str, float]: ...

@overload
def determine_performance(topology: Topology, nodes: List[str], pre_response: Dict[str, Any]) -> Dict[str, Union[Any, Dict[str, float]]]: ...

def determine_performance(topology: Topology, nodes: List[str], pre_response: Dict[str, Any] = {}) -> Union[Dict[str, Union[Any, Dict[str, float]]], Dict[str, float]]:
    latency: float = max([max([mem_info.entangle_time
                               for mem_info in topology.nodes[node].resource_manager.memory_manager
                               if mem_info.index in topology.nodes[node].resource_manager.reservation_id_to_memory_map.get(req_id) and mem_info.state == "ENTANGLED"]) - request.starttime
                          for node in nodes
                          for req_id, request in topology.nodes[node].network_manager.requests.items()
                          if not request.isvirtual]) * 1e-12
    fidelity: float = min([mem_info.fidelity
                           for node in nodes
                           for req_id, request in topology.nodes[node].network_manager.requests.items()
                           for mem_info in topology.nodes[node].resource_manager.memory_manager
                           if not request.isvirtual and mem_info.index in topology.nodes[node].resource_manager.reservation_id_to_memory_map.get(req_id) and mem_info.state == "ENTANGLED"])
    throughput: float = mean([1 if request.status == "APPROVED" else 0
                              for node in nodes
                              for req_id, request in topology.nodes[node].network_manager.requests.items()
                              if req_id in topology.nodes[node].network_manager.networkmap and not request.isvirtual]) * 100
    performance: Dict[str, float] = {"latency": latency,
                                     "fidelity": fidelity,
                                     "throughput": throughput}
    if pre_response:
        pre_response.update(performance = performance)
        return pre_response
    return performance


def load_topology(network_config_json, backend):
    
    """
        Creates the network with nodes, quantum connections and 
        updates their respective components with the parameters specified in json
    """
    Timeline.DLCZ=False
    Timeline.bk=True
    print(f'Loading Topology: {network_config_json}')
    
    tl = Timeline(20e12,backend)
    logger.info("Timeline initiated with bk protocol")

    #Create the topology
    network_topo = Topology("network_topo", tl)
    network_topo.load_config_json(network_config_json)

    return network_config_json,tl,network_topo

def get_entanglement_data(network_topo, src, dst):
    success_entx_src, success_entx_dst = 0, 0
    for mem_info in network_topo.nodes[src].resource_manager.memory_manager:
        if mem_info.state == 'ENTANGLED' and mem_info.remote_node == dst:
            success_entx_src += 1

    for mem_info in network_topo.nodes[dst].resource_manager.memory_manager:
        if mem_info.state == 'ENTANGLED' and mem_info.remote_node == src:
            success_entx_dst += 1

    return min(success_entx_src, success_entx_dst)


def get_service_node(nodes):
    
    service_node = []
    for node in nodes:
        if node.get("Type") == "service":
            service_node.append(node.get("Name"))
    
    return service_node
            
    
def get_end_node(nodes,qconnections):
    
    
    service_node = get_service_node(nodes)
    end_node = {}
    for conns in qconnections:
        nodes = conns.get("Nodes")
        if bool(set(service_node) & set(nodes)):
            end_node[nodes[0]] = nodes[1]
    
    
    return end_node


def get_qconnections(quantum_connections):
    
    qconnections = []
    print('quantun conn',quantum_connections)
    for connections in quantum_connections:
        # for nodes in connections.get("Nodes"):
        conn = {}
        print('connections', connections,connections.get("Nodes")[0])
        conn["node1"] = connections.get("Nodes")[0]
        conn["node2"] = connections.get("Nodes")[1]
        conn["attenuation"] = connections.get("Attenuation")
        conn["distance"] = connections.get("Distance")
        qconnections.append(conn)
    
    print('qconnectios', qconnections)
    return qconnections
            
def to_matrix(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]
                     
def get_cconnections(classical_connections):
    
    cchannels_table ={}
    cchannels_table["type"] ="RT"
    nodes = []
    for conn in classical_connections:
        for node in conn.get("Nodes"):
            # print('inside node', node)
            nodes.append(node)
            # for nod in node:
            #     nodes.append(nod)
            
    # print('nodes',nodes)
    nodes = list(set(nodes))
    # print('nodes',nodes)
    cchannels_table["labels"] = nodes
    table = []
    for node1 in nodes:
        for node2 in nodes:
            if node1 == node2:
                table.append(0)
            else:
                table.append(1000000000)
    
    cchannels_table["table"] = to_matrix(table, len(nodes))
    
    return cchannels_table
 
            
def json_topo(topology):
    
    nodes = topology.get("nodes")
    quantum_connections = topology.get("quantum_connections")
    classical_connections = topology.get("classical_connections")
    
    network_json = {}
    service_node = get_service_node(nodes)
    end_node = get_end_node(nodes,quantum_connections)
    
    network_json["service_node"] = service_node
    network_json["end_node"] = end_node
    network_json["qconnections"] = get_qconnections(quantum_connections)
    network_json["cchannels_table"] = get_cconnections(classical_connections)
    
    return network_json
    
    