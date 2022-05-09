from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from ..topology.node import QuantumRouter

from enum import Enum,auto
from ..message import Message
#from ..network_management.network_manager import NetworkManagerMessage
import networkx as nx
from ..resource_management.rule_manager import Rule
from ..kernel._event import Event
from ..entanglement_management.generation import EntanglementGenerationA
from ..entanglement_management.purification import BBPSSW
from ..entanglement_management.swapping import EntanglementSwappingA, EntanglementSwappingB
import itertools
import json
import math



class Request():


    newid=itertools.count()
    def __init__(self, initiator:str,responder: str, start_time: int, end_time: int, memory_size: int, target_fidelity: float,priority: int,tp_id: int):
        
        self.initiator  = initiator
        self.responder  = responder
        self.start_time = start_time
        self.end_time = end_time
        self.memory_size=memory_size
        self.fidelity = target_fidelity
        self.priority=priority
        self.tp_id=tp_id
        self.path=[] #doubly linked list of Nodes (List(Nodes))
        self.pathnames=[]
        self.isvirtual=False
        self.id=next(self.newid)




class RoutingProtocol():
    
    def __init__(self, node: "Node", initiator:str,responder: str,temp_path:"[List(Node)]",marker:"Node"):
        """Constructor for routing protocol.

        Args:
            own (Node): node protocol is attached to.
            name (str): name of protocol instance.
            
            def __init__(self, own: "Node", name: str):
        
        """
        self.local_neighbor_table={} 
        self.node=node
        self.src=initiator
        self.dst=responder
        self.temp_path=temp_path
        self.marker=marker

    def setattributes(self,curr_node):
        '''Method to set the local neighborhood, distances, physical graphs and virtual link information'''
        
        """
        nodewise_dest_distance: dictionary of distance of a node with other nodes of the topology
        neighbors,vneighbors and nx_graph are attributes of node class.
        """

        all_pair_path = self.node.all_pair_shortest_dist
        all_pair_path=json.loads(json.dumps(all_pair_path))
        nodewise_dest_distance = all_pair_path[curr_node]
        nodewise_dest_distance = json.loads(json.dumps(nodewise_dest_distance))
        neighbors = self.node.neighbors
        vneighbors=self.node.virtualneighbors
        # print('virtual neighbors',vneighbors,self.own.timeline.now()*1e-12)
        G=self.node.nx_graph
        # print('nx graph',self.own.nx_graph)
        """
        The code below is used to populate local_neighbor_table.
        We iterate through the neighbors of node. If that node exist in the nodewise_dest_distance, if it a virtual link we assign distance as 0, else we assign the distance from the nodewise_dest_distance between those nodes.
        """
        for n_nodes in neighbors:
            key=self.node.name
            for node,dist in nodewise_dest_distance.items():  
                if n_nodes==node:  
                    if node in vneighbors:
                        self.local_neighbor_table.setdefault(key,{})[node]=0
                        G.add_edge(key,node,color='red',weight=dist)
                    else:    
                        self.local_neighbor_table.setdefault(key,{})[node]=dist
                    break  

    def tempnexthop(self):
        
        #Compute the next hop here using our logic
        #Pick the best possible nieghbor according to physical distance
        # print('--------------self.own.name------------', self.own.name,self.own.neighborhood_list)
        


        assert self.dst != self.node.name
        self.setattributes(self.node.name)
        
        G=self.node.nx_graph
        skip=[]
        if self.node.name == self.src:
            path=nx.dijkstra_path(G,self.node.name,self.dst) 
            '''We initially calculate the temporary path using Dijkstra's algorithm.'''
            ''' We append this temporary path to message class temporary path'''
            self.temp_path=path
               
            '''
                Marker node: The end node of the the local neighborhood which lies in the temp path.
                We iterate through the temp path, then through the neighborhood_list, and check if the node in the temp path lies in the neighborhood_list.
                we add this marker node to the msg.
            '''
            print("neighbour list of 1st node ",self.node.neighborhood_list)
            for items in self.temp_path:
                self.marker=items
                if self.node.neighborhood_list:
                    for nodes in self.node.neighborhood_list:
                        if nodes==items:

                            self.marker=nodes
            #self.own.send_message(path[1],msg)
            print("marker nodes",self.marker)   
        indexx=self.temp_path.index(self.node.name)
        # print('indx',self.own.name,indexx,len(msg.temp_path))

        # If the node is the first node in the temp path, we run the next_hop method, which gives us the next node using Djisktr's algorithm
            
        if self.node.name == self.temp_path[0]:
            dst=self.nexthop(self.node.name,self.temp_path[-1])
            print("dst 1",dst)
                
        # If the node is the marker node we do the routing again by calling next_hop method
        elif self.node.name ==self.marker:
            # print('At marker node',self.own.name,self.own.marker)
            dst=self.nexthop(self.node.name,self.temp_path[-1])
            print("dst 2",dst)

            #If the node is not the source, marker or end node, we skip the routing.
        elif indexx > 0 and indexx < len(self.temp_path)-1:
            dst=self.temp_path[indexx+1]
            print("dst 3",dst)
            # print('mddle',self.own.name,dst,indexx)
                
        #For end node
        elif indexx==len(self.temp_path)-1:
            # print('last node')
            dst=self.temp_path[-1]
            print("dst 4",dst)
        return dst
                
        
       
    def nexthop(self,src,dest):
        # This function will give the next hop of the Dijkstra's path.

        G=self.node.nx_graph
        path=nx.dijkstra_path(G,src,dest)
        # print('dijkstas path',path,path[1],path[-1])
      
        return path[1]

    def next_hop(self):

        # This function will give the next hop of the Dijkstra's path.
        if (self.node.name==self.dst):
            pass
        print("node",self.node.name)
        G=self.node.nx_graph
        path=nx.dijkstra_path(G,self.src,self.dst)
        print("path" ,path)
        index=path.index(self.node.name)
        print(path[index+1])
        return path[index+1]

        # print('dijkstas path',path,path[1],path[-1])
      


