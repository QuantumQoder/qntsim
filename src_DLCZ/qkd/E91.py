import math
from enum import Enum, auto

import numpy

from ..message import Message
from ..protocol import StackProtocol
from ..kernel.event import Event
from ..kernel.process import Process




def pair_e91_protocols(sender: "E91", receiver: "E91") -> None:
    """Function to pair E91 protocol instances.

    Args:
        sender (E91): protocol instance sending qubits (Alice).
        receiver (E91): protocol instance receiving qubits (Bob).
    """
    print('pairedd',sender,receiver)
    sender.another = receiver
    receiver.another = sender
    sender.role = 0
    receiver.role = 1
    print('after pairedd',sender.role,receiver.role,sender.another,receiver.another)
class E91MsgType(Enum):
    " All possible message type for E91"
    BEGIN_ENTANGLEMENT=auto()
    BASIS_LIST=auto()
    MATCHING_INDICES=auto()

class E91Message(Message):
    """Message used by E91 protocols.

    This message contains all information passed between E91 protocol instances.
    Messages of different types contain different information.

    Attributes:
        msg_type (BB84MsgType): defines the message type.
        receiver (str): name of destination protocol instance.
        start_time (int): simulation start time of qubit pulse (if `msg_type == BEGIN_PHOTON_PULSE`).
        bases (List[int]): list of measurement bases (if `msg_type == BASIS_LIST`).
        indices (List[int]): list of indices for matching bases (if `msg_type == MATCHING_INDICES`).
    """
    def __init__(self, msg_type: E91MsgType, receiver: str, **kwargs):
        super().__init__(msg_type, receiver)
        self.owner_type = E91
        if self.msg_type is E91MsgType.BEGIN_ENTANGLEMENT:
           
            self.frequency = kwargs["frequency"]
            self.light_time = kwargs["light_time"]
            self.start_time = kwargs["start_time"]
            self.wavelength = kwargs["wavelength"]
            print('begin entanglement msg',self.wavelength)


class E91(StackProtocol):
    """Implementation of E91 protocol.

    The BB84 protocol uses entanglements to create a secure key between two QKD Nodes.

    Attributes:
        own (QKDNode): node that protocol instance is attached to.
        name (str): label for protocol instance.
        role (int): determines if instance is "alice" or "bob" node.
        working (bool): shows if protocol is currently working on a key.
        ready (bool): used by alice to show if protocol currently processing a generate_key request.
        basis_lists (List[int]): list of bases that qubits are sent in.
        bit_lists (List[int]): list of 0/1 qubits sent (in bases from basis_lists).
        key (int): generated key as an integer.
        key_bits (List[int]): generated key as a list of 0/1 bits.
        another (E91): other E91 protocol instance (on opposite node).
        key_lenghts (List[int]): list of desired key lengths.
        self.keys_left_list (List[int]): list of desired number of keys.
        self.end_run_times (List[int]): simulation time for end of each request.
    """

    def __init__(self, own: "QKDNode", name: str, role=-1):
        """Constructor for E91 class.

        Args:
            own (QKDNode): node hosting protocol instance.
            name (str): name of protocol instance.
        """
        super().__init__(own,name)
        self.role=role
        self.light_time = 0  # time to use laser (measured in s)
        self.ls_freq = 0  # frequency of light source
        self.working=False
        self.ready= True 
        self.basis_list=None
        self.key=0
        self.key_bits=None
        self.another=None
        self.key_lengths_list = []
        self.end_run_times = []
        self.key_lengths=[]
        self.latency= 0
        self.last_key_time = 0
        self.throughputs=[]
        self.error_rates = []


    def pop(self):

        assert 0

    def push(self, length: int, key_num, run_time=math.inf):
        """Method to receive requests for key generation.

        Args:
            length (int): length of key to generate.
            key_num (int): number of keys to generate.
            run_time (int): max simulation time allowed for key generation (default inf).

        Side Effects:
            Will potentially invoke `start_protocol` method to start operations.
        """

        if self.role != 0:
            raise AssertionError("generate key must be called from Alice")
        
        self.key_lengths.append(length)
        self.another.key_lengths.append(length)
        # self.keys_left_list.append(key_num)
        if self.ready is True:
            print('push true')
            self.ready = False
            self.working = True
            self.another.working = True
            self.start_protocol()

    def start_protocol(self) -> None:
        """Method to start protocol.

        When called, this method will begin the process of key generation.
        Parameters for hardware will be calculated, and a `begin_entanglement` method is scheduled.
        """
        print('inside start_protocol')
        if len(self.key_lengths) > 0:
            # reset buffers for self and another
            self.basis_lists = []
            self.another.basis_lists = []
            self.bit_lists = []
            self.another.bit_lists = []
            self.key_bits = []
            self.another.key_bits = []
            self.latency = 0
            self.another.latency = 0

            self.working = True
            self.another.working = True

            self.ls_freq = self.own.lightsource.frequency

            # calculate light time based on key length
            self.light_time = self.key_lengths[0] / (self.ls_freq * self.own.lightsource.mean_photon_num)
            print('wavelengths',self.own.lightsource.wavelength)
            self.start_time = int(self.own.timeline.now()) + round(self.own.cchannels[self.another.own.name].delay)
            message = E91Message(E91MsgType.BEGIN_ENTANGLEMENT, self.another.name,
                                  frequency=self.ls_freq, light_time=self.light_time,
                                  start_time=self.start_time, wavelength=self.own.lightsource.wavelength)
            self.own.send_message(self.another.own.name, message)


        process = Process(self, "begin_entanglement", [])
        event = Event(2e12, process)
        self.own.timeline.schedule(event)

    def begin_entanglement(self):
        """
        Method to start entanglement between the nodes
        """

        # print('Entanglement started',self.wavelength,self.another.own.name,self.own.timeline.now()*1e-12)
        # tm.request(node2,5e12,10,10e12,1,5e9)
        # self.own.transport_manager.request(self.another.own.name,2e12,10,10e12,1,2e12)
        # process=Process('self.own.transport_manager','request',[])
        # event=Event(3e12,process)
        # self.own.timeline.schedule(event)
        if self.working :
            # generate basis/bit list
            num_pulses = round(self.light_time * self.ls_freq)
            basis_list = numpy.random.choice([0, 1], num_pulses)
            bit_list = numpy.random.choice([0, 1], num_pulses)

            lightsource = self.own.lightsource
            spdcsource=self.own.spdcsource
            encoding_type = lightsource.encoding_type
            print('lightsource encoding type',spdcsource,lightsource,encoding_type)
            state_list = []
            for i, bit in enumerate(bit_list):
                state = (encoding_type["bases"][basis_list[i]])[bit]
                state_list.append(state)
            spdcsource.emit(state_list)
            

        print('state list',state_list)
        print('basis list',basis_list)
        print('bit list', bit_list)

        # self.start_time = self.own.timeline.now()
        # process = Process(self, "begin_entanglement", [])
        # event = Event(self.start_time + int(round(self.light_time * 1e12)), process)
        # self.own.timeline.schedule(event)


    def set_measure_basis_list(self):
        """
        Method to set the measurement basis list
        """

        print('set the measurement basis')

    def received_message(self, src: str, msg: "Message"):
        """Method to receive messages.

        Will perform different processing actions based on the message received.

        Args:
            src (str): source node sending message.
            msg (Message): message received.
        """

        print('recieved message')

    
    def set_keys(self):
        """Method to convert `bit_list` field (List[int]) to a single key (int)."""

        print('set keys')