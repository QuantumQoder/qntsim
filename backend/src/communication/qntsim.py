import cmath
import math
import time
from collections import OrderedDict
from copy import deepcopy
from functools import partial
from types import NoneType
from typing import (TYPE_CHECKING, Any, Callable, Dict, Iterator, List,
                    Literal, Optional, Tuple, TypeAlias, Union, overload)

import numpy as np
from networkx import Graph
from pandas import DataFrame

from ..components import Photon, Waveplate
from ..kernel import Circuit, Timeline
from ..log_functions import log_object, log_object_instantiation
from ..topology import Topology
from ..types import Types
from ..utils import encoding, log
from .analyzer_circuits import bell_state_analyzer
from .utils import to_binary, to_characters

if TYPE_CHECKING:
    from ..topology import EndNode, ServiceNode
    from ..topology.node import Node

class QNtSim(Timeline, Topology):
    __formalism_type:TypeAlias = Literal["ket_vector", "density_matrix"],
    _flow: List[Tuple[Callable[..., NoneType], Tuple[Any]]] = []

    def __init__(self,
                 topology: Types.topology,
                 message_packets: Types.messages,
                 /,
                 name: Optional[str] = "",
                 backend: Types.backend = "qutip",
                 stop_time: float = 10e12,
                 end_time: float = 5e12,
                 timeout: float = 1e12,
                 target_fidelity: float = 1.0,
                 ent_gen_protocol: Literal["BK", "DLCZ"] = "BK",
                 **kwds) -> None:
        match ent_gen_protocol:
            case "DLCZ": Timeline.DLCZ = True
            case "BK": Timeline.BK = True

        # Load the timeline and the topology and run it once to handshake between nodes and initiate entities
        Timeline.__init__(self=self, stop_time=stop_time, backend=backend)
        Topology.__init__(self=self, name=name, timeline=self)
        (self.load_config if isinstance(topology, str) else self.load_config_json)(topology)
        self.init()
        self.run()
        self.message_packets = message_packets
        self.binary_packets = to_binary(message_packets)

        # For each packet, the entanglements and the photons are generated
        for binary_packet in self.binary_packets:
            medium: Literal["photon", "entanglement"] = binary_packet.get("medium", "entanglement")
            size: int = self.__determine_size(binary_packet)
            if medium == "photon":
                self.initialize_photons(binary_packet, size)
            elif medium == "entanglement":
                for sender, binary_message in binary_packet.items():
                    self.request_entanglements(sender, binary_message.get("receiver"), size, end_time, target_fidelity, timeout)

        # Set any extra parameter passed to the object as an attribute of the object
        self.setattrs(**kwds)

    def __determine_size(packet: Dict[str, Any]) -> int:
        size: Optional[Union[int, Callable[[int], int]]] = packet.pop("size", None)
        if isinstance(size, int): return size
        for package in packet.values():
            if isinstance(package, dict) and "message" in package:
                return (size if callable(size) else len)(package.get("message", ""))

    def initialize_photons(self, binary_packet, demand_size: int = 1, encoding_type: Types.encoding = "polarization") -> None:
        binary_packet = deepcopy(binary_packet)
        binary_packet.pop("medium")
        if (num_photons := self.count_media(*binary_packet, "photon")) < demand_size:
            encoder: Dict[str, Union[str, List[Tuple[complex]]]] = getattr(encoding, encoding_type)
            self.__quantum_states: Dict[int, List[Tuple[complex]]] = encoder.get("bases")
            photons: List["Photon"] = self.photons.get(tuple(binary_packet), [])
            photons.extend([Photon(f"{i}", encoding_type=encoding_type, quantum_state=self.__quantum_states[i // 2][i % 2]) for i in np.random.randint(4, size = demand_size - num_photons)])
            self.photons.update({tuple(binary_packet): photons})
            self.initialize_photons(binary_packet, demand_size, encoding_type)

    def count_mdeia(self, *nodes: str, medium: Literal["photon", "entanglement"]) -> int:
        attr: str = f"{medium}s"
        if not hasattr(self, attr):
            setattr(self, attr, {})
            return 0
        attribute: Dict[Tuple[str], List[Union[Photon, Tuple[int]]]] = getattr(self, attr)
        if tuple(nodes) not in attribute:
            return 0

    @overload
    def photoncode(self, packet: Dict[str, Dict[str, Union[str, bool]]] = {}) -> List[int]: ...

    @overload
    def photoncode(self, /, photons: List[Photon]) -> List[int]: ...

    def photoncode(self, packet: Optional[Dict[str, Dict[str, Union[str, bool]]]] = {}, /, photons: Optional[List[Photon]] = []) -> List[int]:
        from ..components.waveplates import HalfWaveplate
        from ..kernel.event import Event
        hwp = HalfWaveplate(0.0, self)
        for i, src_node, package in enumerate(packet.items()):
            dst_node: str = package.get("receiver")
            message: str = package.get("message", "")
            send_photons: bool = package.get("send", False)
            photons: List[Photon] = photons or (self.photons.get(*packet) if i == 0 else self.nodes.get(dst_node).qubit_buffer.get(1))
            photons = [hwp.apply(photon) if int(m) else photon for photon, m in zip(photons, message)] or photons
            if send_photons:
                for photon in photons:
                    self.events.push(Event(self.now(), self.nodes.get(src_node), "send_qubit", [dst_node, photon]))
                self.run()
            else: return self.dst_measure(photons)

    def teleport(self, packet: Dict[str, Dict[str, str]]) -> List[int]:
        alpha = complex(1 / math.sqrt(2))
        bsa = bell_state_analyzer(2)
        measurements = OrderedDict()
        ctrl_node: str = packet.get("controller", "")
        for src_node, package in packet.items():
            message: str = package.get("message")
            for mem_info, m in zip(self.nodes.get(src_node).resource_manager.memory_manager, message):
                new_key: int = self.quantum_manager.new([alpha, (1 - 2 * int(m)) * alpha])
                key: int = mem_info.memory.qstate_key
                qstate = self.quantum_manager.get(key)
                ent_keys: List[int] = deepcopy(qstate.keys)
                measurement: Dict[int, int] = self.quantum_manager.run_circuit(bsa, [new_key, key])
                ent_keys.remove(key)
                measurements.update({tuple(ent_keys): [measurement.get(new_key), measurement.get(key)]})
            self.measurements = measurements
            if ctrl_node: self.__control_mechanism(ctrl_node)
            return self.dst_measure()

    def __control_mechanism(self, ctrl_node: str) -> None:
        circuit = Circuit(self.backend, 1)
        if not self.state: circuit.h(0) # Validate this with qss and xor
        circuit.measure(0)
        for keys in self.measurements:
            key = None
            for mem_info in self.nodes.get(ctrl_node).resource_manager.memory_manager:
                key = mem_info.memory.qstate_key
                if key in keys: break
            measurement = self.quantum_manager.run_circuit(circuit, key)
            previous_measurement: List[int] = self.measurements.pop(keys)
            keys = list(keys)
            keys.remove(key)
            previous_measurement.append(measurement.get(key))
            self.measurements.update({tuple(keys): previous_measurement})

    def dst_measure(self, photons: Optional[List[Photon]] = None) -> List[int]:
        if photons:
            self.results: List[int] = [Photon.measure(self.__quantum_states[int(photon.name) // 2], photon) for photon in photons]
            return self.results
        self.results: List[int] = []
        for (key,), measurements in self.measurements.items():
            circuit = Circuit(self.backend, 1)
            for i, correction in enumerate(measurements):
                circuit.apply_gate("z" if int(i % 2) ^ correction ^ self.state else "x", 0)
            circuit.h(0)
            circuit.measure(0)
            result = self.quantum_manager.run_circuit(circuit, key)
            self.results.append(result.get(key))
        return self.results

    def decode(self, binary_packet: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        output_binary: Dict[str, str] = {}
        for package in binary_packet.values():
            if not isinstance(package, dict): continue
            output_binary.update({package.get("receiver", ""): "".join(self.results)})

    def __getattr__(self, __name: str) -> int:
        match __name:
            case "state": return 0

    def request_entanglements(self, src_node: str, dst_node: str, demand_size: int = 1, end_time: float = -1, target_fidelity: float = 1, timeout: float = -1) -> None:
        if (num_eprs := self.count_media(src_node, dst_node, "entanglement")) < demand_size:
            self.nodes.get(src_node).transport_manager.request(dst_node, self.now(), demand_size - num_eprs, end_time, 0, target_fidelity, timeout)
            self.run()
            self.request_entanglements(src_node, dst_node, demand_size, end_time, target_fidelity, timeout)

    def count_media(self, src_node: str, dst_node: str, medium: Literal["photon", "entanglement"]) -> int:
        if not hasattr(self, f"{medium}s"):
            setattr(self, f"{medium}s", {})
            return 0
        attribute: Dict[str, Dict[str, List[Union["Photon", Tuple[int]]]]] = getattr(self, f"{medium}s")
        if dst_node in attribute and src_node in attribute.get(dst_node, {}):
            src_node = src_node + dst_node
            dst_node = src_node[:-len(dst_node)]
            src_node = src_node[len(dst_node):]
        media: List[Union["Photon", Tuple[int]]] = attribute.get(src_node, {}).get(dst_node, [])
        if medium == "entanglement":
            for mem_info in self.nodes.get(src_node).resource_manager.memory_manager:
                if mem_info.state != "ENTANGLED": break
                key = mem_info.memory.qstate_key
                qstate = self.quantum_manager.get(key)
                if len(qstate.state) < 4: raise Exception
                media.append(tuple(reversed(((j := int(qstate.state[0] == qstate.state[3] == 0)), int(qstate.state[0 + j] + qstate.state[3 - j]) // 2))))
            attribute.update({src_node: {dst_node: media}})
        return len(media)

    def setattrs(self, **kwds) -> None:
        for key, value in kwds.items():
            setattr(self, key, value)

    def __iter__(self) -> Iterator["EndNode"]:
        return iter(self.get_nodes_by_type("EndNode"))

    def __getitem__(self, __name:str) -> "Node":
        return self.nodes.get(__name)

    def __call__(self) -> None:
        from ..kernel.event import Event
        self.init()
        self.run
        for event_method, event_params in self._flow:
            self.events.push(event=Event(time=self.now(), activation_method=event_method, act_params=event_params))
            self.init()
            self.run()

    def __len__(self) -> int:
        return len([e_node for e_node in self] + self.get_nodes_by_type("ServiceNode"))

    def __str__(self) -> str:
        num_nodes = len(self)
        num_enodes = len([enode for enode in self])
        num_snodes = num_nodes - num_enodes
        return f"Interface(nodes={num_nodes}, end_nodes={num_enodes}, service_nodes={num_snodes}, entanglements={self.size}, messages={self.message_packets})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the interface showing the memory keys and states of each node.

        Returns:
        str: A string representation of the interface.
        """
        # For each node in the network, get the memory keys and states of its resource manager.
        # Then join the key-state pairs for each state into a single string and join the node memory
        # state strings together with a newline character.
        return "\n".join(
            [
                f"Memory keys of: {node.owner.name}\n"
                + "\n".join(
                    [
                        f"{state.keys}\t{state.state}"
                        for state in [
                            self.quantum_manager.get(info.memory.qstate_key)
                            for info in node.resource_manager.memory_manager
                        ]
                    ]
                )
                for node in self
            ]
        )

    def densecode(self, src_node: str, package: Dict[str, str]) -> None:
        keys: List[int] = []
        message: str = package.get("message", "")
        for mem_info, m1, m2 in zip(self.nodes.get(src_node).resource_manager.memory_manager, message[::2], message[1::2]):
            if mem_info.state != "ENTANGLED": break
            circuit = Circuit(self.backend, 1)
            if int(m2): circuit.x(0)
            if int(m1): circuit.z(0)
            key = mem_info.memory.qstate_key
            keys.append(key)
            self.quantum_manager.run_circuit(circuit, key)
        self.teleport(src_node, package, keys = keys)

    def analyse_circuit(self, circuit:"Circuit", node_map:Dict[str, Union[int, List[int]]], shots:int=1024) -> Tuple[Dict[int, Dict[int, int]], Dict[str, int]]:
        """
        outputs = {500:{0:0.5, 1:0.5}, 1000:{0:0.5, 1:0.5}, ...}
        counts = {"00":145, "01":346, ...}
        """
        assert circuit.num_measured_qubits, "Atleast, one qubit must be measured."
        node_map = {key:([val] if isinstance(val, int) else val) for key, val in node_map.items()}
        assert len([enode for enode in self]) <= circuit.num_qubits, "Number of nodes should be less than number of qubits."
        memory_managers = [self.nodes.get(node_name).resource_manager.memory_manager[i:i+1] for node_name, qubits in node_map.items() for i in range(len(qubits))]
        keys = [info.memory.qstate_key for infos in zip(*memory_managers) for info in infos]
        outputs = {key:{0:0, 1:0} for key in keys}
        counts = {}
        for _ in range(shots):
            for infos in zip(*memory_managers):
                for info in infos:
                    info.to_raw()
                    # Why 'to_raw'?? Beacuse, it not always necessary that the entanglements must be maximal, so can't use transport_manager.request for this
                    # and hence, resetting all the memory states in order to execute a fresh circuit on the memories
            result:dict = self.quantum_manager.run_circuit(circuit=circuit, keys=keys)
            base = ""
            for key, val in result.items():
                base += str(val)
                outputs[key][val] += 1
            if base in counts: counts[base] += 1
            else: counts[base] = 1
        for key, res in outputs.items():
            for bit, count in res.items():
                if count == 0: res.pop(bit)
            if not res: outputs.pop(key)
        return outputs, counts

    @staticmethod
    def U(theta: float, phi: float, lam: float) -> np.ndarray:
        return np.ndarray([[math.cos(theta/2),                   -cmath.exp(1j*lam)*math.sin(theta/2)],
                           [cmath.exp(1j*phi)*math.sin(theta/2), cmath.exp(1j*(phi+lam))*math.cos(theta/2)]])

    def execute_custom_protocol(self, circuits: Dict[str, "Circuit"], encoding_type: Literal["state", "gate"], transmit: bool = False, teleport: bool = False) -> None:
        message: str = list(self.message_packets.values())[0]
        sender: str = list(self.message_packets.keys())[0][0]
        receiver: str = list(self.message_packets.keys())[0][1]
        if transmit:
            self.photoncode(self.nodes.get(receiver), self.nodes.get(sender), message)
            photons = self.photons.get(sender, {}).get(receiver, [])
            gate_map: Dict[str, np.ndarray] = {"h": self.U(math.pi/2, 0, math.pi),
                                               "x": self.U(math.pi, 0, math.pi),
                                               "sx": np.ndarray([[complex(1, 1), complex(1, -1)],
                                                                 [complex(1, -1), complex(1, 1)]])/2,
                                               "y": self.U(math.pi, math.pi/2, math.pi/2),
                                               "z": self.U(0, 0, math.pi),
                                               "s": self.U(0, 0, math.pi/2),
                                               "sdg": self.U(0, 0, -math.pi/2),
                                               "t": self.U(0, 0, math.pi/4),
                                               "tdg": self.U(0, 0, -math.pi/4),
                                               "rx": partial(self.U, phi = -math.pi/2, lam = math.pi/2),
                                               "ry": partial(self.U, phi = 0, lam = 0),
                                               "rz": partial(self.U, theta = 0, phi = 0),
                                               "p": partial(self.U, theta = 0, phi = 0),
                                               "u": self.U}
            for photon in photons:
                for gate, args in sender_circuit.gates:
                    angles = list(filter(lambda x: isinstance(x, float), args))
                    photon.quantum_state.state = (gate_map.get(gate, self.U)(*angles) if angles else
                                                  gate_map.get(gate, self.U(0, 0, 0))) @ photon.quantum_state.state
            self.photoncode(self.nodes.get(receiver))
            self.dst_measure(photons=photons)
        else:
            self.determine_keys()
            sender_circuit: Circuit = circuits.get(sender).duplicate()
            receiver_circuit: Circuit = circuits.get(receiver).duplicate()
            if encoding_type == "state":
                sender_circuit.insert_gate(0, "h", 0)
                sender_circuit.measure_all()
                sender_circuits: List["Circuit"] = [sender_circuit for _ in range(len(message))]
            elif encoding_type == "gate":
                sender_circuits: List["Circuit"] = []
                for m1, m2 in zip(message[::2], message[1::2]):
                    _circuit = sender_circuit.__class__(sender_circuit.num_qubits)
                    if int(m2): _circuit.x(0)
                    if int(m1): _circuit.z(0)
                    _circuit + sender_circuit
                    if teleport:
                        pass
                    sender_circuits.append(_circuit)
            all_results: List[Dict[int, int]] = {}
            for other_circuit in list(circuits.values())[1:]:
                circuit = other_circuit.duplicate()
                # for sender_circuit in sender_circuits:
                #     if sender_circuit.num
            for sender_circuit in sender_circuits:
                if sender_circuit.num_qubits > receiver_circuit.num_qubits:
                    new_keys = [self.quantum_manager.new() for _ in range()]
                all_results.append(self.quantum_manager.run_circuit(sender_circuit))

    def determine_keys(self, mem_state: Optional[Literal["raw", "occupied", "entangled"]] = None) -> None:
        self.keys: Dict[str, List[Union[int, List[int]]]] = {}
        ent_keys: List[List[int]] = []
        for node_seq in self.message_packets:
            for node_name in node_seq:
                keys: List[int] = []
                node: Union["EndNode", "ServiceNode"] = self.nodes.get(node_name)
                for mem_info in node.resource_manager.memory_manager:
                    if mem_state and mem_state != mem_info.state: break
                    key = mem_info.memory.qstate_key
                    keys.append(key)
                    if not mem_state or mem_state == "entangled":
                        mem_qstate = self.quantum_manager.get(key)
                        ent_keys.append(mem_qstate.keys)
                self.keys.update({node_name: keys})
        self.keys.update({"ent_keys": ent_keys})

    def get_keys(self, _:Optional[None], node_index: int, info_state: str = "ENTANGLED") -> None:
        """Retrives the keys of a node, of a specific state. Updates the 'keys' attribute with the required keys.

        Args:
            node_index (int): Index of the node in the network.
            info_state (str, optional): The state of the keys, on demand. Defaults to 'ENTANGLED'.
        """
        keys = []
        for info in self[node_index].resource_manager.memory_manager:
            if info.state == info_state:
                key = info.memory.qstate_key
                state = self.manager.get(key=key)
                keys.append(state.keys)
        self.keys = keys

    def generate_state(self, state: Literal["ghz", "xor"], *nodes: str) -> None:
        self.state: int = {"ghz": 0,
                           "xor": 1}.get(state.lower(), 0)

        circuit1 = Circuit(self.backend, 2)
        circuit1.cx(0, 1)
        if self.state: circuit1.h(0)
        circuit1.measure(1 - self.state)

        circuit2 = Circuit(self.backend, 1)
        if self.state: circuit2.z(0)
        else: circuit2.x(0)

    def generate_state(self, _, state: int = 0, label: str = None) -> None:
        """Generates multi-party entangled states from Bell pairs.
        'state=0' generates GHZ states.
        'state=1' generates XOR states.

        Args:
            state (int, optional): Refernce to a specific entangled state. Defaults to 0.
            label (str, optional): Initial state of the qubits. Defaults to None.
        """
        self.state = state

        qtc: Circuit = Circuit(self.backend, 2)
        qtc = self._add_noise(err_type="reset", qtc=qtc)
        qtc.cx(0, 1)
        if state:
            qtc.h(0)
        qtc.measure(1 - state)

        qc: Circuit = Circuit(self.backend, 1)
        qc = self._add_noise(err_type="reset", qtc=qc)
        if state:
            qc.z(0)
        else:
            qc.x(0)

        for keys in self.message_packets:
            for key in keys[1:-1]:
                for info1, info2 in zip(self.nodes.get(key).resource_manager.memory_manager[: self.size],
                                        self.nodes.get(key).resource_manager.memory_manager[self.size: ]):
                    keys = [info1.memory.qstate_key, info2.memory.qstate_key]
                    qstate = self.quantum_manager.get(keys[1 - state])
                    if self._add_noise(err_type="readout", qtc=qtc, keys=keys).get(keys[1 - state]):
                        self.quantum_manager.run_circuit(qc, list(set(qstate.keys) - set([keys[1 - state]])))
        if label:
            for info in self[0].resource_manager.memory_manager:
                if info.state != "ENTANGLED":
                    break
                keys = self.quantum_manager.get(info.memory.qstate_key).keys
                for key, (i, lbl) in zip(keys, enumerate(label)):
                    qtc: Circuit = Circuit(self.backend, 1)
                    qtc = self._add_noise(err_type="reset", qtc=qtc)
                    if int(lbl):
                        _ = qtc.x(0) if i else qtc.z(0)
                    self.quantum_manager.run_circuit(qtc, [key])

    def _decode(self, *_) -> Dict[Tuple[str], str]:
        self._strings = []
        if hasattr(self, "_initials"):
            node = self.nodes[0]
            for bin_msg in self._bin_dict:
                string = ""
                for info, initial, output in zip(
                    node.resource_manager.memory_manager, self._initials, self._results
                ):
                    bin = bin_msg[info.index] if len(self._bin_dict) > 1 else "0"
                    key = info.memory.qstate_key
                    string += str(initial % 2 ^ output.get(key) ^ int(bin))
                self._strings.append(string)
        else:
            self._strings = ["".join(str(*output.values()) for output in self._results)]
        # print(self._strings)
        self.recv_msgs = {rec[1:]:message for rec, message in zip(list(self.message_packets)[::-1], to_characters(strings=self._strings, _was_binary=self.__is_binary))}
        for k, v in self.recv_msgs.items():
            log.logger.info(f"Received message {k}: {v}")

        return self.recv_msgs

    @staticmethod
    def decode(interfaces: List["QNtSim"], all_returns:Any, *args) -> List[Dict[Tuple[str], str]]:
        """Decodes the received message from the meaured outputs

        Args:
            networks (List[Network]): List of <Network> objects

        Returns:
            List[Dict[int, str]]: The decoded messages for all the 'networks'
        """
        log.logger.info("messages")
        return [interface._decode(return_, *arg) for interface, return_, arg in zip(interfaces, all_returns, args if args else [[None]]*len(interfaces))]

    def dump(self, node_name:Optional[str] = "", info_state:Optional[Literal["ENTANGLED", "RAW", "OCCUPIED"]] = None) -> None:
        """Logs the current memory state of the nodes in the network

        Args:
            returns (Any): Returns from the previous functions
            node_name (str, optional): Index of the node to be dumped. Defaults to ''.
            info_state (str, optional): State of the memory to be dumped. Choices = ['ENTANGLED', 'OCCUPIED', 'RAW']. Defaults to '', upon which all memories are dumped.
        """
        for node in self[node_name] if node_name else self:
            log.logger.debug(f"{node_name}'s memory array")
            keys, states = [], []
            for mem_info in node.resource_manager.memory_manager:
                if info_state and mem_info.state != info_state: break
                key = mem_info.memory.qstate_key
                state = self.quantum_manager.get(key)
                keys.append(state.keys)
                states.append(state.state)
            dataframe = DataFrame({"keys": keys, "states": states})
            # prettify(dataframe)
            log.logger.debug(dataframe.to_string())

    def draw(self, _: Any) -> Graph:
        """_summary_

        Args:
            returns (Any): Returns from the previous function call.

        Returns:
            networkx.Graph: <networkx.Graph> object
        """
        return self.get_virtual_graph()




"""
QSDC: {('n1', 'n2'): message}
QD: {('n1', 'n2'): message1, ('n2', 'n1'): message2} or {('n1', 'n2'): [message1, message2]}
ISSUE: 
QSS: {('n1', 'n2', 'n3'): message}
TODO: No Idea how qc works!!
QC: {('n1', 'n2', ...): message} one-to-many
    {('n2', 'n1'): message1, ('n3', 'n1'): message2, ...} many-to-one
"""

{"n1": {"receiver": "n2",
        "message": "hello",
        "send": True},
 "n2": {"receiver": "n1",
        "message": "world",
        "send": False},
 "medium": "photon"}