"""Definition of the Network Manager.

This module defines the NetworkManager class, an implementation of the SeQUeNCe network management module.
Also included in this module is the message type used by the network manager and a function for generating network managers with default protocols.
"""
import itertools
from enum import Enum
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ..topology.node import QuantumRouter
    from ..protocol import StackProtocol
    from ..kernel.event import Event
    from ..kernel.process import Process


from ..message import Message
from .routing import StaticRoutingProtocol,NewRoutingProtocol,RoutingTableUpdateProtocol
from .reservation import ResourceReservationProtocol, ResourceReservationMessage, RSVPMsgType, Reservation
from ..transport_layer.transport_manager import TransportProtocol
from ..resource_management.resource_manager import ResourceManagerMsgType, ResourceManagerMessage
from ..kernel.event import Event
from ..kernel.process import Process


class NetworkManagerMessage(Message):
    """Message used by the network manager.

    Attributes:
        message_type (Enum): message type required by base message type.
        receiver (str): name of destination protocol instance.
        payload (Message): message to be passed through destination network manager.
    """

    def __init__(self, msg_type: Enum, receiver: str, payload: "Message"):
        Message.__init__(self, msg_type, receiver)
        self.payload = payload


class NetworkManager():
    """Network manager implementation class.

    The network manager is responsible for the operations of a node within a broader quantum network.
    This is done through a `protocol_stack` of protocols, which messages are passed and packaged through.

    Attributes:
        name (str): name of the network manager instance.
        owner (QuantumRouter): node that protocol instance is attached to.
        protocol_stack (List[StackProtocol]): network manager protocol stack.
    """
    id=itertools.count()
    def __init__(self, owner: "QuantumRouter", protocol_stack: "List[StackProtocol]"):
        """Constructor for network manager.

        Args:
            owner (QuantumRouter): node network manager is attached to.
            protocol_stack (List[StackProtocol]): stack of protocols to use for processing.
        """

        self.name = "network_manager"
        self.owner = owner
        self.protocol_stack = protocol_stack
        self.load_stack(protocol_stack)
        self.abort = False
        self.requests={}
        self.networkmap={}
        self.tp_id=None
        # self.net_id=next(self.id)

    def load_stack(self, stack: "List[StackProtocol]"):
        """Method to load a defined protocol stack.

        Args:
            stack (List[StackProtocol]): new protocol stack.
        """

        self.protocol_stack = stack
        if len(self.protocol_stack) > 0:
            self.protocol_stack[0].lower_protocols.append(self)
            self.protocol_stack[-1].upper_protocols.append(self)

    def push(self, **kwargs):
        """Method to receive pushes from lowest protocol in protocol stack.

        Will create message to send to another node.

        Keyword Args:
            msg (any): message to deliver.
            dst (str): name of destination node.
        """

        message = NetworkManagerMessage(Enum, "network_manager", kwargs["msg"])
        print('nm',self.owner.name,kwargs["dst"])
        self.owner.send_message(kwargs["dst"], message)

    def pop(self, **kwargs):
        """Method to receive pops from highest protocol in protocol stack.

        Will get reservation from message and attempt to meet it.

        Keyword Args:
            msg (any): message containing reservation.
        """

        msg = kwargs.get("msg")
        assert isinstance(msg, ResourceReservationMessage)
        reservation = msg.reservation
        if reservation.initiator == self.owner.name:
            if msg.msg_type == RSVPMsgType.APPROVE:
                # when the path has been approved, you check if the connection has been aborted
                # Get the path formed during path discovery
                self.owner.get_reserve_res(reservation, True)
                path = msg.path
                
                
                print("NETWORK MANAGER PATH: ", path,self.abort,reservation,reservation.start_time*1e-12)
                # If the path has been aborted
                if self.abort:
                    print("THIS CONNECTION GOT ABORTED",self.abort)
                    print(self.abort,self.preempted_reservation)

                    # create and send a message to all the nodes in the path that the connection has been aborted
                    msg = ResourceManagerMessage(ResourceManagerMsgType.ABORT, receiver = "resource_manager", protocol = None, reservation = self.preempted_reservation)
                    self.owner.resource_manager.received_message(self.owner.name, msg)
                    self.notify_nm('ABORT',msg.reservation.id,msg.reservation)
                    for i in path[1:]: 
                        self.owner.send_message(i, msg)
                    self.abort=False
                else:
                    # the connection is not aborted and we can move forward

                    # msg = ResourceManagerMessage(ResourceManagerMsgType.RESPONSE, receiver = "resource_manager", protocol = None, reservation = reservation)
                    # self.owner.resource_manager.received_message(self.owner.name, msg)

                    print('abort false')
                    
            else:
                self.owner.get_reserve_res(reservation, False)
        elif reservation.responder == self.owner.name:
            self.owner.get_other_reservation(reservation)

    def received_message(self, src: str, msg: "NetworkManagerMessage"):
        """Method to receive transmitted network reservation method.

        Will pop message to lowest protocol in protocol stack.

        Args:
            src (str): name of source node for message.
            msg (NetworkManagerMessage): message received.

        Side Effects:
            Will invoke `pop` method of 0 indexed protocol in `protocol_stack`.
        """
        # if the abort message is received, set the abort flag for the network manager and append the aborted connection to the preempted reservations
        if msg.msg_type == RSVPMsgType.ABORT:
            self.abort = True
            self.preempted_reservation = msg.reservation
            print("received a message to abort the connection")
            # self.notify_nm(status='ABORT')
            return

        self.protocol_stack[0].pop(src=src, msg=msg.payload)

    def request(self, responder: str, start_time: int, end_time: int, memory_size: int, target_fidelity: float,priority: int,tp_id: int) -> None:
    # def request(self, responder: str, start_time: int, end_time: int, memory_size: int, target_fidelity: float, ) -> None:
        """Method to make an entanglement request.

        Will defer request to top protocol in protocol stack.

        Args:
            responder (str): name of node to establish entanglement with.
            start_time (int): simulation start time of entanglement.
            end_time (int): simulation end time of entanglement.
            memory_size (int): number of entangledd memory pairs to create.
            target_fidelity (float): desired fidelity of entanglement.

        Side Effects:
            Will invoke `push` method of -1 indexed protocol in `protocol_stack`.
        """
        """
        reservation = Reservation(initiator,responder, start_time, end_time, memory_size, target_fidelity,isvirtual)
        #reqid=Reservation.id
        reqobj=reservation.Reservation()
        requests={'reqid':reqid,'reqobj':reqobj}
        print('aaa', requests)
        """
        # self.net_id=next(self.id)
        # self.abort=False
        self.tp_id=tp_id
        print('tpsid',self.tp_id)
        # self.notify_nm(tp_id=tp_id)
        self.protocol_stack[-1].push(responder, start_time, end_time, memory_size, target_fidelity,False, priority)#$$Shouldnt isvirtual be a _isvirtual?

    #Add notify method
    def notify_nm(self,status,ReqId,ResObj):
        
        # This method would receive notification from the reservation protocols about the status of the request.
        # Depending upon the nature of the status of the request it would propagate that message to the transport manager notify method.
        # 
        self.networkmap[ReqId]=[self.tp_id,status]
        # for ReqId,ResObj in self.requests.items():
        #     print('REqId',ReqId,self.tp_id,status,ResObj.isvirtual)
           
        #     print('nnwetwork map',self.networkmap)
        if ResObj.isvirtual:
            print('approved virtual link',self.owner.name,ResObj.responder)
            self.owner.virtualneighbors.append(ResObj.responder)
            self.owner.virtualneighbors=list(set(self.owner.virtualneighbors))
            print('virtual neighbours',self.owner.name,self.owner.virtualneighbors,self.owner.timeline.now()*1e-12)
        print('Network map',self.networkmap)
        for key,value in self.networkmap.items():
            print('id status',key , value[1])
            if value[1]== 'REJECT' or value[1]=='ABORT': # For reject and abort call notify of the transport manager
                fail_time=self.owner.timeline.now()
                # print('faileds',fail_time*1e-12,value[1])
                self.owner.transport_manager.notify_tm(fail_time,value[0],value[1])
            
                
        
        #call transport manager notify

    def createvirtualrequest(self, responder: str, start_time: int, end_time: int, memory_size: int, target_fidelity: float) -> None:#$$
        """Method to make an entanglement request.

        Will defer request to top protocol in protocol stack.

        Args:
            responder (str): name of node to establish entanglement with.
            start_time (int): simulation start time of entanglement.
            end_time (int): simulation end time of entanglement.
            memory_size (int): number of entangledd memory pairs to create.
            target_fidelity (float): desired fidelity of entanglement.

        Side Effects:
            Will invoke `push` method of -1 indexed protocol in `protocol_stack`.
        """

        self.protocol_stack[-1].push(responder, start_time, end_time, memory_size, target_fidelity, True,1)#$$
    