class RRPMsgType(Enum):
    """Defines possible message types for the reservation protocol."""

    RESERVE = auto()
    CREATE_TASKS = auto()
    FAIL = auto()
    #ABORT = auto()
    #SKIP_ROUTING=auto()
    


class RRMessage(Message):
    """Message used by resource reservation protocol.

    This message contains all information passed between reservation protocol instances.
    Messages of different types contain different information.

    Attributes:
        msg_type (GenerationMsgType): defines the message type.
        receiver (str): name of destination protocol instance.
        reservation (Reservation): reservation object relayed between nodes.
        qcaps (List[QCaps]): cumulative quantum capacity object list (if `msg_type == REQUEST`)
        path (List[str]): cumulative node list for entanglement path (if `msg_type == APPROVE`)
    """

    def __init__(self, msg_type: any, receiver: str,request:"Request"):
        Message.__init__(self, msg_type, receiver )
        self.payload = request
        self.temp_path=None
        self.marker=None
        

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

class MemoryTimeCard():
    """Class for tracking reservations on a specific memory.

    Attributes:
        memory_index (int): index of memory being tracked (in memory array).
        reservations (List[Reservation]): list of reservations for the memory.
    """

    def __init__(self, memory_index: int):
        """Constructor for time card class.

        Args:
            memory_index (int): index of memory to track.
        """

        self.memory_index = memory_index
        self.reservations = []
    def has_virtual_reservation(self):
        for res in self.reservations:
            if res.isvirtual:
                return True
        return False


