from enum import Enum, auto
from math import inf
from collections import defaultdict

from aenum import Enum


class MsgRecieverType(Enum):

    PROTOCOL = auto()
    MANAGER = auto


class ManagerType(Enum):

    NetworkManager = auto()
    ResourceManager = auto()
    MemoryManager = auto()
    TransportManager = auto()
    VirtualLinkManager = auto()
    ReservationManager = auto()


class ProtocolType(Enum):

    TransportProtocol = auto()
    NewRoutingProtocol = auto()
    RoutingTableUpdateProtocol = auto()
    ResourceReservationProtocol = auto()
    EntanglementGenerationA = auto()
    # EntanglementGenerationB = auto()
    BBPSSW = auto()
    EntanglementSwapping = auto()
    # EntanglementSwappingB = auto()
    # extend_enum(EntanglementGenerationA, )

class MessageQueueHandler():

    def __init__(self,owner) -> None:
        
        self.owner=owner
        self.protocol_queue = {}
        self.manager_queue = {}

    def send_message(self, dst:str, msg, priority = inf):

        if priority == inf:
            priority = self.owner.timeline.schedule_counter
        self.owner.cchannels[dst].transmit(msg, self.owner, priority)
    
    def push_message(self, src, msg):
        
        # self.protocol_queue = defaultdict(tuple)
        # self.manager_queue = defaultdict(tuple)
        # print('push message', src, msg.receiver_type)

        if msg.receiver_type == MsgRecieverType.MANAGER:
            # self.manager_queue[msg.receiver.name]=[[msg],0]

            if msg.receiver.name in self.manager_queue.keys():
                self.manager_queue[msg.receiver.name].append([[msg],0])
            else:
                self.manager_queue[msg.receiver.name]=[[msg],0]

            if self.manager_queue[msg.receiver.name][1] == 0:
                if msg.receiver == ManagerType.TransportManager:
                    self.owner.transport_manager.received_message(src, msg)

                elif msg.receiver == ManagerType.ResourceManager:
                    self.owner.resource_manager.received_message(src, msg)
                
                elif msg.receiver == ManagerType.NetworkManager:
                    self.owner.network_manager.received_message(src, msg)
                
                elif msg.receiver == ManagerType.ReservationManager:
                    print('reservation manager', msg.kwargs['request'])
                    for reservation in self.owner.reservation_manager:
                        if reservation.request == msg.kwargs['request']:
                            reservation.receive_message(msg)
                            break


        if msg.receiver_type == MsgRecieverType.PROTOCOL:
            # print('Message receiver type',msg.receiver,msg.receiver)
            
            if msg.receiver in self.protocol_queue.keys():
                self.protocol_queue[msg.receiver].append([[msg],0])
            else:
                self.protocol_queue[msg.receiver]=[[msg],0]
            # print('Pahskdjask',self.protocol_queue[msg.receiver][0])
            if self.protocol_queue[msg.receiver][1] == 0:
                for protocol in self.owner.protocols:
                    # print('self protocols', self.owner.name, msg.receiver, protocol.name)
                    # if msg.receiver == 'EntanglementGenerationA':
                    #     print('ENtngl gen A received')
                    #     protocol.name=protocol.split('.')
                    #     if protocol.name[0] == msg.receiver.name:
                    #         protocol.received_message(src,msg)
                    if protocol.name == msg.receiver:
                        print(' Protocol match',self.owner.name,protocol.name,msg.receiver)
                        protocol.received_message(src,msg)
                        # self.protocol_queue[msg.receiver.name][1]=1
            # print('flag value',self.protocol_queue[msg.receiver][1])
        # print('Manager Queue',self.manager_queue)
        # print('Protocol Queue',self.protocol_queue)

        # for key,value in self.manager_queue.items():
        #     print('flag',value[1])
            

        # for key,value in self.protocol_queue.items():
        #     print('flag',value[1])
        #     if self.flag == 0:
        #         for protocol in self.owner.protocols:
        #             print('self protocols', self.owner.name, msg.receiver.name, protocol.name)
        #             if protocol.name == msg.receiver.name:
        #                 # print(' Protocol match',protocol.name,msg.receiver.name)
        #                 protocol.received_message(src,msg)

    # def protocol_is_over(self, protocol_id):
    #     if not self.protocol_queue:
    #         pass
    #     else:
    #         self.flag = 0

    #     pass

    # def manager_is_over(self, manager_id):
    #     print('Manager is over',manager_id.name)
    #     print()
    #     if manager_id.name in self.manager_queue:
    #         print('manager present')
    #         msg=self.manager_queue[manager_id.name][0]
    #         print('Manager over message',msg)
    #     else:
    #         self.manager_queue[manager_id.name][1]=0