"""Code for Barrett-Kok entanglement Generation protocol

This module defines code to support entanglement generation between single-atom memories on distant nodes.
Also defined is the message type used by this implementation.
Entanglement generation is asymmetric:

* EntanglementGenerationA should be used on the QuantumRouter (with one node set as the primary) and should be started via the "start" method
* EntanglementGeneraitonB should be used on the BSMNode and does not need to be started
"""

from enum import Enum, auto
from math import sqrt
from typing import List, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from ..components.memory import Memory
    from ..topology.node import Node
    from ..components.bsm import SingleAtomBSM

from .entanglement_protocol import EntanglementProtocol
from ..message import Message
from ..kernel._event import Event
from ..kernel.process import Process
from ..components.circuit import Circuit
from ..utils import log


class GenerationMsgType(Enum):
    """Defines possible message types for entanglement generation."""

    NEGOTIATE = auto()
    NEGOTIATE_ACK = auto()
    MEAS_RES = auto()
    FAILURE = auto()
    RELEASE_BSM = auto()
    REQUEST_BSM = auto()
    BSM_ALLOCATE = auto()
    ENTANGLEMENT_SUCCESS = auto()


class EntanglementGenerationMessage(Message):
    """Message used by entanglement generation protocols.

    This message contains all information passed between generation protocol instances.
    Messages of different types contain different information.

    Attributes:
        msg_type (GenerationMsgType): defines the message type.
        receiver (str): name of destination protocol instance.
        qc_delay (int): quantum channel delay to BSM node (if `msg_type == NEGOTIATE`).
        frequency (float): frequency with which local memory can be excited (if `msg_type == NEGOTIATE`).
        emit_time (int): time to emit photon for measurement (if `msg_type == NEGOTIATE_ACK`).
        res (int): detector number at BSM node (if `msg_type == MEAS_RES`).
        time (int): detection time at BSM node (if `msg_type == MEAS_RES`).
        resolution (int): time resolution of BSM detectors (if `msg_type == MEAS_RES`).
    """

    def __init__(self, msg_type: GenerationMsgType, receiver: str, **kwargs):
        super().__init__(msg_type, receiver)
        self.protocol_type = EntanglementGenerationA

        if msg_type is GenerationMsgType.NEGOTIATE:
            self.qc_delay = kwargs.get("qc_delay")
            self.frequency = kwargs.get("frequency")

        elif msg_type is GenerationMsgType.NEGOTIATE_ACK:
            self.emit_time_0 = kwargs.get("emit_time_0")
            self.emit_time_1 = kwargs.get("emit_time_1")

        elif msg_type is GenerationMsgType.FAILURE:
            self.time = kwargs.get("time")

        elif msg_type is GenerationMsgType.MEAS_RES:
            self.protocol = kwargs.get("protocol")
            self.res = kwargs.get("res")
            self.time = kwargs.get("time")
            self.accepted_index = kwargs.get("accepted_index")
        elif msg_type is GenerationMsgType.RELEASE_BSM:
            self.protocol = kwargs.get("protocol")

        elif msg_type is GenerationMsgType.REQUEST_BSM:
            self.protocol = kwargs.get("protocol")

        elif msg_type is GenerationMsgType.BSM_ALLOCATE:
            self.protocol = kwargs.get("protocol")
        elif msg_type is GenerationMsgType.ENTANGLEMENT_SUCCESS:
            self.accepted_index = kwargs.get("accepted_index")

        else:
            raise Exception("EntanglementGeneration generated invalid message type {}".format(msg_type))


