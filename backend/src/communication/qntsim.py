import cmath
from functools import partial
import math
import time
from types import NoneType
from typing import (TYPE_CHECKING, Any, Callable, Dict, Iterator, List,
                    Literal, Optional, Tuple, TypeAlias, Union, overload)

import numpy as np
from networkx import Graph
from pandas import DataFrame
from qntsim.communication.analyzer_circuits import bell_type_state_analyzer
from qntsim.communication.noise_model import NoiseModel
from qntsim.communication.utils import to_binary, to_characters
from qntsim.components.photon import Photon
from qntsim.components.waveplates import Waveplate
from qntsim.kernel.circuit import BaseCircuit
from qntsim.kernel.timeline import Timeline
from qntsim.log_functions import log_object, log_object_instantiation
from qntsim.topology.topology import Topology
from qntsim.utils import log

# from rich_dataframe import prettify


if TYPE_CHECKING:
    from qntsim.topology.node import EndNode, Node, ServiceNode


class QNtSim(Timeline, Topology):
    """
    Initializes a quantum network object, which consists of nodes that can communicate with each other using qubits.

    During object creation:
        Args:
        - topology (str): A string representing the type of network topology, e.g. 'complete', 'line', 'ring', 'grid'.
        - messages (Dict[Tuple, str]): A dictionary containing the messages to be sent, in the form {(sender, receiver): message}.
        - name (str): An optional string representing the name of the network.
        - backend (str): An optional string representing the name of the backend to be used, e.g. 'Qutip'.
        - parameters (str): An optional string representing the name of the file containing the network parameters.
        - stop_time (int): An optional integer representing the time to stop the simulation, in nanoseconds.
        - start_time (int): An optional integer representing the time to start the simulation, in nanoseconds.
        - end_time (int): An optional integer representing the time to end the simulation, in nanoseconds.
        - priority (int): An optional integer representing the priority of the network.
        - target_fidelity (float): An optional float representing the target fidelity of the network.
        - timeout (int): An optional integer representing the timeout of the network, in nanoseconds.
        - **kwds (Any): Additional keyword arguments to be passed to the network.

        (Optional) Kwds:
            size (int, callable): The number of n2n entangled pairs required in the network.
            keys_of (int): Index of the node, for which the keys are requested.
            label (str): Initial states of the qubits. Doesn't work with superposition statess.

    During function call:
        Args:
            id_ (int, optional): The id of the <Network> object. Defaults to 0.

    Attributes:
        Network.__Network_name: Name of the object for identification.
        Network._backend: The backend on which the circuits are executed.
        Network._bell_pairs: Dictionary of the bell pairs with the index denoting the entanglement between the memory keys
        Network._bin_msgs: Binary equivalent of <Network>.messages.
        Network._flow: List of functions which will be executed in the defined sequence.
        Network._initials: Initials states of single photons.
        Network._kwds: Keyword arguements provided to the object, required during specific function calls.
        Network._net_topo: <Topology> object, managing network topologies.
        Network._outputs: Measurement outcomes from measuring out the photons.
        Network._parameters: the device parameters of the optical components.
        Network._strings: List of binary strings generated from the measurement outcomes.
        Network._timeline: <Timeline> object, which provides an interface for the simulation kernel and drives event execution.
        Network._topology: Topology of the network.
        Network.cchannels: Classical channels between the nodes in the network.
        Network.manager: <QuantumManager> object to track and manage quantum states.
        Network.messages: Messages to be transfered over the network.
        Network.nodes: End nodes present in the network.
        Network.qchannels: Quantum channels between the nodes in the network.
        Network.recv_msgs: Dictionary of the received messages, recreated from the strings.
        Network.size: Number of entangled pairs required for successful transmission of the messages.

    Methods:
        Network.__call__(id_): Calls and executes the network of 'id_'
        Network.__getitem__(item): Return indexed end node.
        Network.__iter__(): Iterates over the nodes in the network
        Network.__repr__(): Returns the string representation of the <Network> object
        Network._decode(): Reconstructs the message from the received messages in the network
        Network._execute(id_): Executes the network of 'id_'
        Network._identify_states(): Notes the entanglement of each keys
        Network._initialize_photons(): Initializes photons into random states among {|H⟩, |V⟩, |u⟩, |d⟩}
        Network._initiate(): Initiates the simulator, while requesting and rectifying entanglements or, initializing photons
        Network._rectify_entanglements(label): Rectifies the entanglements generated by the simulator
        Network._request_entanglements(): Requests entanglements from the simulator
        Network._set_parameters(): Tunes in the optical components
        Network.get_keys(node_index, info_state): Extracts the info on keys for the states matching the 'info_state'
        Network.generate_state(state, label): Generates multi-party entangled states from Bell pairs
        Network.encode(msg_index, node_index): Transmits message over the network through encoding the info on single photons
        Network.superdense_code(msg_index, node_index): Tranmits message over the network through superdense coding
        Network.teleport(msg_index, node_index): Teleports the message over the network
        Network.measure(): Measures the qubits in the network
        Network.dump(node_name, info_state): Dumps all the quantum states maching with the 'info_state' for the nodes provided
        Network.draw(): Generates a visual representation of the topology of network
        Network.execute(networks): Executes all the networks in the list
        Network.decode(networks, *args): Reconstructs the message from the received messages for all the networks

    Further info:

    Examples:
        QSDC with mutual authentication (IP2):
            from functools import partial
            from typing import Any, Dict, List, Tuple
            from qntsim.library import insert_check_bits, insert_decoy_photons, bell_type_state_analyzer, Protocol
            from qntsim.library.attack import Attack, ATTACK_TYPE

            class Party:
                input_messages:Dict[Tuple, str] = None
                id:str = None
                received_msgs:Dict[int, str] = None

            class Alice(Party):
                chk_bts_insrt_lctns:List[int] = None
                num_check_bits:int = None

                @classmethod
                def input_check_bits(cls, network:Network, returns:Any):
                    .
                    .
                    .

                @classmethod
                def encode(cls, network:Network, returns:Any):
                    .
                    .
                    .

                @classmethod
                def insert_new_decoy_photons(cls, network:Network, returns:Any, num_decoy_photons:int):
                    .
                    .
                    .

            class Bob(Party):
                @classmethod
                def setup(cls, network:Network, returns:Any, num_decoy_photons:int):
                    .
                    .
                    .

                def decode(network:Network, returns:Any):
                    .
                    .
                    .

                @classmethod
                def check_integrity(cls, network:Network, returns:Any, cls1, threshold:float):
                    .
                    .
                    .

            class UTP:
                @classmethod
                def check_channel_security(cls, network:Network, returns:Any, cls1, cls2, threshold:float):
                    .
                    .
                    .

                def authenticate(network:Network, returns:Any, cls1, cls2, circuit:QutipCircuit):
                    .
                    .
                    .

                def measure(network:Network, returns:Any, circuit:QutipCircuit, cls):
                    .
                    .
                    .

            def pass_(network:Network, returns:Any):
                return returns

            topology = '2n_linear.json'
            Alice.input_messages = {(1, 2):'011010'
            Alice.id = '1011'
            Alice.num_check_bits = 4
            Bob.id = '0111'
            threshold = 0.2
            attack, chnnl = (None, None) #(attack_type, channel_no.) channel_no. doesn't implement attack. one can say that the channel 1 is secured.
            chnnl = [1 if i==chnnl else 0 for i in range(3)]
            Network._funcs = [partial(Alice.input_check_bits),
                            partial(Bob.setup, num_decoy_photons=num_decoy_photons),
                            partial(Alice.encode),
                            partial(Attack.implement, attack=ATTACK_TYPE[attack].value) if attack and chnnl[0] else partial(pass_),
                            partial(UTP.check_channel_security, cls1=Alice, cls2=Bob, threshold=threshold),
                            partial(Alice.insert_new_decoy_photons, num_decoy_photons=num_decoy_photons),
                            #   partial(Attack.implement, attack=ATTACK_TYPE[attack].value) if attack and chnnl[1] else partial(pass_),
                            partial(UTP.check_channel_security, cls1=UTP, cls2=Alice, threshold=threshold),
                            partial(Attack.implement, attack=ATTACK_TYPE[attack].value) if attack and chnnl[2] else partial(pass_),
                            partial(UTP.check_channel_security, cls1=UTP, cls2=Bob, threshold=threshold),
                            partial(UTP.authenticate, cls1=Alice, cls2=Bob, circuit=bell_type_state_analyzer(2)),
                            partial(UTP.measure, circuit=bell_type_state_analyzer(2), cls=Alice),
                            partial(Bob.decode),
                            partial(Bob.check_integrity, cls1=Alice, threshold=threshold)]

            network = Network(topology='2n_linear.json',
                            messages=Alice.input_messages,
                            name='ip2',
                            size=lambda x:(x+Alice.num_check_bits+len(Alice.id)+len(Bob.id))//2,
                            label='00')
            network()
            # print(f'Received messages:{Bob.received_messages}')
            # print(f'Error in execution:{mean(protocol.mean_list)}')
    """

    __backend_type:TypeAlias = Literal["Qiskit", "Qutip"]
    __encoding_type:TypeAlias = Literal["polarization", "time_bin", "single_atom"]
    __formalism_type:TypeAlias = Literal["ket_vector", "density_matrix"],
    _flow: List[Tuple[Callable[..., NoneType], Tuple[Any]]] = []

    def __init__(self, topology: Union[str, Dict[str, Dict[str, Any]]], messages: Dict[Tuple[str], str], name: Optional[str] = "",
                 backend: __backend_type = "Qutip", formalism: __formalism_type = "ket_vector", stop_time: float = 10e12,
                 end_time: float = 5e12, timeout: float = 1e12, priority: int = 0, target_fidelity: float = 1.0,
                 require_entanglement:bool = True, ent_gen_protocol:Literal["bk", "DLCZ"] = "bk", **kwds) -> None:
        # Create a timeline and topology for the quantum network
        Timeline.__init__(self=self, stop_time=stop_time, backend=backend, formalism=formalism)
        Topology.__init__(self=self, name=name, timeline=self)
        log.track_module(".")
        log.set_logger(__class__.__name__, self, "out.log")
        log.set_logger_level("debug")
        log_object_instantiation(self)
        if ent_gen_protocol == "DLCZ":
            Timeline.DLCZ = True
            Timeline.bk = False
        self._topology = topology
        self.messages = messages
        self.__is_binary, self._bin_dict = to_binary(msg_dict = messages)
        print("converted")
        if callable((size := kwds.pop("size", self.size))):
            self.size = size(self.size)
        print(self.size)
        self.__dict__.update(**kwds)
        # if hasattr(self, "noise"):
        #     self.__dict__.update(
        #         {
        #             noise: ERROR_TYPE[noise].value(*probs)
        #             for noise, probs in self.noise.items()
        #         }
        #     )
        self._initiate(require_entanglement=require_entanglement,
                       end_time=end_time,
                       priority=priority,
                       target_fidelity=target_fidelity,
                       timeout=timeout)
        log_object(self)

    def __getattr__(self, __name:str) -> ...:
        match __name:
            case "size":
                return len(list(self._bin_dict.values())[0])

    def __iter__(self) -> Iterator["EndNode"]:
        """
        Returns an iterator over the nodes in the network.

        Args:
        - None

        Returns:
        - An iterator over the nodes in the network.
        """
        return iter(self.get_nodes_by_type("EndNode"))

    def __getitem__(self, __name:str) -> "Node":
        """
        Retrieve the node of the specified name.

        Parameters:
            __name (str): The name of the node to retrieve.

        Returns:
            Node: The node of the specified name.
        """
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
        return f"Interface(nodes={num_nodes}, end_nodes={num_enodes}, service_nodes={num_snodes}, entanglements={self.size}, messages={self.messages})"

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

    def _initiate(self, require_entanglement:bool=True, *args, **kwds) -> None:
        """
        Initializes the quantum network by creating a timeline and topology,
        setting parameters, and identifying end nodes. If there are multiple end nodes,
        it requests entanglements, identifies states, rectifies entanglements,
        and logs information. Otherwise, it initializes photons.
        """
        print(f"debug: initiating simulation")

        # Load the configuration for the network topology
        (self.load_config if isinstance(self._topology, str) else self.load_config_json)(self._topology)
        # self.init()
        # self.run()

        # If entanglements has been requested, then
        if require_entanglement:
            # Set initial values for Bell pairs and state identification
            self._bell_pairs = {}
            for node_seq in self.messages:
                src_node = self.nodes.get(node_seq[0])
                for dst_name in node_seq[1:]:
                    self._request_entanglements(src_node=src_node, dst_node=(dst_node := self.nodes.get(dst_name)), demand_size=self.size, *args, **kwds)
                    pass
                    self._identify_epr_pairs(src_node=src_node, dst_node=dst_node)
        # Otherwise, initialize photons
        else:
            self.photons: Dict[str, Dict[str, List["Photon"]]] = {}
            self._initial_states: Dict[str, Dict[str, np.ndarray]] = {}
            for node_seq in self.messages:
                src_node = self.nodes.get(node_seq[0])
                for dst_name in node_seq[1:]:
                    self._initialize_photons(src_node=src_node, dst_node=(dst_node := self.nodes.get(dst_name)), encoding_type=kwds.get("encoding", "polarization"))

    def _request_entanglements(self, src_node:"EndNode", dst_node:"EndNode", demand_size:int = 1, end_time:float = math.inf, priority:int = 0, target_fidelity:float = 1, timeout:float = math.inf) -> None:
        print(f"info: Pre-request\n{self.events}")
        src_node.transport_manager.request(responder=dst_node.name, start_time=1e12, size=demand_size, end_time=end_time, priority=priority, target_fidelity=target_fidelity, timeout=timeout)
        print(f"info: Post-request\n{self.events}")
        self.init()
        self.run()
        print(f"info: Post-execution\n{self.events}")
        # if (num_eprs := sum([1 for info in src_node.resource_manager.memory_manager if info.state == "ENTANGLED"])) < demand_size:
        #     self._request_entanglements(src_node, dst_node, demand_size-num_eprs, end_time=end_time, priority=priority, target_fidelity=target_fidelity)

    def _identify_epr_pairs(self, src_node:"EndNode", dst_node:"EndNode") -> None:
        """
        Identifies the quantum states of a circuit.
        """
        pairs = {}
        for mem_info in src_node.resource_manager.memory_manager:
            if mem_info.state != "ENTANGLED":
                break
            key = mem_info.memory.qstate_key
            state = self.quantum_manager.get(key=key).state
            pair_index_j = 0 if state[1] == state[2] == 0 else 1
            pair_index_i = (1-(state[pair_index_j]//state[3-pair_index_j]))//2
            pairs.update({tuple(self.quantum_manager.get(key=key).keys):[pair_index_i, pair_index_j]})
        self._bell_pairs.update({(src_node.name, dst_node.name):pairs})

    def _rectify_entanglements(self, label: str) -> None:
        """
        Rectifies the entanglements of a circuit based on the Bell pairs identified.
        """
        for (key1, key2), (
            bell_pair_index_i,
            bell_pair_index_j,
        ) in self._bell_pairs.items():
            qtc: BaseCircuit = BaseCircuit(self.backend, 1)
            if bell_pair_index_j ^ int(label[1]):
                qtc.x(0)
            if bell_pair_index_i ^ int(label[0]):
                qtc.z(0)
            self.quantum_manager.run_circuit(qtc, [key1])
            self._bell_pairs[(key1, key2)] = (int(label[0]), int(label[1]))

    def _add_noise(self, err_type: str, qtc: BaseCircuit, keys: List[int] = None) -> None:
        """
        Add noise to a QutipCircuit object using the specified error model.

        Args:
        - err_type (str): The type of error to apply ('reset' or 'readout').
        - qtc (QutipCircuit): The QutipCircuit object to apply the error to.
        - keys (Optional[List[int]]): A list of qubit indices to apply the readout error to.

        Returns:
        - QutipCircuit: The QutipCircuit object with the specified error applied.
        """
        model = NoiseModel()  # Create a new noise model

        # Apply the specified error to the noise model
        match err_type:
            case "reset":
                if hasattr(self, "reset"):
                    model.add_reset_error(err=self.reset)
                    # Apply the reset error to the circuit
                    return model._apply_reset_error(crc=qtc, size=qtc.size)
                return (
                    qtc  # If no reset error is specified, return the original circuit
                )
            case "readout":
                if hasattr(self, "readout"):
                    model.add_readout_error(err=self.readout)
                # Apply the readout error to the circuit
                return model._apply_readout_error_qntsim(
                    crc=qtc, manager=self.quantum_manager, keys=keys
                )

    def _initialize_photons(self, src_node: "EndNode", dst_node: "EndNode", encoding_type: __encoding_type) -> None:
        """
        Initializes the photons for a quantum circuit.
        """
        from ..utils import encoding
        bases: List[Optional[Tuple[Tuple[complex]]]] = getattr(encoding, encoding_type).get("bases")
        initial_states = np.random.randint(4, size=self.size)
        photons = [Photon(name="", encoding_type=encoding_type, quantum_state=bases[initial_state // 2][initial_state % 2])
                   for initial_state in initial_states]
        self.photons.update({src_node.name: {dst_node.name: photons}})
        self._initial_states.update({src_node.name: {dst_node.name: initial_states}})
        log.logger.info(f"Initialized {self.size} photons with initial states {initial_states}")
        self.__sent_photons = False

    # To encode and send the photons
    @overload
    def _photoncode(self, dst_node: "EndNode", src_node: "EndNode", bin_msg: str) -> None: ...

    # To recieve, encode and measure the photons
    @overload
    def _photoncode(self, dst_node: "EndNode", bin_msg: str) -> None: ...

    # To receive and measure the photons
    @overload
    def _photoncode(self, dst_node: "EndNode") -> None: ...

    def _photoncode(self, dst_node: "EndNode", src_node: Optional["EndNode"] = None, bin_msg: Optional[str] = None) -> None:
        from ..components.waveplates import HalfWaveplate
        from ..kernel.event import Event
        hwp = HalfWaveplate(name=0.0, timeline=self)
        if self.__sent_photons:
            self.init()
            self.run()
            photons = dst_node.qubit_buffer.get(1, [])
            self._measure(photons = photons if not bin_msg else [hwp.apply(photon) if int(char) else photon for photon, char in zip(photons, bin_msg)])
            return
        [self.events.push(Event(self.now()+time.time(), src_node, "send_qubit", [dst_node.name, hwp.apply(photon) if int(char) else photon]))
         for parties, bin_msg in self._bin_dict.items()
         if set([src_node.name, dst_node.name]).issubset(parties)
         for photon, char in zip(self.photons.get(src_node.name).get(dst_node.name), bin_msg)]
        self.init()
        self.run()
        self.__sent_photons = True

    def _densecode(self, src_node:"EndNode", dst_node:"EndNode") -> None:
        for parties, bin_msg in self._bin_dict.items():
            if set([src_node.name, dst_node.name]).issubset(parties):
                keys = []
                for bin1, bin2, mem_info in zip(bin_msg[::2], bin_msg[1::2], src_node.resource_manager.memory_manager):
                    if mem_info.state != "ENTANGLED": break
                    qtc: BaseCircuit = BaseCircuit(self.backend, 1)
                    if int(bin2): qtc.x(0)
                    if int(bin1): qtc.z(0)
                    key = mem_info.memory.qstate_key
                    keys.append(key)
                    self.quantum_manager.run_circuit(qtc, [key])
                self._teleport(src_node=src_node, dst_node=dst_node, keys = keys)

    def _teleport(self, src_node:"EndNode", dst_node:"EndNode", **kwds) -> None:
        self._corrections = {}
        alpha = complex(1 / math.sqrt(2))
        new_keys = iter(kwds.get("keys", []))
        for parties, bin_msg in self._bin_dict.items():
            if set([src_node.name, dst_node.name]).issubset(parties):
                for bin, mem_info in zip(bin_msg, src_node.resource_manager.memory_manager):
                    if mem_info.state != "ENTANGLED": break
                    key = mem_info.memory.qstate_key
                    new_key = next(new_keys) or self.quantum_manager.new([alpha, ((-1)**int(bin))*alpha])
                    state = self.quantum_manager.get(key)
                    keys = tuple(set(state.keys) - set([key]))
                    output:dict = self.quantum_manager.run_circuit(bell_type_state_analyzer(2), [new_key, key])
                    self._corrections[keys] = [output.get(new_key), output.get(key)]

    def _measure(self, photons:Optional["Photon"] = None, **kwds) -> None:
        if photons:
            from ..utils import encoding
            encoder:dict = getattr(encoding, kwds.get("encoding", "polarization"))
            bases = encoder.get("bases")
            self._results = [Photon.measure(basis=bases[initial_state//2], photon=photon) for initial_state, photon in zip(self.initial_states, photons)]
        elif hasattr(self, "_corrections"):
            for keys, value in self._corrections.items():
                if len(keys) > 1:
                    key = max(keys)
                    qtc: BaseCircuit = BaseCircuit(self.backend, 1)
                    qtc = self._add_noise(err_type="reset", qtc=qtc)
                    if ~self.state:
                        qtc.h(0)
                    qtc.measure(0)
                    output = self._add_noise(
                        err_type="readout", qtc=qtc, keys=[key]
                    ).get(key)
                qtc: BaseCircuit = BaseCircuit(self.backend, 1)
                qtc = self._add_noise(err_type="reset", qtc=qtc)
                if output:
                    if self.state:
                        qtc.x(0)
                    else:
                        qtc.z(0)
                if value[1]:
                    qtc.x(0)
                if value[0]:
                    qtc.z(0)
                qtc.h(0)
                qtc.measure(0)
                key = min(keys)
                self._results.append(
                    self._add_noise(err_type="readout", qtc=qtc, keys=[key])
                )

    def analyse_circuit(self, circuit:"BaseCircuit", node_map:Dict[str, Union[int, List[int]]], shots:int=1024) -> Tuple[Dict[int, Dict[int, int]], Dict[str, int]]:
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

    def execute_custom_protocol(self, circuits: Dict[str, "BaseCircuit"], encoding_type: Literal["state", "gate"], transmit: bool = False, teleport: bool = False) -> None:
        message: str = list(self.messages.values())[0]
        sender: str = list(self.messages.keys())[0][0]
        receiver: str = list(self.messages.keys())[0][1]
        if transmit:
            self._photoncode(self.nodes.get(receiver), self.nodes.get(sender), message)
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
            self._photoncode(self.nodes.get(receiver))
            self._measure(photons=photons)
        else:
            self.determine_keys()
            sender_circuit: BaseCircuit = circuits.get(sender).duplicate()
            receiver_circuit: BaseCircuit = circuits.get(receiver).duplicate()
            if encoding_type == "state":
                sender_circuit.insert_gate(0, "h", 0)
                sender_circuit.measure_all()
                sender_circuits: List["BaseCircuit"] = [sender_circuit for _ in range(len(message))]
            elif encoding_type == "gate":
                sender_circuits: List["BaseCircuit"] = []
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
        for node_seq in self.messages:
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

    def generate_state(self, _, state: int = 0, label: str = None) -> None:
        """Generates multi-party entangled states from Bell pairs.
        'state=0' generates GHZ states.
        'state=1' generates XOR states.

        Args:
            state (int, optional): Refernce to a specific entangled state. Defaults to 0.
            label (str, optional): Initial state of the qubits. Defaults to None.
        """
        self.state = state

        qtc: BaseCircuit = BaseCircuit(self.backend, 2)
        qtc = self._add_noise(err_type="reset", qtc=qtc)
        qtc.cx(0, 1)
        if state:
            qtc.h(0)
        qtc.measure(1 - state)

        qc: BaseCircuit = BaseCircuit(self.backend, 1)
        qc = self._add_noise(err_type="reset", qtc=qc)
        if state:
            qc.z(0)
        else:
            qc.x(0)

        for keys in self.messages:
            for key in keys[1:-1]:
                for info1, info2 in zip(
                    self.nodes.get(key).resource_manager.memory_manager[
                        : self.size
                    ],
                    self.nodes.get(key).resource_manager.memory_manager[
                        self.size :
                    ],
                ):
                    keys = [info1.memory.qstate_key, info2.memory.qstate_key]
                    qstate = self.quantum_manager.get(keys[1 - state])
                    if self._add_noise(err_type="readout", qtc=qtc, keys=keys).get(
                        keys[1 - state]
                    ):
                        self.quantum_manager.run_circuit(
                            qc, list(set(qstate.keys) - set([keys[1 - state]]))
                        )
        if label:
            for info in self[0].resource_manager.memory_manager:
                if info.state != "ENTANGLED":
                    break
                keys = self.quantum_manager.get(info.memory.qstate_key).keys
                for key, (i, lbl) in zip(keys, enumerate(label)):
                    qtc: BaseCircuit = BaseCircuit(self.backend, 1)
                    qtc = self._add_noise(err_type="reset", qtc=qtc)
                    if int(lbl):
                        _ = qtc.x(0) if i else qtc.z(0)
                    self.quantum_manager.run_circuit(qtc, [key])

    # def measure(self, _: Any):
    #     """Measures the qubits and stores the output for decoding the message

    #     Args:
    #         returns (Any): Returns from the previous function call.
    #     """
    #     self._results = []
    #     if hasattr(self, "_initials"):
    #         node = self[0]
    #         for info, initial in zip(
    #             node.resource_manager.memory_manager, self._initials
    #         ):
    #             key = info.memory.qstate_key
    #             qtc = QutipCircuit(1)
    #             qtc = self._add_noise(err_type="reset", qtc=qtc)
    #             if initial // 2:
    #                 qtc.h(0)
    #             qtc.measure(0)
    #             self._results.append(
    #                 self._add_noise(err_type="readout", qtc=qtc, keys=[key])
    #             )
    #     elif hasattr(self, "_corrections"):
    #         output = 0
    #         # print(self._corrections)
    #         for keys, value in self._corrections.items():
    #             # print(keys)
    #             if len(keys) > 1:
    #                 key = max(keys)
    #                 qtc = QutipCircuit(1)
    #                 qtc = self._add_noise(err_type="reset", qtc=qtc)
    #                 if ~self.state:
    #                     qtc.h(0)
    #                 qtc.measure(0)
    #                 output = self._add_noise(
    #                     err_type="readout", qtc=qtc, keys=[key]
    #                 ).get(key)
    #             qtc = QutipCircuit(1)
    #             qtc = self._add_noise(err_type="reset", qtc=qtc)
    #             if output:
    #                 if self.state:
    #                     qtc.x(0)
    #                 else:
    #                     qtc.z(0)
    #             if value[1]:
    #                 qtc.x(0)
    #             if value[0]:
    #                 qtc.z(0)
    #             qtc.h(0)
    #             qtc.measure(0)
    #             key = min(keys)
    #             self._results.append(
    #                 self._add_noise(err_type="readout", qtc=qtc, keys=[key])
    #             )

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
        self.recv_msgs = {rec[1:]:message for rec, message in zip(list(self.messages)[::-1], to_characters(strings=self._strings, _was_binary=self.__is_binary))}
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