class ReservationProtocol():     #(Protocol): 

    def __init__(self,node:"QuantumRouter",request:"Request",routing:"Routing"):
        
        self.node=node
        self.request = request
        self.routing = routing
        #self.node=Node
        self.vmemorylist=self.node.vmemory_list
        self.accepted_reservation=[]
        self.es_succ_prob = 1
        self.es_degradation = 0.95

    def create_rules(self, path: List[str], reservation: "Request") -> List["Rule"]:
        """Method to create rules for a successful request.

        Rules are used to direct the flow of information/entanglement in the resource manager.

        Args:
            path (List[str]): list of node names in entanglement path.
            reservation (Reservation): approved reservation.

        Returns:
            List[Rule]: list of rules created by the method.
        """
        
        rules = []
        # print('Reservation------', reservation.initiator, reservation.responder)
        self.node.resource_manager.rule_manager.rules = []
        # print(f'Rules for this node: {self.own.name} are {len(self.own.resource_manager.rule_manager.rules)}')
        memory_indices = []
        virtual_indices = []
        memory_indices_occupied = []
        last_virtual_index = -1
        memories_indices_free=[]

        for card in self.vmemorylist:
            #print("1")
            #print('111111', card)
            if reservation in card.reservations:
                memory_indices.append(card.memory_index)
                # print("To maintain the virtual link indices")
                if card.has_virtual_reservation() and not reservation.isvirtual:
                    virtual_indices.append(card.memory_index)
                    if card.memory_index > last_virtual_index:
                        last_virtual_index= card.memory_index
                # elif card.has_virtual_reservation() and reservation.isvirtual:
                #     print('Another virtual request arrived')
                
                    
                    
        # print('last_virtual_index', last_virtual_index)        

        # create rules for entanglement generation
        # print('Current node in Entanglement generation', self.own.name)
        index = path.index(self.node.name)
        # print('Path--------', path)
        print('Reservation------', reservation.initiator, reservation.responder)
        if index > 0:
            #print(f"index>0:{index}")
            #To accept virtual links, we skip the generation step when a non physical neighbor is found
            if path[index - 1] in self.node.neighbors:
                #print("###",self.own.name)
                #This will run for all nodes barring starting node
                def eg_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                    
                    
                    """if manager.resource_manager.owner.name == 'd' and memory_info.index == 1:
                        #print('EG for node: ', manager.resource_manager.owner.name)
                        #print('memory_info.state ', memory_info.state)
                        #print('memory_info.index: ', memory_info.index)
                        #print('memory_indices[last_virtual_index + 1 : last_virtual_index + reservation.memory_size + 1]: ', memory_indices[last_virtual_index + 1 : last_virtual_index + reservation.memory_size + 1])
                        #print('reservation.memory_size', reservation.memory_size)
                    """
                    #memory_list = memory_indices[:reservation.memory_size]
                    #if index < len(path) - 1 and path[index + 1] not in self.own.neighbors:
                    #    memory_list.append(reservation.memory_size)                    

                    memories_indices_free = [x for x in memory_indices if x not in virtual_indices]

                    #if memory_info.state == "RAW" and memory_info.index in memory_indices[:reservation.memory_size]:
                    #begin, end = last_virtual_index + 1 , (last_virtual_index+1) + reservation.memory_size
                    if memory_info.state == "RAW" and memory_info.index in memory_indices[last_virtual_index + 1 : last_virtual_index + reservation.memory_size + 1]:
                        #Check for node B's memory
                        """#print('self.own.name here is : ', self.own.name)
                        if self.own.name == 'd':
                            #print(f'In rule condition for Entanglement Generation  at node e for d')
                            #print('memory_info.index: ', memory_info.index)
                            #print('memory_info.state: ', memory_info.state)
                            #print('memory_info.remote_node: ', memory_info.remote_node)
                        """
                        return [memory_info]
                    else:
                        return []

                def eg_rule_action(memories_info: List["MemoryInfo"]):
                    # print('Current node in eg_ruleaction for index>0', self.own.name)
                    memories = [info.memory for info in memories_info]
                    memory = memories[0]
                    mid = self.node.map_to_middle_node[path[index - 1]]
                    # print('---------EntanglementGenerationA----------for pair: ', (self.own.name, path[index - 1]))
                    ##print('---------Middle node for this----------', mid)
                    protocol = EntanglementGenerationA(None, "EGA." + memory.name, mid, path[index - 1], memory)
                    return [protocol, [None], [None]]
                

                rule = Rule(10, eg_rule_action, eg_rule_condition)
                rules.append(rule)

            #memory_indices_occupied=memory_indices_occupied.append(memories_indices_free)
            #memories_indices_free = [x for x in memory_indices if x not in memory_indices_occupied]
        if index < len(path) - 1:
            print(f"index<<{index}")
            #To accept virtual links, we skip the generation step when a non physical neighbor is found
            if path[index + 1] in self.node.neighbors:
                #Starting node
                print("####",self.node.name)
                if index == 0:
                    # print("index=0")
                    def eg_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                        if memory_info.state == "RAW" and memory_info.index in memory_indices:
                            return [memory_info]
                        else:
                            return []
                #second to second last node
                else:
                    print("index!=0")
                    def eg_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                       
                        memories_indices_free = [x for x in memory_indices if x not in memory_indices_occupied]
                        """
                        if self.own.name == 'd':
                                #print(f'In rule condition for Entanglement Generation  at node d for e')
                                #print('memory_info.index: ', memory_info.index)
                                #print('memory_info.state: ', memory_info.state)
                                #print('memory_info.remote_node: ', memory_info.remote_node)
                                #print('last_virtual_index, reservation.memory_size: ',last_virtual_index, reservation.memory_size)
                                #print('acceptable indexes: ', memory_indices[last_virtual_index + reservation.memory_size:])
                        """
                        # print(f'free memory indices of {self.own.name}', memories_indices_free)
                        #if memory_info.state == "RAW" and memory_info.index in memory_indices[reservation.memory_size:]:
                        if memory_info.state == "RAW" and memory_info.index in memory_indices[(last_virtual_index+1) + reservation.memory_size:]:
                            #Check for node B's memory
                            #print('self.own.name here is : ', self.own.name)
                            """
                            #print(f'In rule condition for Entanglement Generation  at node {self.own.name}')
                            #print('memory_info.index: ', memory_info.index)
                            #print('memory_info.state: ', memory_info.state)
                            #print('memory_info.remote_node: ', memory_info.remote_node)
                            """
                            
                            return [memory_info]
                        else:
                            return []

                def eg_rule_action(memories_info: List["MemoryInfo"]):
                    def req_func(protocols):
                        for protocol in protocols:
                            if isinstance(protocol,
                                          EntanglementGenerationA) and protocol.other == self.node.name and protocol.rule.get_reservation() == reservation:
                                return protocol
                    
                    print('Current node in eg_ruleaction for indexnot > 0', self.node.name)
                    memories = [info.memory for info in memories_info]
                    memory = memories[0]
                    #memory = memories[-1]
                    mid = self.node.map_to_middle_node[path[index + 1]]
                    # print('1---------EntanglementGenerationA----------for pair: ', (self.own.name, path[index + 1]))
                    ##print('---------Middle node for this---------- ', mid)
                    protocol = EntanglementGenerationA(None, "EGA." + memory.name, mid, path[index + 1], memory)
                    return [protocol, [path[index + 1]], [req_func]]
                print('---------EntanglementGenerationA----------for pair: ', (self.node.name, path[index + 1]))
                rule = Rule(10, eg_rule_action, eg_rule_condition)
                rules.append(rule)
        # print('last_virtual_index', last_virtual_index)
        ##print(f'For {self.own.name}: --- len(rules): {len(rules)}')


        # create rules for entanglement purification
        if index > 0:
            # print("adding rules for purification")
            def ep_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                #if (memory_info.index in memory_indices[:reservation.memory_size]

                if (memory_info.index in memory_indices[last_virtual_index + 1 : last_virtual_index + reservation.memory_size + 1]):
                    # print("purification index satisified")
                    if memory_info.state == "ENTANGLED":
                        # print("memory info state satisfied")
                        # print("memory fidelity is", memory_info.fidelity, "reservation fidelity:", reservation.fidelity)
                        if memory_info.fidelity < reservation.fidelity:
                            # print("fidelity satisfied")
                    # print("memories found")
                            for info in manager:
                                #if (info != memory_info and info.index in memory_indices[:reservation.memory_size]
                                if (info != memory_info and info.index in memory_indices[last_virtual_index + 1 : last_virtual_index + reservation.memory_size + 1]
                                        and info.state == "ENTANGLED" and info.remote_node == memory_info.remote_node
                                        and info.fidelity == memory_info.fidelity):
                                    assert memory_info.remote_memo != info.remote_memo
                                    return [memory_info, info]
                # else:
                #     print("no memories found")
                return []

            def ep_rule_action(memories_info: List["MemoryInfo"]):
                memories = [info.memory for info in memories_info]

                def req_func(protocols):
                    _protocols = []
                    for protocol in protocols:
                        if not isinstance(protocol, BBPSSW):
                            continue

                        if protocol.kept_memo.name == memories_info[0].remote_memo:
                            _protocols.insert(0, protocol)
                        if protocol.kept_memo.name == memories_info[1].remote_memo:
                            _protocols.insert(1, protocol)

                    if len(_protocols) != 2:
                        return None

                    protocols.remove(_protocols[1])
                    _protocols[1].rule.protocols.remove(_protocols[1])
                    _protocols[1].kept_memo.detach(_protocols[1])
                    _protocols[0].meas_memo = _protocols[1].kept_memo
                    _protocols[0].memories = [_protocols[0].kept_memo, _protocols[0].meas_memo]
                    _protocols[0].name = _protocols[0].name + "." + _protocols[0].meas_memo.name
                    _protocols[0].meas_memo.attach(_protocols[0])
                    _protocols[0].t0 = _protocols[0].kept_memo.timeline.now()

                    return _protocols[0]

                name = "EP.%s.%s" % (memories[0].name, memories[1].name)
                protocol = BBPSSW(None, name, memories[0], memories[1])
                dsts = [memories_info[0].remote_node]
                req_funcs = [req_func]
                return protocol, dsts, req_funcs

            rule = Rule(10, ep_rule_action, ep_rule_condition)
            rules.append(rule)

        if index < len(path) - 1:
            if index == 0:
                def ep_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                    if (memory_info.index in memory_indices
                            and memory_info.state == "ENTANGLED" and memory_info.fidelity < reservation.fidelity):
                        return [memory_info]
                    return []
            else:
                def ep_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                    if (memory_info.index in memory_indices[reservation.memory_size:]
                    #if (memory_info.index in memory_indices[last_virtual_index + reservation.memory_size:]
                            and memory_info.state == "ENTANGLED" and memory_info.fidelity < reservation.fidelity):
                        return [memory_info]
                    return []

            def ep_rule_action(memories_info: List["MemoryInfo"]):
                memories = [info.memory for info in memories_info]
                name = "EP.%s" % (memories[0].name)
                protocol = BBPSSW(None, name, memories[0], None)
                return protocol, [None], [None]

            rule = Rule(10, ep_rule_action, ep_rule_condition)
            rules.append(rule)

        
        print(f'For {self.node.name}: --- len(rules): {len(rules)}')


        # create rules for entanglement swapping
        def es_rule_actionB(memories_info: List["MemoryInfo"]):
            memories = [info.memory for info in memories_info]
            memory = memories[0]
            protocol = EntanglementSwappingB(None, "ESB." + memory.name, memory)
            return [protocol, [None], [None]]

        # print('Current node in Swapping', self.own.name)
        if index == 0:
            def es_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                #if self.own.name == 'h' and memory_info.state == "ENTANGLED":
                    #print('memory_info.index', memory_info.index)
                    #print('memory_info.remote_node', memory_info.remote_node)
                    #print('path[-1]', path[-1])
                    #print('path', path)

                if (memory_info.state == "ENTANGLED"
                        and memory_info.index in memory_indices
                        and memory_info.remote_node != path[-1]
                        #and memory_info.remote_node == path[index+1]
                        and memory_info.fidelity >= reservation.fidelity):
                    
                    return [memory_info]
                else:
                    return []

            rule = Rule(10, es_rule_actionB, es_rule_condition)
            rules.append(rule)

        elif index == len(path) - 1:
            def es_rule_condition(memory_info: "MemoryInfo", manager: "MemoryManager"):
                #if self.own.name == 'h' and memory_info.state == "ENTANGLED":
                    #print('memory_info.index', memory_info.index)
                    #print('memory_info.remote_node', memory_info.remote_node)
                    #print('path[0]', path[0])
                    #print('path', path)

                if (memory_info.state == "ENTANGLED"
                        and memory_info.index in memory_indices
                        and memory_info.remote_node != path[0]
                        #and memory_info.remote_node == path[index-1]
                        and memory_info.fidelity >= reservation.fidelity):
                    return [memory_info]
                else:
                    return []

            rule = Rule(10, es_rule_actionB, es_rule_condition)
            rules.append(rule)

        else:
            _path = path[:]
            ##print('In middle node for entanglement swapping: ', self.own.name)
            while _path.index(self.node.name) % 2 == 0:
                ##print('Inside new path loop for : ', self.own.name)
                ##print("Path inside reservation---------",_path)
                ##print('_path.index(self.own.name): ' , _path.index(self.own.name))
                new_path = []
                for i, n in enumerate(_path):
                    if i % 2 == 0 or i == len(_path) - 1:
                        new_path.append(n)
                ##print('new_path: ', new_path)
                _path = new_path
            _index = _path.index(self.node.name)
            ##print('new path: ', _path)
            ##print('value of _index at mid swap node: ', _index)
            left, right = _path[_index - 1], _path[_index + 1]
            ##print('(left, right)', (left, right))

            def es_rule_conditionA(memory_info: "MemoryInfo", manager: "MemoryManager"):
                ##print("Node---",)
                ##print("STATE",memory_info.state)
                ##print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
                #for info in [memory_info]:
                #    #print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                #                         str(info.fidelity), str(info.entangle_time * 1e-12)))
                ##print("INDEX,REMOTE NODE,FIDELITY, RESERVATION FIDELITY ",memory_info.index,memory_info.remote_node,memory_info.fidelity,reservation.fidelity)
                                
                #print('enter ESA condition check')
                # print('Current node in Rule conditionA', self.own.name)
                # print('memory_info.remote_node : ', memory_info.remote_node)
                # print('memory_info.state : ', memory_info.state)
                # if memory_info.remote_node == 'v2':
                #     print('condition values for v2------')
                #     print('memory_info.state == "ENTANGLED" ', memory_info.state == "ENTANGLED")
                #     print('memory_info.index in memory_indices ', memory_info.index in memory_indices)
                #     print('memory_info.remote_node == left ', memory_info.remote_node == left)
                #     print('memory_info.fidelity >= reservation.fidelity ', memory_info.fidelity >= reservation.fidelity)
                #     print('Ends------')

                # if memory_info.remote_node == 'v1':
                #     print('condition values for v1------')
                #     print('memory_info.state == "ENTANGLED" ', memory_info.state == "ENTANGLED")
                #     print('memory_info.index in memory_indices ', memory_info.index in memory_indices)
                #     print('memory_info.remote_node == right ', memory_info.remote_node == right)
                #     print('memory_info.fidelity >= reservation.fidelity ', memory_info.fidelity >= reservation.fidelity)
                #     print('Ends------')
                
                # print('Remote node : ', memory_info.remote_node)
                #if ((memory_info.state == "ENTANGLED" or memory_info.state == "OCCUPIED")
                if (memory_info.state == "ENTANGLED"
                        and memory_info.index in memory_indices
                        and memory_info.remote_node == left
                        and memory_info.fidelity >= reservation.fidelity):
                    # print('gets in left if')
                    for info in manager:
                        """#print('info.remote_node: ', info.remote_node)
                        if info.remote_node == 'e':
                            #print('condition values for E------')
                            #print('info.state == "ENTANGLED" ', info.state == "ENTANGLED")
                            #print()
                            #print()
                            #print('info.index: ', info.index)
                            #print('memory_indices: ', memory_indices)
                            #print('info.index in memory_indices ', info.index in memory_indices)
                            #print('info.remote_node == right ', info.remote_node == right)
                            #print('info.fidelity >= reservation.fidelity ', info.fidelity >= reservation.fidelity)
                            #print('info.fidelity: ', info.fidelity)
                            #print('reservation.fidelity: ', reservation.fidelity)
                            #print()
                            #print()
                            #print('Ends------')
                        """
                        #if ((info.state == "ENTANGLED" or info.state == "OCCUPIED")
                        if (info.state == "ENTANGLED"
                                and info.index in memory_indices
                                and info.remote_node == right
                                and info.fidelity >= reservation.fidelity):
                            ##print("ES Condition matched A in IF----",self.own.name)
                            ##print("(PAIR OF NODES)",(left,right))
                            # print('gets in left of right')
                            return [memory_info, info]
                    
                #elif ((memory_info.state == "ENTANGLED" or memory_info.state == "OCCUPIED")
                if (memory_info.state == "ENTANGLED"
                      and memory_info.index in memory_indices
                      and memory_info.remote_node == right
                      and memory_info.fidelity >= reservation.fidelity):
                    # print('gets in right if')
                    for info in manager:
                        """if info.remote_node == 'a' and memory_info.remote_node == 'e':
                            #print('info.state == "ENTANGLED" ' , info.state == "ENTANGLED")
                            #print('info.index in memory_indices ', info.index in memory_indices)
                            #print('info.remote_node == left ', info.remote_node == left)
                            #print('info.fidelity >= reservation.fidelity ', info.fidelity >= reservation.fidelity)
                        """
                        #if ((info.state == "ENTANGLED" or info.state == "OCCUPIED")
                        if (info.state == "ENTANGLED"
                                and info.index in memory_indices
                                and info.remote_node == left
                                and info.fidelity >= reservation.fidelity):
                            """#print('memory_info.remote_node : ', memory_info.remote_node)
                            #print('info.remote_node : ', info.remote_node)
                            #print("ES Condition matched A in ELIF----",self.own.name)
                            #print("(PAIR OF NODES)",(left,right))
                            """
                            # print('gets in right of left')
                            return [memory_info, info]
                """else:
                    for info in manager:
                        #print("This else")
                        return [memory_info, info]"""
                # print("ES Condition in A failed----",self.own.name)
                # print("(PAIR OF NODES)",(left,right))
                return []

            def es_rule_actionA(memories_info: List["MemoryInfo"]):
                memories = [info.memory for info in memories_info]

                def req_func1(protocols):
                    for protocol in protocols:
                        if (isinstance(protocol, EntanglementSwappingB)
                                and protocol.memory.name == memories_info[0].remote_memo):
                            return protocol

                def req_func2(protocols):
                    for protocol in protocols:
                        if (isinstance(protocol, EntanglementSwappingB)
                                and protocol.memory.name == memories_info[1].remote_memo):
                            return protocol

                protocol = EntanglementSwappingA(None, "ESA.%s.%s" % (memories[0].name, memories[1].name),
                                                 memories[0], memories[1],
                                                 success_prob=self.es_succ_prob, degradation=self.es_degradation)
                dsts = [info.remote_node for info in memories_info]
                req_funcs = [req_func1, req_func2]
                return protocol, dsts, req_funcs
            ##print("Node---",self.own.name)
            ##print("Index A:\tEntangled Node A:\tFidelity A:\tEntanglement Time A:")
            #for info in self.own.resource_manager.memory_manager:
            #    #print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
            #                             str(info.fidelity), str(info.entangle_time * 1e-12)))
            rule = Rule(10, es_rule_actionA, es_rule_conditionA)
            rules.append(rule)

            def es_rule_conditionB(memory_info: "MemoryInfo", manager: "MemoryManager") -> List["MemoryInfo"]:
                ##print("Node---", self.own.name)
                ##print("In RULE B")
                ##print("STATE",memory_info.state)

                

                if (memory_info.state == "ENTANGLED"
                        and memory_info.index in memory_indices
                        and memory_info.remote_node not in [left, right]
                        and memory_info.fidelity >= reservation.fidelity):
                    ##print("Node---",self.own.name)
                    ##print("Index B:\tEntangled Node:\tFidelity:\tEntanglement Time:")
                    #for info in self.own.resource_manager.memory_manager:
                    #    #print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                    #                                str(info.fidelity), str(info.entangle_time * 1e-12)))
                    return [memory_info]

                else:
                    return []
            
            rule = Rule(10, es_rule_actionB, es_rule_conditionB)
            rules.append(rule)

        for rule in rules:
            rule.set_reservation(reservation)

        ##print(f'For {self.own.name}: --- len(rules): {len(rules)}')

        return rules

    def load_rules(self, rules: List["Rule"], reservation: "Request") -> None:
        """Method to add created rules to resource manager.

        This method will schedule the resource manager to load all rules at the reservation start time.
        The rules will be set to expire at the reservation end time.

        Args:
            rules (List[Rules]): rules to add.
            reservation (Reservation): reservation that created the rules.
        """
        # cache events that are being scheduled to access them later if the reservations need to be aborted
        scheduled_events = []
        self.accepted_reservation.append(reservation)
        for card in self.vmemorylist:

            # initialise all memories in the reservations by first setting their state to raw and setting their expiry time
            if reservation in card.reservations:
                #if self.own.name == 'b' and card.memory_index == 0:
                #    #print ('Memory 0 in b is in this reservation')
                #process = Process(self.own.resource_manager, "update",
                                 # [None, self.own.memory_array[card.memory_index], "RAW"])
                #event = Event(reservation.end_time, process, 1)
                event = Event(reservation.end_time,self.node.resource_manager, "update",[None, self.node.memory_array[card.memory_index], "RAW"],1)
                scheduled_events.append(event)
                #self.own.timeline.schedule(event)
                self.node.timeline.schedule_counter += 1
                self.node.timeline.events.push(event)


        # for all the rules corresponding to these memories (generation, purification or swapping), create processes
        # for each rule, a load and an expire event is scheduled. 
        for rule in rules:
            #process = Process(self.own.resource_manager, "load", [rule])
            #event = Event(reservation.start_time, process)
            event = Event(reservation.start_time,self.node.resource_manager, "load", [rule] )
            #self.own.timeline.schedule(event)
            self.node.timeline.schedule_counter += 1
            self.node.timeline.events.push(event)
            scheduled_events.append(event)
            #process = Process(self.own.resource_manager, "expire", [rule])
            #event = Event(reservation.end_time, process, 0)
            event = Event(reservation.end_time,self.node.resource_manager, "expire", [rule],0)
            scheduled_events.append(event)
            #self.own.timeline.schedule(event)
            self.node.timeline.schedule_counter += 1
            self.node.timeline.events.push(event)

        # Map the new events to a map with the corresponding reservation stored in the resource manager 
        self.node.resource_manager.reservation_to_events_map[reservation] = scheduled_events


    def memories_available(self):


        demand_count=0

        #self.vmemorylist = [MemoryTimeCard(i) for i in range(len(self.node.memory_array))]
        self.vmemorylist=self.node.vmemory_list

        print(len(self.node.vmemory_list),self.node.name,self.request,"memory available")

        index_list=[]

        if self.node.name==self.request.initiator or self.node.name==self.request.responder :
            
            demand_count=self.request.memory_size

        else :

            demand_count=self.request.memory_size*2

        #print("demand count by request",demand_count,self.request)

        for vmemory in self.vmemorylist:

            start =0
            end = len(vmemory.reservations)-1

            while start<=end :
                mid=(start+end)//2 
                if vmemory.reservations[mid].start_time>self.request.end_time :
                    
                    end=mid-1

                elif vmemory.reservations[mid].end_time<self.request.start_time :

                    start=mid+1

                elif max(vmemory.reservations[mid].start_time,self.request.start_time)<min(vmemory.reservations[mid].end_time,self.request.end_time):
                    start=-1
                    break
        
                else:
                    
                    pass 
  
            if (start>=0):
                
                index_list.append((start,vmemory.memory_index))
                demand_count=demand_count-1
            
            
            if(demand_count==0):

                for i in range(0,len(index_list)) :
                    print(index_list,index_list[i],)
                    #print("memory index",vmemorylist[index_list[i][1]])
                    #print("list index" ,index_list[i][0] )
                    self.vmemorylist[index_list[i][1]].reservations.insert(index_list[i][0],self.request)
                    if self.request.id not in self.node.resource_manager.reservation_id_to_memory_map:

                        self.node.resource_manager.reservation_id_to_memory_map[self.request.id] = []
                        self.node.resource_manager.reservation_id_to_memory_map[self.request.id].append(index_list[i][1])


                return True    
        #print(demand_count)
        
        if (demand_count>0):

            print(demand_count,"demand count")
            index_list.clear()
            return False
        

    def start(self):

        #print(self.memories_available(),self.node.name)
            #if RESOURCES AVAILABLE:
        if self.memories_available() :

            if (self.request.responder!=self.node.name):

                next_node=self.routing.tempnexthop()
                #msgr=RRMessage(RRPMsgType.RESERVE,next_node,self.request) #msg_type="RESERVE"
                
                #print("message type , receiver", msgr.msg_type ,msgr.receiver)
                msg=RRMessage(RRPMsgType.RESERVE,"network_manager",self.request)
                msg.temp_path=self.routing.temp_path
                msg.marker=self.routing.marker
                print("msg.msg_typed",msg.msg_type,msg)
                self.request.path.append(self.node)
                self.request.pathnames.append(self.node.name)
                self.node.send_message(next_node,msg)
                #send_message(self, dst: str, msg: "Message", priority=inf)
                #self.node.messagehandler.send_message(receiver_node,request , msg_type)####send message to next hop node's network manager (send message function?network manager or protocol)
             
            if (self.request.responder==self.node.name):
                
                print ("destination",self.node.name)
                self.request.path.append(self.node)
                self.request.pathnames.append(self.node.name)
                index=self.request.path.index(self.node)
                prev_node=self.request.path[index-1]
                msg=RRMessage(RRPMsgType.CREATE_TASKS,"reservation_manager",self.request)
                print(" final message type fp , receiver", msg.msg_type ,msg.receiver)
                #index=path.index(self.node.name)
                #print(path[index+1])

                """create tasks and back propagate that msg to create tasks to previous node
                
                """
                rules=self.create_rules(self.request.pathnames,self.request)
                self.load_rules(rules,self.request)
                print("tasks created at" ,self.node.name )
                #call task and dependency creation method
                self.node.send_message(prev_node.name,msg)
                #send classical message to previous node path[index-1]'s Reservation protocol to createtasks 
                #in receive msg check this condn
                #send(msg_type)
                          
        else :
            msg=RRMessage(RRPMsgType.FAIL,"reservation_manager",self.request)
            
            #(RESORCES NOT AVAILABLE)
            #msg_type="FAIL"

            #self.rnode.send_message(path[len(path)-1].name ,msg)
            if self.node.name==self.request.initiator:
                print("------node at which it is failing---",self.node.name)
                return
            else :
                #index=self.request.path.index(self.node)
                index=len(self.request.path)-1
                #prev_node=self.request.path[index-1]
                prev_node=self.request.path[index]
                self.node.send_message(prev_node.name,msg)

    
    def receive_message(self ,msg :"RRPMsgType"):

        if msg.msg_type==RRPMsgType.CREATE_TASKS :

            self.request=msg.payload

            if self.node.name==self.request.initiator:
                #create tasks
                print("tasks created at ",self.node.name)
                rules=self.create_rules(self.request.pathnames,self.request)
                self.load_rules(rules,self.request)

            else:
                index=self.request.path.index(self.node)
                prev_node=self.request.path[index-1]
                
                """create tasks and back propagate that msg to crate tasks to previous node"""
                rules=self.create_rules(self.request.pathnames,self.request)
                self.load_rules(rules,self.request)
                #call tasks and dependency
                print("tasks created at ",self.node.name)
                msg=RRMessage(RRPMsgType.CREATE_TASKS,"reservation_manager",self.request)
                self.node.send_message(prev_node.name,msg)
                
            
                #previous_node=self.request.path[previous_node_index]

                #send classical msg to previous node to create tasks
            #elif msg.msg_type==RRPMsgType.FAIL:
            # Mechanism to release resources
            #send_message(to release)
            #vmemoryarray[index_list[i][1]].reservations.remove(req.reser)

            #back track path and release resources"""

        elif msg.msg_type==RRPMsgType.FAIL :
            
            self.request=msg.payload

            if self.node.name==self.request.initiator:
                #create tasks
                print("removed resources at ",self.node.name)
                #vmemoryarray[index_list[i][1]].reservations.remove(req.reser)
                for vmemory in self.vmemorylist:
                    if self.request in vmemory.reservations:
                        vmemory.reservations.remove(self.request)
                

            else:
                for vmemory in self.vmemorylist:
                    if self.request in vmemory.reservations:
                        vmemory.reservations.remove(self.request)
                index=self.request.path.index(self.node)
                prev_node=self.request.path[index-1]
                print("removed resources at ",self.node.name)
                msg=RRMessage(RRPMsgType.FAIL,"reservation_manager",self.request)
                self.node.send_message(prev_node.name,msg)





    
    




        
        

       