class EntanglementGenerationA(EntanglementProtocol):
    """Entanglement generation protocol for quantum router.

    The EntanglementGenerationA protocol should be instantiated on a quantum router node.
    Instances will communicate with each other (and with the B instance on a BSM node) to generate entanglement.

    Attributes:
        own (QuantumRouter): node that protocol instance is attached to.
        name (str): label for protocol instance.
        middle (str): name of BSM measurement node where emitted photons should be directed.
        other (str): name of distant QuantumRouter node, containing a memory to be entangled with local memory.
        memory (Memory): quantum memory object to attempt entanglement for.
    """
    
    # TODO: use a function to update resource manager

    _plus_state = [sqrt(1/2), sqrt(1/2)]
    _flip_circuit = Circuit(1)
    _flip_circuit.x(0)
    _z_circuit = Circuit(1)
    _z_circuit.z(0)


    def __init__(self, own: "Node", name: str, middle: str, other: str, memory: "Memory"):
        """Constructor for entanglement generation A class.

        Args:
            own (Node): node to attach protocol to.
            name (str): name of protocol instance.
            middle (str): name of middle measurement node.
            other (str): name of other node.
            memory (Memory): memory to entangle.
        """

        super().__init__(own, name)
        self.middle = middle
        self.other = other  # other node
        self.other_protocol = None  # other EG protocol on other node

        # memory info
        self.memory = memory

        self.memories = [memory]
        self.remote_memo_id = ""  # memory index used by corresponding protocol on other node

        # network and hardware info
        self.fidelity = memory.raw_fidelity
        self.qc_delay = 0
        self.expected_times = -1

        self.scheduled_events = []

        # misc
        self.primary = False  # one end node is the "primary" that initiates negotiation
        self.debug = False

        self.frequency = 2e3
        self.isSuccess = False

    def set_others(self, other: "EntanglementGenerationA") -> None:
        """Method to set other entanglement protocol instance.

        Args:
            other (EntanglementGenerationA): other protocol instance.
        """

        assert self.other_protocol is None
        assert self.fidelity == other.fidelity
        if other.other_protocol is not None:
            assert self == other.other_protocol
        self.other_protocol = other
        self.remote_memo_id = other.memories[0].name
        self.primary = self.own.name > self.other
        # print("primray is set")

    def start(self) -> None:
        """Method to start entanglement generation protocol.

        Will start negotiations with other protocol (if primary).

        Side Effects:
            Will send message through attached node.
        """
        
        log.logger.info(self.own.name + " protocol start with partner {}".format(self.other))
        # print("generatin between ", self.own.name, self.other)
        if self not in self.own.protocols:
            return
        
        # If the node is primary, start the entanglement by sending 1st request bsm message
        if self.primary:
            # print("request sent")
            message = EntanglementGenerationMessage(GenerationMsgType.REQUEST_BSM, None, protocol = self)
            self.own.send_message(self.middle, message)


    def emit_event(self) -> None:
        """Method to setup memory and emit photons.

        If the protocol is in round 1, the memory will be first set to the \|+> state.
        Otherwise, it will apply an x_gate to the memory.
        Regardless of the round, the memory `excite` method will be invoked.

        Side Effects:
            May change state of attached memory.
            May cause attached memory to emit photon.
        """
        # print("!!!!!!!!!!!!!!!! emit event", self.own.name)

        # Assign light sources
        self.own.lightsource.assign_middle(self.middle)
        self.own.lightsource.assign_memory(self.memory)

        # emit photons from lightsources
        # print("memory index is", self.memory.memory_array.memories.index(self.memory))
        self.own.lightsource.emit()

    def schedule_and_emit_event(self,  min_time) -> None:
        """Method to setup memory and emit photons.

        If the protocol is in round 1, the memory will be first set to the \|+> state.
        Otherwise, it will apply an x_gate to the memory.
        Regardless of the round, the memory `excite` method will be invoked.

        Side Effects:
            May change state of attached memory.
            May cause attached memory to emit photon.
        """
        # print("!!!!!!!!!!!!!!!! emit event", self.own.name)

        # Assign light sources
        self.own.lightsource.assign_middle(self.middle)
        self.own.lightsource.assign_memory(self.memory)

        # schedule a qubit 
        # print("memory index is", self.memory.memory_array.memories.index(self.memory))
        previous_time = self.own.schedule_qubit(self.middle, min_time)
        
        # emit the photon
        status = self.own.lightsource.emit()
        # print("emit status node:", self.own.name, "mamory:", self.memory.memory_array.memories.index(self.memory), "status:", status)

    def release_bsm(self):
        # Send release bsm message to the BSM
        message = EntanglementGenerationMessage(GenerationMsgType.RELEASE_BSM, None, protocol = self)
        self.own.send_message(self.middle, message)

    def received_message(self, src: str, msg: EntanglementGenerationMessage) -> None:
        """Method to receive messages.

        This method receives messages from other entanglement generation protocols.
        Depending on the message, different actions may be taken by the protocol.

        Args:
            src (str): name of the source node sending the message.
            msg (EntanglementGenerationMessage): message received.

        Side Effects:
            May schedule various internal and hardware events.
        """

        if src not in [self.middle, self.other]:
            return

        msg_type = msg.msg_type
        
        # If BSM has been allocated by the BSM
        if msg_type is GenerationMsgType.BSM_ALLOCATE:
            self.qc_delay = self.own.qchannels[self.middle].delay
            frequency = self.memory.frequency
            message = EntanglementGenerationMessage(GenerationMsgType.NEGOTIATE, self.other_protocol.name,
                                                    qc_delay=self.qc_delay, frequency=frequency)
            self.own.send_message(self.other, message)
            # print("BSM ALLOCATED, STARTING PROTOCOL")
       
        # Start negotiating generation parameters
        elif msg_type is GenerationMsgType.NEGOTIATE:
            # configure params
            another_delay = msg.qc_delay
            self.qc_delay = self.own.qchannels[self.middle].delay
            cc_delay = int(self.own.cchannels[src].delay)
            total_quantum_delay = max(self.qc_delay, another_delay)

            # get time for first excite event
            min_time = self.own.timeline.now() + total_quantum_delay - self.qc_delay + cc_delay
            previous_time = self.own.schedule_qubit(self.middle, min_time)
            # print("min_time:", min_time, "previous_time", previous_time)

            another_emit_time_0 = previous_time + self.qc_delay - another_delay
            message = EntanglementGenerationMessage(GenerationMsgType.NEGOTIATE_ACK, self.other_protocol.name,
                                                    emit_time_0=another_emit_time_0)
            self.own.send_message(src, message)

            # schedule emit
            #process = Process(self, "emit_event", [])
            #event = Event(previous_time, process)
            event = Event(previous_time, self, "emit_event", [])
            #self.own.timeline.schedule(event)
            self.own.timeline.schedule_counter += 1
            self.own.timeline.events.push(event)
            self.scheduled_events.append(event)

            # In a batch, schedule all qubits for forming entanglement
            for i in range(100):
                next_time = previous_time + int(1e12 / self.frequency)
                # print("time of ", i, "th emission at", self.own.name,"is :", next_time)
                #process = Process(self, "schedule_and_emit_event", [next_time])
                #event = Event(next_time, process)
                event = Event(next_time, self, "schedule_and_emit_event", [next_time])
                #self.own.timeline.schedule(event)
                self.own.timeline.schedule_counter += 1
                self.own.timeline.events.push(event)
                self.scheduled_events.append(event)
                previous_time = next_time


        elif msg_type is GenerationMsgType.NEGOTIATE_ACK:
            # configure params
            self.expected_times = msg.emit_time_0 + self.qc_delay

            if msg.emit_time_0 < self.own.timeline.now():
                msg.emit_time_0 = self.own.timeline.now()

            # schedule emit
            previous_time = self.own.schedule_qubit(self.middle, msg.emit_time_0)
            assert previous_time == msg.emit_time_0, "%d %d %d" % (emit_time_0, msg.emit_time_0, self.own.timeline.now())

            #process = Process(self, "emit_event", [])
            #event = Event(msg.emit_time_0, process)
            event = Event(msg.emit_time_0, self, "emit_event", [])
            #self.own.timeline.schedule(event)
            self.own.timeline.schedule_counter += 1
            self.own.timeline.events.push(event)
            self.scheduled_events.append(event)

            # In a batch, schedule all qubits for forming entanglement
            for i in range(100):
                next_time = previous_time + int(1e12 / self.frequency)
                # print("time of ", i, "th emission at", self.own.name,"is :", next_time)
                #process = Process(self, "schedule_and_emit_event", [next_time])
                #event = Event(next_time, process)
                event = Event(next_time, self, "schedule_and_emit_event", [next_time])
                #self.own.timeline.schedule(event)
                self.own.timeline.schedule_counter += 1
                self.own.timeline.events.push(event)
                self.scheduled_events.append(event)
                previous_time = next_time
            # print("PREVIOUS TIME WAS:", previous_time)

            # Let go of the BSM
            #process = Process(self, "release_bsm", [])
            #event = Event(next_time + int(1e12 / self.frequency), process)
            event = Event(next_time + int(1e12 / self.frequency), self, "release_bsm", [])
            #self.own.timeline.schedule(event)
            self.own.timeline.schedule_counter += 1
            self.own.timeline.events.push(event)
            self.scheduled_events.append(event)

        # When the BSM returns a measurement result
        elif msg_type is GenerationMsgType.MEAS_RES:
            if not self.isSuccess:
                # print("running entanglement success")
                self._entanglement_succeed(msg.accepted_index)
                self.isSuccess = True
                # print("primary Accepted index :", msg.accepted_index, "qmodes:", len(self.memory.qmodes))

                message = EntanglementGenerationMessage(GenerationMsgType.ENTANGLEMENT_SUCCESS, self.other_protocol.name, accepted_index = msg.accepted_index)
                self.own.send_message(self.other, message)

        # Success message received
        elif msg_type is GenerationMsgType.ENTANGLEMENT_SUCCESS:
            self._entanglement_succeed(msg.accepted_index)
            # print("secondary Accepted index :", msg.accepted_index, "qmodes:", len(self.memory.qmodes))
            self.isSuccess = True
            
        else:
            raise Exception("Invalid message {} received by EG on node {}".format(msg_type, self.own.name))

        return True

    def is_ready(self) -> bool:
        return self.other_protocol is not None

    def memory_expire(self, memory: "Memory") -> None:
        """Method to receive expired memories."""

        assert memory == self.memory

        self.update_resource_manager(memory, 'RAW')
        for event in self.scheduled_events:
            if event.time >= self.own.timeline.now():
                #self.own.timeline.remove_event(event)
                self.own.timeline.events.remove(event)
                

    def _entanglement_succeed(self, accepted_index):
        # print("!!!!!!!!!!!!!!!!!!!SUCCEEDED!!!!!!!!!!!!!!!!!!!!!!!!")
        log.logger.info(self.own.name + " successful entanglement of memory {}".format(self.memory))
        self.memory.entangled_memory["node_id"] = self.other
        self.memory.entangled_memory["memo_id"] = self.remote_memo_id
        self.memory.fidelity = self.memory.raw_fidelity
        self.memory.accepted_index = accepted_index

        self.update_resource_manager(self.memory, 'ENTANGLED')

    def _entanglement_fail(self):
        for event in self.scheduled_events:
            #self.own.timeline.remove_event(event)
            self.own.timeline.events.remove(event)
        log.logger.info(self.own.name + " failed entanglement of memory {}".format(self.memory))
        
        self.update_resource_manager(self.memory, 'RAW')


