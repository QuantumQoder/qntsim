"""Definitions of node types.

This module provides definitions for various types of quantum network nodes.
All node types inherit from the base Node type, which inherits from Entity.
Node types can be used to collect all the necessary hardware and software for a network usage scenario.
"""

from math import inf
from time import monotonic_ns
from typing import TYPE_CHECKING, Any , List

if TYPE_CHECKING:
    from ..kernel.timeline import Timeline
    from ..message import Message
    from ..protocol import StackProtocol
    from ..resource_management.memory_manager import MemoryInfo
    from ..network_management.reservation import Reservation
    from ..components.optical_channel import QuantumChannel, ClassicalChannel
    from ..components.memory import Memory

from ..kernel.entity import Entity
from ..components.memory import MemoryArray
from ..components.bsm import SingleAtomBSM
from ..components.light_source import LightSource, SPDCSource2
from ..components.detector import QSDetectorPolarization, QSDetectorTimeBin
from ..resource_management.resource_manager import ResourceManager
from ..transport_layer.transport_manager import TransportManager
from ..network_management.network_manager import NewNetworkManager
from ..entanglement_management.generation import GenerationMsgType
from ..utils.encoding import *


class Node(Entity):
    """Base node type.
    
    Provides default interfaces for network.

    Attributes:
        name (str): label for node instance.
        timeline (Timeline): timeline for simulation.
        cchannels (Dict[str, ClassicalChannel]): mapping of destination node names to classical channel instances.
        qchannels (Dict[str, ClassicalChannel]): mapping of destination node names to quantum channel instances.
        protocols (List[Protocol]): list of attached protocols.
    """

    def __init__(self, name: str, timeline: "Timeline"):
        """Constructor for node.

        name (str): name of node instance.
        timeline (Timeline): timeline for simulation.
        """

        Entity.__init__(self, name, timeline)
        self.owner = self
        self.cchannels = {}  # mapping of destination node names to classical channels
        self.qchannels = {}  # mapping of destination node names to quantum channels
        self.protocols = []

    def init(self) -> None:
        pass

    def assign_cchannel(self, cchannel: "ClassicalChannel", another: str) -> None:
        """Method to assign a classical channel to the node.

        This method is usually called by the `ClassicalChannel.add_ends` method and not called individually.

        Args:
            cchannel (ClassicalChannel): channel to add.
            another (str): name of node at other end of channel.
        """

        self.cchannels[another] = cchannel

    def assign_qchannel(self, qchannel: "QuantumChannel", another: str) -> None:
        """Method to assign a quantum channel to the node.

        This method is usually called by the `QuantumChannel.add_ends` method and not called individually.

        Args:
            qchannel (QuantumChannel): channel to add.
            another (str): name of node at other end of channel.
        """

        self.qchannels[another] = qchannel

    def send_message(self, dst: str, msg: "Message", priority=inf) -> None:
        """Method to send classical message.

        Args:
            dst (str): name of destination node for message.
            msg (Message): message to transmit.
            priority (int): priority for transmitted message (default inf).
        """
        if priority == inf:
            priority = self.timeline.schedule_counter
        self.cchannels[dst].transmit(msg, self, priority)

    def receive_message(self, src: str, msg: "Message") -> None:
        """Method to receive message from classical channel.

        Searches through attached protocols for those matching message, then invokes `received_message` method of protocol(s).

        Args:
            src (str): name of node sending the message.
            msg (Message): message transmitted from node.
        """

        # signal to protocol that we've received a message
        print('node msg', msg)
        if msg.receiver is not None:
            for protocol in self.protocols:
                print('protocol', protocol)
                if protocol.name == msg.receiver and protocol.received_message(src, msg):
                    return
        else:
            matching = [p for p in self.protocols if type(p) == msg.protocol_type]
            for p in matching:
                p.received_message(src, msg)

    def schedule_qubit(self, dst: str, min_time: int) -> int:
        """Interface for quantum channel `schedule_transmit` method."""

        return self.qchannels[dst].schedule_transmit(min_time)

    def send_qubit(self, dst: str, qubit) -> None:
        """Interface for quantum channel `transmit` method."""
        #print(f'sent qubit from node: {self.name} to node: {dst}')
        # print((dst), type(qubit))
        # print("qchannels", self.qchannels)
        self.qchannels[dst].transmit(qubit, self)

    def receive_qubit(self, src: str, qubit) -> None:
        """Method to receive qubits from quantum channel (does nothing for this class)."""

        pass


