import math
import time
from collections import deque
from functools import partial, reduce
from typing import (Any, Callable, Dict, Iterable, List, Optional, Self,
                    Sequence, Tuple, Union)
from networkx import shortest_path

import numpy as np

from ....core.kernel.event import Event
from ....core.kernel.timeline import Timeline
from ....core.topology.node import EndNode, ServiceNode
from ....core.topology.topology import Topology
from ....utils import encoding
from ....utils.log import logger
from ...physical_layer.components.circuit import QutipCircuit
from ...physical_layer.components.photon import Photon
from ...physical_layer.components.waveplates import (HalfWaveplate,
                                                     QuarterWaveplate,
                                                     Waveplate)
from ..noise.noise import ERROR_TYPE, ReadoutError, ResetError
from ..noise.noise_model import NoiseModel
from ..relay_manager import RelayManager
from ..utils.circuits import bell_type_state_analyzer, xor_type_state_analyzer
from ..utils.utils import to_binary, to_string

# Timeline.DLCZ = False
# Timeline.bk = True


class Communication(Timeline, Topology):
    _obj:'Communication' = None
    _flow:List[Callable] = []

    def __init__(self,
                 name:str,
                 topology:Union[Dict[str, Dict[str, Any]], str],
                 messages:Dict[Tuple[str], str],
                 stop_time:float,
                 backend:str="Qutip",
                 formalism:str="ket_vector",
                 require_entanglements:bool=True,
                 timeout:int=10e12,
                 ent_gen_prot:str='bk'|'DLCZ',
                 **kwds) -> None:
        if ent_gen_prot == 'bk':
            self.bk = True
            self.DLCZ = False
        self._obj = self
        self.__name = name or __class__.__name__
        self.__timeout = timeout
        self.messages = messages
        self.__is_binary, self._bin_strs = to_binary()
        self.__dict__.update(
            {
                noise_type:
                    (ERROR_TYPE[noise_type].value(*param_val.get("prob", [0, 0]))
                     if noise_type in ["reset", "readout"] else
                     param_val.get("prob"))
                    if isinstance(param_val, dict) else
                    (ERROR_TYPE[noise_type].value(*param_val)
                     if noise_type in ["reset", "readout"] else
                     param_val)
                    for noise_type, param_val in kwds.get("noise", {}).items()
            })
        if callable(self.size):
            self.size = self.size(len(list(self._bin_strs.values())[0]))
        Timeline.__init__(self=self, stop_time=stop_time, backend=backend, formalism=formalism)
        Topology.__init__(self=self, name=self.__name, timeline=self)
        if (attack:=kwds.get("attack")):
            from ..attack.attacker import Attacker
            Attacker.load_modified_topology(comm_net=self, topology=topology, insert_locations=attack.get("nodes"), attack=attack.get("attack_fn"))
        else:
            (self.load_config_json if isinstance(topology, dict) else self.load_config)(topology)
        self.__dict__.update(kwds)
        if require_entanglements:
            for nodes in self._bin_strs:
                src_node = nodes[0]
                dst_nodes = nodes[1:]
                for dst_node in dst_nodes:
                    self._request_entanglements(src_node=self.nodes.get(src_node),
                                                dst_node=self.nodes.get(dst_node),
                                                demand_size=self.size,
                                                start_time=self.start_time,
                                                end_time=self.end_time,
                                                priority=self.priority,
                                                target_fidelity=self.target_fidelity)
                    logger.info(f"{self.size} EPR pairs generated between {src_node} and {dst_node}")
                    self._identify_entanglements(src_node=self.nodes.get(src_node),
                                                 dst_node=self.nodes.get(dst_node))
        else:
            for nodes in self._bin_strs:
                src_node = nodes[0]
                dst_nodes = nodes[1:]
                for dst_node in dst_nodes:
                    self._initialize_photons(src_node=self.nodes.get(src_node),
                                             dst_node=self.nodes.get(dst_node),
                                             encoding_type=kwds.get("encoding_type", "polarization"))
        self.is_running = True

    def __getattr__(self, name) -> Any:
        if hasattr(self, name):
            return getattr(self, name)
        if name == "size":
            return len(list(self._bin_strs.values())[0])
        if name == "start_time":
            return self.now()
        if name == "end_time":
            return self.now() + 10e12
        if name == "target_fidelity":
            return 0.99
        if name == "initial_states":
            return np.random.randint(4, size=self.size)
        if name in ["photons", "noise"]:
            return {}
        if name == "reset":
            return ResetError(0, 0)
        if name == "readout":
            return ReadoutError(0, 0)
        if name == "pauli":
            return []
        if name in ["priority", "damp", "bitflip", "phaseflip", "depolarize"]:
            return 0

    def __iter__(self) -> Iterable:
        return iter(self.get_nodes_by_type("EndNode"))

    def __getitem__(self, item) -> Union[EndNode, ServiceNode]:
        return self.nodes.get(item)

    def __call__(self) -> Any:
        self.init()
        self.run()

    def __repr__(self) -> str:
        return "\n".join(
            [
                f"Memory keys of: {node.name}\n"
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

    def _request_entanglements(self,
                               src_node:EndNode,
                               dst_node:EndNode,
                               demand_size:int,
                               *,
                               start_time:int=0,
                               end_time=10e12,
                               priority:int=0,
                               target_fidelity:float=1) -> None:
        transport_manager = src_node.transport_manager
        transport_manager.request(responder=dst_node.name,
                                  start_time=start_time,
                                  size=demand_size,
                                  end_time=end_time,
                                  priority=priority,
                                  target_fidelity=target_fidelity,
                                  timeout=self.__timeout)
        self()
        num_epr = sum([1 for info in src_node.resource_manager.memory_manager if info.state == "ENTANGLED"])
        if num_epr < demand_size:
            logger.debug(f"Demand size not met. Requesting for {demand_size-num_epr} entanglements.")
            self._request_entanglements(src_node=src_node, dst_node=dst_node, demand_size=demand_size-num_epr, start_time=self.now())

    def _identify_entanglements(self, src_node:EndNode, dst_node:EndNode) -> None:
        pass

    def _initialize_photons(self, src_node:EndNode, dst_node:EndNode, encoding_type:str="polarization") -> None:
        encoder = getattr(encoding, encoding_type)
        bases = encoder.get("bases")
        self.photons.update({src_node:{dst_node:[Photon(name=bases[state//2],
                                                        encoding_type=encoding_type,
                                                        quantum_state=bases[state//2][state%2])
                                                 for state in self.initial_states]}})
        
    def _apply_noise(self, noise:str, qtc:QutipCircuit, keys:Optional[List[int]]) -> Union[QutipCircuit, Optional[Dict[int, int]]]:
        model = NoiseModel()
        noise_params = self.noise.get(noise)
        qubits = noise_params.get("qubits") if isinstance(noise_params, dict) else None
        match noise:
            case "reset":
                model.add_reset_error(err=self.reset, qubit=qubits)
                return model._apply_reset_error(crc=qtc, size=qtc.size) if hasattr(self, "reset") else qtc # -> QutipCircuit
            case "readout"|"damp":
                if noise == "readout": model.add_readout_error(err=self.readout, qubit=qubits)
                else: model.add_amplitude_damping_error(err=self.damp, qubit=qubits)
                return model.execute(qc=qtc, manager=self.quantum_manager, keys=keys) # -> Optional[Dict[int, int]]
            case "pauli":
                model.add_Pauli_error(err=self.pauli, qubit=qubits)
            case "bitflip":
                model.add_BitFlip_error(err=self.bitflip, qubit=qubits)
            case "phaseflip":
                model.add_PhaseFlip_error(err=self.phaseflip, qubit=qubits)
            case "depolarize":
                model.add_depolarizing_error(err=self.depolarize, qubit=qubits)
        return model.apply(qc=qtc) # -> QutipCircuit

    def _photoncode(self, src_node:EndNode, dst_node:EndNode) -> None:
        hwp = HalfWaveplate(name=np.pi/2, timeline=self)
        for parties, bin_msg in self._bin_strs.items():
            if src_node.name in parties and dst_node.name in parties:
                for photon, char in zip(self.photons.get(src_node).get(dst_node), bin_msg):
                    self.events.push(event=Event(time=self.now()+time.time(), owner=src_node, activation_method="send_qubit",
                                                 act_params=[dst_node.name, hwp.apply(photon) if int(char) else photon]))
                    self.schedule_counter += 1

    def _densecode(self, src_node:EndNode, dst_node:EndNode) -> None:
        for parties, bin_msg in self._bin_strs.items():
            if src_node.name in parties and dst_node.name in parties:
                bin_msg = iter(bin_msg)
                for mem_info in src_node.resource_manager.memory_manager:
                    if mem_info.state == "ENTANGLED":
                        char0 = next(bin_msg)
                        char1 = next(bin_msg)
                        qtc = QutipCircuit(1)
                        qtc = self._apply_noise(noise="reset", qtc=qtc)
                        if int(char1): qtc.x(0)
                        if int(char0): qtc.z(0)
                        mem_key = mem_info.memory.qstate_key
                        self.events.push(event=Event(time=self.now()+time.time(), owner=self.quantum_manager, activation_method="run_circuit",
                                                     act_params=[qtc, [mem_key]]))
                        self.schedule_counter += 1

    def _teleport(self, src_node:EndNode, dst_node:EndNode) -> None:
        self._pauli_ctrls = {}
        for parties, bin_msg in self._bin_strs.items():
            if src_node.name in parties and dst_node.name in parties:
                corrections = {}
                bin_msg = iter(bin_msg)
                for mem_info in src_node.resource_manager.memory_manager:
                    if mem_info.state == "ENTANGLED":
                        char = next(bin_msg)
                        new_mem_key = self.quantum_manager.new(getattr(encoding, "polarization").get("bases")[1][char])
                        mem_key = mem_info.memory.qstate_key
                        mem_meas = self._apply_noise(noise="readout", qtc=bell_type_state_analyzer(2), keys=[new_mem_key, mem_key])
                        ket_state = self.quantum_manager.get(mem_key)
                        corrections[tuple(set(ket_state.keys)-set([mem_key]))] = [mem_meas.get(new_mem_key), mem_meas.get(mem_key)]
                self._pauli_ctrls.update({(src_node, dst_node):corrections})

    def _decode(self, src_node:EndNode, dst_nodes:List[EndNode]) -> None:
        self()
        self._strings = {}
        for dst_node in dst_nodes:
            if dst_node in self.photons.get(src_node, {}):
                recv_photons = dst_node.qubit_buffer.get(1, [])
                self._strings.update({(src_node.name, dst_node.name):"".join([str(Photon.measure(basis=photon.name, photon=photon)) for photon in recv_photons])})

    # def _get_state(self, state:str, nodes:List[EndNode]):
    #     topology = {node_name:node.neighbors for node_name, node in self.__configuration.nodes.items() if node.__class__ in [EndNode, ServiceNode]}
    #     routes = [self._find_route(src_node=src_node.name, dst_node=dst_node.name, topology=topology) for src_node, dst_node in zip(nodes[:-1], nodes[1:])]
    #     service_nodes = self._extract_service_nodes(routes=routes)
    #     for service_node in service_nodes:
    #         neighbour_nodes = service_node.neighbors
    #         self._swap_entanglement(node=service_node)

    def _swap_entanglement(self, state:str, current_node:ServiceNode, neighbor_nodes:List[Union[EndNode, ServiceNode]], qtc:QutipCircuit) -> None:
        current_keys = [info.memory.qstate_key for info in current_node.resource_manager.memory_manager if info.state=="ENTANGLED"]
        neighbor_keys = [[self.quantum_manager.get(info.memory.qstate_key).keys for info in neighbor_node.resource_manager.memory_manager if info.state=="ENTANGLED"] for neighbor_node in neighbor_nodes]
        circuit = (
            bell_type_state_analyzer(len(neighbor_nodes)) if state == "ghz" else
            xor_type_state_analyzer(len(neighbor_nodes)) if state == "xor" else
            qtc
            )
        for entangled_keys in zip(*neighbor_keys):
            swap_keys = []
            for ent_keys in entangled_keys:
                swap_keys.append(set(ent_keys) & set(current_keys))
            swap_keys.sort()
            results = self.quantum_manager.run_circuit(circuit=circuit, keys=swap_keys)
            for key in swap_keys:
                pass

    def _extract_service_nodes(self, routes:List[List[str]]) -> List[str]:
        service_nodes = set()
        for route in routes:
            for node in route[1:-1]:
                service_nodes.add(node)
        return list(service_nodes)

    def get_shortest_route(self, src_node:Optional[str], dst_node:Optional[str]) -> Union[List[str], Dict[str, List[str]], Dict[str, Dict[str, List[str]]]]:
        graph = self.generate_nx_graph()
        return shortest_path(graph, source=src_node, target=dst_node)

    def _meas_all(self, meas_results:Dict[Tuple, List[int]], /):
        for key, val in meas_results.items():
            qtc = QutipCircuit(1)
            qtc = self._apply_noise(noise="reset", qtc=qtc)
            if val[1]:
                qtc.x(0)
            if val[0]:
                qtc.z(0)
            qtc.h(0)
            qtc.measure(0)

    @classmethod
    def create_object(cls, topology:Dict, messages, stop_time:float, backend:str="Qutip", formalism:str="ket_vector", require_entanglements:bool=True, timeout:int=10e12, **kwds) -> Self:
        cls._obj = cls(topology=topology, messages=messages, stop_time=stop_time, backend=backend, formalism=formalism, require_entanglements=require_entanglements, timeout=timeout, **kwds)
        return cls._obj

    @staticmethod
    def encode(comm_obj:"Communication", src_node:str, dst_node:str, encode_func:Union[Callable, str]="photoncode"|"densecode"|"teleport") -> None:
        setattr(comm_obj, "__encode", partial(encode_func, comm_obj) if callable(encode_func) else getattr(comm_obj, "_"+encode_func))
        comm_obj.events.push(event=Event(time=comm_obj.now(), owner=comm_obj, activation_method=[comm_obj.nodes.get(src_node), comm_obj.nodes.get(dst_node)]))
        pass

    @staticmethod
    def decode(comm_objs:Iterable["Communication"]):
        for comm_obj in comm_objs:
            comm_obj._decode()
        pass

    def execute():
        pass

""" messages
1-to-1: {(s1, r1):m1, (s2, r2):m2, ...} unidirectional
        {(s1, r1):m1, (r1, s1):m2} bidirectional
1-to-many: {(s1, r1, r2, r3, ...):m1} secret-sharing
many-to-1: {(s1, r1):m1, (s2, r1):m2, (s3, r1):m3, ...}
"""