class EntanglementGenerationB(EntanglementProtocol):
    """Entanglement generation protocol for BSM node.

    The EntanglementGenerationB protocol should be instantiated on a BSM node.
    Instances will communicate with the A instance on neighboring quantum router nodes to generate entanglement.

    Attributes:
        own (BSMNode): node that protocol instance is attached to.
        name (str): label for protocol instance.
        others (List[str]): list of neighboring quantum router nodes
    """

    def __init__(self, own: "Node", name: str, others: List[str]):
        """Constructor for entanglement generation B protocol.

        Args:
            own (Node): attached node.
            name (str): name of protocol instance.
            others (List[str]): name of protocol instance on end nodes.
        """

        super().__init__(own, name)
        assert len(others) == 2
        self.own.protocols.append(self)
        self.others = others  # end nodes
        self.previous_detection_time = None
        self.frequency = int(1e12 / 2e2)
        self.accepted_indices = 0
        self.current_protocol = None
        self.reservations = []
        self.first_received = False


    def bsm_update(self, bsm: 'SingleAtomBSM', info: Dict[str, Any]):
        """Method to receive detection events from BSM on node.

        Args:
            bsm (SingleAtomBSM): bsm object calling method.
            info (Dict[str, any]): information passed from bsm.
        """

        res = info["res"]
        time = info["time"]
        # print("got photon at", time)
        resolution = self.own.bsm.resolution

        # If this is the first detection
        if self.previous_detection_time == None:
            self.first_received = True
            self.previous_detection_time = time
            return

        # If detection after intermediate cases of no detections from both sources
        elif not self.first_received and (time > (self.previous_detection_time + self.frequency)):
            self.first_received = True
            self.accepted_indices += (time - self.previous_detection_time) // self.frequency
            self.previous_detection_time = time
            return

        # Default case for first received photon
        elif not self.first_received:
            self.first_received = True
            self.accepted_indices += 1
            self.previous_detection_time = time
            return

        # if only one photon received in the window, entanglement success, send message
        elif time > self.previous_detection_time + self.frequency:
            # print("!!!!!!!!!!!!!!!Entanglement SUCESS!!!!!!!!!!!!!!!!!!!")
            for i, node in enumerate(self.others):
                # print("sneding accepted indices: ", self.accepted_indices)
                message = EntanglementGenerationMessage(GenerationMsgType.MEAS_RES, None, protocol = self.current_protocol, res=res, time=time,
                                                        accepted_index=self.accepted_indices)
                self.own.send_message(node, message)
                self.first_received = False

        # if 2 photons received, entnaglement failure, move to next one
        else:
            # print("!!!!!!!!!!!!!!!Entanglement FAILURE!!!!!!!!!!!!!!!!!!!")
            self.first_received = False
            self.accepted_indices += 1
            # print("Others are:", self.others, "present accepted index = ", self.accepted_indices)
            
    def received_message(self, src: str, msg: EntanglementGenerationMessage):
        msg_type = msg.msg_type

        # If new request comes for access to BSM, check if some process already blocking the BSM. 
        # if yes, append this process to self.reservations, else, allocate it right away. 
        if msg_type is GenerationMsgType.REQUEST_BSM:
            if len(self.reservations) == 0:
                message = EntanglementGenerationMessage(GenerationMsgType.BSM_ALLOCATE, None, protocol = msg.protocol)
                self.own.send_message(msg.protocol.own.name, message)
                self.current_protocol = msg.protocol
                # print("MESAGE SENT TO NODE")
            self.reservations.append(msg.protocol)
            # print("protocol appended: ", msg.protocol)

        # Once attempt to entanglement generation is complete, the BSM is released. Check if other process exist
        # in reservations queue. If yes, start one on top. Else, return 
        elif msg_type is GenerationMsgType.RELEASE_BSM:
            # print("protocol removed:", msg.protocol)
            self.reservations.remove(msg.protocol)
            self.accepted_indices = 0
            self.previous_detection_time = None
            if len(self.reservations) > 0:
                message = EntanglementGenerationMessage(GenerationMsgType.BSM_ALLOCATE, None, protocol = self.reservations[0])
                self.own.send_message(self.reservations[0].own.name, message)
                self.current_protocol = self.reservations[0]

    def start(self) -> None:
        pass

    def set_others(self, other: "EntanglementProtocol") -> None:
        pass

    def is_ready(self) -> bool:
        return True

    def memory_expire(self) -> None:
        raise Exception("EntanglementGenerationB protocol '{}' should not have memory_expire".format(self.name))