class BSMNode(Node):
    """Bell state measurement node.

    This node provides bell state measurement and the EntanglementGenerationB protocol for entanglement generation.

    Attributes:
        name (str): label for node instance.
        timeline (Timeline): timeline for simulation.
        bsm (SingleAtomBSM): BSM instance object.
        eg (EntanglementGenerationB): entanglement generation protocol instance.
    """

    def __init__(self, name: str, timeline: "Timeline", other_nodes: List[str]) -> None:
        """Constructor for BSM node.

        Args:
            name (str): name of node.
            timeline (Timeline): simulation timeline.
            other_nodes (str): 2-member list of node names for adjacent quantum routers.
        """

        from ..entanglement_management.generation import EntanglementGenerationB
        Node.__init__(self, name, timeline)
        self.bsm = SingleAtomBSM("%s_bsm" % name, timeline)
        self.eg = EntanglementGenerationB(self, "{}_eg".format(name), other_nodes)
        self.bsm.attach(self.eg)

    def receive_message(self, src: str, msg: "Message") -> None:
        # signal to protocol that we've received a message
        print("protocols on bsm: ", self.protocols)
        for protocol in self.protocols:
            protocol.received_message(src, msg)
            # if type(protocol) == msg.owner_type:
            #     if protocol.received_message(src, msg):
            #         return

        # if we reach here, we didn't successfully receive the message in any protocol
        ##print(src, msg)
        # raise Exception("Unkown protocol")

    def receive_qubit(self, src: str, qubit):
        """Method to receive qubit from quantum channel.

        Invokes get method of internal bsm with `qubit` as argument.

        Args:
            src (str): name of node where qubit was sent from.
            qubit (any): transmitted qubit.
        """
        #print(f'optical_channel at node: {self.name}, recv qubit from {src}')
        self.bsm.get(qubit)

    def eg_add_others(self, other):
        """Method to addd other protocols to entanglement generation protocol.

        Args:
            other (EntanglementProtocol): other entanglement protocol instance.
        """

        self.eg.others.append(other.name)


