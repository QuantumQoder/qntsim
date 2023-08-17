from typing import Any, Callable, Dict, List, Optional, Self, Union
import deepcopy
import json5
import numpy as np

from backend.src.core.kernel.timeline import Timeline
from backend.src.core.topology.node import Node
from backend.src.layers.physical_layer.components.photon import Photon

from ....core.topology.node import BSMNode, EndNode, ServiceNode
from ....utils import encoding
from ...physical_layer.components.optical_channel import QuantumChannel
from ...physical_layer.components.waveplates import QuarterWaveplate, Waveplate
from ..communication import Communication, Network
from .attack import Attack

class Attacker(ServiceNode, QuantumChannel):
    """A class representing an attacker node in a quantum communication network."""

    def __init__(self, name: str, timeline: Timeline, memo_size: Optional[int], attack: Optional[Union[Callable, str]]):
        """
        Initialize an Attacker node.

        Args:
            name (str): Name of the attacker node.
            timeline (Timeline): Timeline of the quantum communication network.
            memo_size (int, optional): Size of the memory for the attacker node.
            attack (Callable or str, optional): The attack strategy to be used.
        """
        self.__attack = attack or "DS"
        super().__init__(name, timeline, memo_size or 500)

    def attack(self, qubit: Photon) -> Optional[Photon]:
        """
        Apply an attack on the input qubit.

        Args:
            qubit (Photon): The input qubit.

        Returns:
            Optional[Photon]: The modified qubit after applying the attack.
        """
        encoder = getattr(encoding, qubit.encoding_type)
        bases = encoder.get("bases")
        match self.__attack:
            case "DS":
                qubit.random_noise()
            case "EM":
                photon = deepcopy(qubit)
                photon.set_state(state=bases[0][0]) #attacker's photon
                qubit.entangle(photon=photon)
                Photon.measure(basis=bases[0], photon=photon)
            case "IR":
                photon = deepcopy(qubit)
                photon.set_state(state=(basis := bases[np.random.randint(2)])[Photon.measure(basis=basis, photon=qubit)]) #attacker's photon
                return photon
            case Callable():
                return self.__attack(qubit)

    @classmethod
    def modify_topology(cls, topology:Union[str, Dict[str, Dict[str, Any]]], insert_locations:Optional[List[List[str]]], attack:Optional[Union[Callable, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Inserting attacker in the topology.

        """
        topology = json5.load(open(topology)) if isinstance(topology, str) else topology
        return (cls._modify_new_topology if "nodes" in topology else cls._modify_old_topology)(topology=topology, insert_locations=insert_locations, attack=attack)

    @staticmethod
    def _modify_new_topology(topology:Dict[str, List[Dict[str, Any]]], insert_locations:List[List[str]], attack:Optional[Union[Callable, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Inserting attacker in the topology.
        
        """
        for i in range(len(insert_locations)):
            topology.get("nodes").append({"name":f"attacker{i+1}", "Type":"attacker", "memo_size":500, "attack":attack})
        quantum_connections = topology.get("quantum_connections", [])
        for insert_location in insert_locations:
            for quantum_connection in quantum_connections:
                pass
            quantum_connections.append({"Nodes":[quantum_connection.get("Nodes")[0], insert_location[1]],
                                        "Attenuation":quantum_connection.get("Attenuation", 1e-5),
                                        "Distance":quantum_connection.get("Distance", 70)/2})
            quantum_connections.append({"Nodes":[insert_location[0], insert_location[1]],
                                        "Attenuation":quantum_connection.get("Attenuation", 1e-5),
                                        "Distance":quantum_connection.get("Distance", 70)/2})
            quantum_connections.append({"Nodes":[insert_location[0], quantum_connection.get("Nodes")[1]],
                                        "Attenuation":quantum_connection.get("Attenuation", 1e-5),
                                        "Distance":quantum_connection.get("Distance", 70)/2})
        topology.update(quantum_connections=quantum_connections)
        return topology

    @staticmethod
    def _modify_old_topology(topology:Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]], insert_locations:List[List[str]]) -> Dict[str, Dict[str, Any]]:
        nodes = [{"name":topology.get(entity).pop("name"),
                  "Type":entity[:-5],
                  "memo_size":topology.get(entity).pop("memo_size", 500),
                  **topology.get(entity)} for entity in topology if "node" in entity]
        quantum_connections = [{"Nodes":[topology.get(entity).pop("node1"), topology.get(entity).pop("node2")],
                                "Attenuation":topology.get(entity).pop("attenuation", 1e-5),
                                "Distance":topology.get(entity).pop("distance"),
                                **topology.get("entity")} for entity in topology if entity in ["qconnections", "qchannels"]]
        classical_connections = [{"Nodes":[topology.get(entity).pop("node1"), topology.get(entity).pop("node2")],
                                  "Attenuation":topology.get(entity).pop("attenuation", 1e-5),
                                  "Distance":topology.get(entity).pop("distance"),
                                  **topology.get("entity")} for entity in topology if entity in ["cconnections", "cchannels"]]
        cchannels_table = topology.get("cchannels_table")
        if cchannels_table:
            nodes = cchannels_table.get("labels", [])
            table = cchannels_table.get("table", [[]])
            for i in range(len(table)):
                for j in range(len(table[i])):
                    classical_connection = {"Nodes":[nodes[i], nodes[j]],
                                            "Attenuation":1e-5,
                                            "Distance":table[i][j]}
                    if classical_connection not in classical_connections: 
                        classical_connections.append(classical_connection)
        topology.clear()
        topology.update(nodes=nodes, quantum_connections=quantum_connections, classical_connections=classical_connections)
        return __class__._modify_new_topology(topology=topology, insert_locations=insert_locations)

    @classmethod
    def load_modified_topology(cls, comm_net:Communication, topology:Union[str, Dict[str, List[Dict[str, Any]]]], insert_locations:Optional[List[List[str]]], attack:Optional[Union[Callable, str]]) -> None:
        """
        Attacker modifies the topology by inserting a node.
        
        """
        
        for nodes in comm_net.messages:
            src_node = nodes[0]
            dst_nodes = nodes[1:]
            for dst_node in dst_nodes:
                route = comm_net.get_shortest_route(src_node=src_node, dst_node=dst_node)
                for insert_location in insert_locations:
                    if not set(insert_location).issubset(set(route)):
                        insert_locations.append([])
        topology = cls.modify_topology(topology=topology, insert_locations=insert_locations, attack=attack)
        for node in topology.get("nodes", []):
            node_type = node.pop("Type", "end")
            params = {"timeline":comm_net, **node}
            match node_type:
                case "service": node_cls = ServiceNode
                case "end": node_cls = EndNode
                case "attacker": node_cls = __class__
            node_obj = node_cls(**params)
            for arg, val in node.get("memory", {}).items():
                node_obj.memory_array.update_memory_params(arg, val)
            for arg, val in node.get("lightSource", {}).items():
                setattr(node_obj.lightsource, arg, val)
            node_obj.network_manager.set_swap_success(es_swap_success=node.get("swap_success_rate", 1))
            node_obj.network_manager.set_swap_degradation(es_swap_degradation=node.get("swap_degradation", 0.99))
        for qunatum_connection in topology.get("quantum_connections", {}):
            comm_net.add_quantum_connection(node1=qunatum_connection.get("Nodes")[0], node2=qunatum_connection.get("Nodes")[1], **qunatum_connection)
        for classical_connection in topology.get("classical_connections", {}):
            comm_net.add_classical_connection(node1=classical_connection.get("Nodes")[0], node2=classical_connection.get("Nodes")[1], **classical_connection)
        all_pair_dist, graph = comm_net.all_pair_shortest_dist()
        comm_net.nx_graph = graph
        for node in comm_net.nodes.values():
            if type(node) == BSMNode:
                for attr, val in topology.get("detector", {}):
                    setattr(node.bsm, attr, val)
                continue
            node.all_pair_shortest_dist = all_pair_dist
            node.nx_graph = comm_net.nx_graph
            node.delay_graph = comm_net.cc_delay_graph
            node.neighbors = list(graph.neighbors(node.name))
        for quantum_connection in topology.get("quantum_connections"):
            node0 = next(filter(lambda node: node.name == quantum_connection.get("Nodes")[0], comm_net.nodes.values()), None)
            node1 = next(filter(lambda node: node.name == quantum_connection.get("Nodes")[1], comm_net.nodes.values()), None)
            if node0: setattr(node0, "end_node" if type(node1) == EndNode else "service_node", node1)
            if node1: setattr(node1, "end_node" if type(node0) == EndNode else "service_node", node0)