def NewNetworkManager(owner: "QuantumRouter") -> "NetworkManager":
    """Function to create a new network manager.

    Will create a network manager with default protocol stack.
    This stack inclused a reservation and routing protocol.

    Args:
        owner (QuantumRouter): node to attach network manager to.

    Returns:
        NetworkManager: network manager object created.
    """

    manager = NetworkManager(owner, [])
    "Commented code is the static Routing protocol"
    # routing = StaticRoutingProtocol(owner, owner.name + ".StaticRoutingProtocol", {})
    # rsvp = ResourceReservationProtocol(owner, owner.name + ".RSVP")
    # routing.upper_protocols.append(rsvp)
    # rsvp.lower_protocols.append(routing)
    # manager.load_stack([routing, rsvp])

    "Initializing our routing protocol"
    routing = NewRoutingProtocol(owner, owner.name + ".NewRoutingProtocol") 
    """Instance of new routing protocol"""
    routing_update=RoutingTableUpdateProtocol(owner,owner.name)     
    """
    Instance of routing update protocol that runs independently at regular time interval.
    """
    rsvp = ResourceReservationProtocol(owner, owner.name + ".RSVP")
    routing.upper_protocols.append(rsvp)
    rsvp.lower_protocols.append(routing)
    manager.load_stack([routing, rsvp])
    """
    To initiate the routing update protocol we create an event of routing update which
    calls the sendmessage of the RoutingTableUpdateProtocol in routing.py.
    """
    protocol_start_time=2e12
    process = Process(routing_update, "sendmessage",[])
    event = Event(protocol_start_time+owner.timeline.now(), process)
    owner.timeline.schedule(event)
    owner.protocols.append(routing_update)
    return manager