class QuantumRouter(Node):
    """Node for entanglement distribution networks.

    This node type comes pre-equipped with memory hardware, along with the default SeQUeNCe modules (sans application).

    Attributes:
        name (str): label for node instance.
        timeline (Timeline): timeline for simulation.
        memory_array (MemoryArray): internal memory array object.
        resource_manager (ResourceManager): resource management module.
        network_manager (NetworkManager): network management module.
        map_to_middle_node (Dict[str, str]): mapping of router names to intermediate bsm node names.
        app (any): application in use on node.
    """

    def __init__(self, name, tl, memo_size=10):
        """Constructor for quantum router class.

        Args:
            name (str): label for node.
            tl (Timeline): timeline for simulation.
            memo_size (int): number of memories to add in the array (default 50).
        """

        Node.__init__(self, name, tl)
        self.memory_array = MemoryArray(name + ".MemoryArray", tl, num_memories=memo_size)
        self.memory_array.owner = self
        self.resource_manager = ResourceManager(self)
        self.network_manager = NewNetworkManager(self)
        self.transport_manager=TransportManager(self)
        self.map_to_middle_node = {}
        self.app = None
        self.lightsource = SPDCSource2(self, name, tl)
        #-------------------------------------
        self.all_pair_shortest_dist = None
        self.all_neighbor={}
        self.neighbors = None
        self.random_seed = None
        self.virtualneighbors=[]
        self.nx_graph=None
        self.delay_graph=None
        self.neighborhood_list=None
        self.marker=None
        #-------------------------------------

    #--------------------------------------------------------------------------
    def find_virtual_neighbors(self):
        virtual_neighbors = {}
        virtual_neighbor=[]
        #Check the memory of this node for existing entanglements
        for info in self.resource_manager.memory_manager:
            
            if info.state != 'ENTANGLED':
                continue
            else:
                ##print((node, info.remote_node))
                #This is a virtual neighbor
                #nx_graph.add_edge(node, str(info.remote_node), color='r')
                if str(info.remote_node) in virtual_neighbors.keys():
                    # print('remotre',info.remote_node,virtual_neighbors)
                    virtual_neighbors[str(info.remote_node)] = virtual_neighbors[str(info.remote_node)] + 1
                else:
                    virtual_neighbors[str(info.remote_node)] = 1
            # virtual_neighbor=[info.remote_node,self.name]
            # print('findvirtualneighbors',virtual_neighbors,self.name,info.remote_node)
        return virtual_neighbors
    #--------------------------------------------------------------------------

    def receive_message(self, src: str, msg: "Message") -> None:
        # print('receive msg', msg.receiver,msg.protocol_type)
        if msg.receiver == "resource_manager":
            self.resource_manager.received_message(src, msg)
        elif msg.receiver == "network_manager":
            self.network_manager.received_message(src, msg)
        elif msg.receiver == "transport_manager":
            self.transport_manager.received_message(src, msg)
        elif msg.msg_type == GenerationMsgType.MEAS_RES or msg.msg_type == GenerationMsgType.BSM_ALLOCATE:
            try:
                msg.protocol.received_message(src, msg)
                return
            except:
                pass 
        # else:
        if msg.receiver is None:
            matching = [p for p in self.protocols if type(p) == msg.protocol_type]
            # print('ms protocol type',msg.protocol_type)
            # for p in self.protocols:
            #     # print('type p',type(p))
            #     p.received_message(src, msg)
            # # print('matching', matching)
            for p in matching:
                p.received_message(src, msg)
            if msg.protocol_type == "TransportProtocolSrc":
                print()
                

        else:
            for protocol in self.protocols:
                if protocol.name == msg.receiver:
                    protocol.received_message(src, msg)
                    break

    def init(self):
        """Method to initialize quantum router node.

        Sets up map_to_middle_node dictionary.
        """

        super().init()
        for dst in self.qchannels:
            end = self.qchannels[dst].receiver
            if isinstance(end, BSMNode):
                for other in end.eg.others:
                    if other != self.name:
                        self.map_to_middle_node[other] = end.name

    def memory_expire(self, memory: "Memory") -> None:
        """Method to receive expired memories.

        Args:
            memory (Memory): memory that has expired.
        """

        self.resource_manager.memory_expire(memory)

    def reserve_net_resource(self, responder: str, start_time: int, end_time: int, memory_size: int,
                             target_fidelity: float) -> None:
        """Method to request a reservation.

        Args:
            responder (str): name of the node with which entanglement is requested.
            start_time (int): desired simulation start time of entanglement.
            end_time (int): desired simulation end time of entanglement.
            memory_size (int): number of memories requested.
            target_fidelity (float): desired fidelity of entanglement.
        """

        self.network_manager.request(responder, start_time, end_time, memory_size, target_fidelity)

    def get_idle_memory(self, info: "MemoryInfo") -> None:
        """Method for application to receive available memories."""

        if self.app:
            self.app.get_memory(info)

    def get_reserve_res(self, reservation: "Reservation", res: bool) -> None:
        """Method for application to receive reservations results."""

        if self.app:
            self.app.get_reserve_res(reservation, res)

    def get_other_reservation(self, reservation: "Reservation"):
        """Method for application to get another reservation."""

        if self.app:
            self.app.get_other_reservation(reservation)

