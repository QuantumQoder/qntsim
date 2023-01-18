import numpy as np
from typing import List
from IPython.display import clear_output
from numpy.random import randint

from ..kernel.timeline import Timeline
Timeline.bk = True
Timeline.DLCZ = False
from ..topology.topology import Topology
from ..components.circuit import QutipCircuit

def string_to_binary(messages:List[str]):
    print('Converting to binary...')
    strings = [''.join('0'*(8-len(bin(ord(char))[2:]))+bin(ord(char))[2:] for char in message) for message in messages]
    print('Conversion completed!!')
    
    return strings

class Network:
    def __init__(self,
                 topology:str,
                 messages:List[str],
                 backend:str='Qutip',
                 parameters:str='parameters.txt',
                 **kwargs) -> None:
        self.topology = topology
        self.backend = backend
        self.parameters = parameters
        self.messages = messages
        is_binary = all(char=='0' or char=='1' for message in messages for char in message)
        messages = messages if is_binary else string_to_binary(messages=messages)
        if callable((size:=kwargs.get('size', len(messages[0])))): size=size(messages[0])
        self.size = size
        self.__kwargs__ = kwargs
        self.__initiate__()
        self._get_keys_(node_index=kwargs.get('keys_of', 0), info_state='ENTANGLED')
    
    def __initiate__(self):
        topology = self.topology
        backend = self.backend
        kwargs = self.__kwargs__
        stop_time = kwargs.get('stop_time', 10e12)
        timeline = Timeline(stop_time=stop_time, backend=backend)
        net_topo = Topology(name=kwargs.get('name', 'network'), timeline=timeline)
        net_topo.load_config(topology)
        self.timeline = timeline
        self.net_topo = net_topo
        self.__set_parameters__()
        self.nodes = net_topo.get_nodes_by_type('EndNode')
        self.qchannels = net_topo.qchannels
        self.cchannels = net_topo.cchannels
        self.manager = timeline.quantum_manager
        if len(self.nodes)>1:
            self.__initials__ = 0
            self.__request_entanglements__()
            timeline.init()
            timeline.run()
            self.__rectify_entanglements__(label=kwargs.get('label', '00'))
            clear_output()
            print('Entanglement generated!!')
        else:
            self.__initialize_photons__()
            print('Photons have been randomly initialized.')
    
    def __set_parameters__(self):
        parameters = self.parameters
        net_topo = self.net_topo
        with open(parameters, 'r') as file:
            dict = eval(file.read())
            for key, value in dict.items():
                for component in net_topo.get_nodes_by_type(key) if key!='qchannel' else net_topo.qchannels:
                    if key=='qchannel':
                        component.attenuation = value[0]
                        component.frequency = value[1]
                    else:
                        for k, v in value.items():
                            if key=='EndNode' or key=='ServiceNode': component.memory_array.update_memory_params(k, v)
                            elif key=='BSMNode': component.bsm.update_detectors_params(k, v)
                            elif key=='QuantumRouter':
                                if k=='SWAP_SUCCESS_PROBABILITY': component.network_manager.protocol_stack[1].set_swapping_success_rate(v)
                                else: component.network_manager.protocol_stack[1].set_swapping_degradation(v)
    
    def __request_entanglements__(self):
        nodes = self.nodes
        kwargs = self.__kwargs__
        start_time = kwargs.get('start_time', 5e12)
        end_time = kwargs.get('end_time', 10e12)
        priority = kwargs.get('priority', 0)
        target_fidelity = kwargs.get('target_fidelity', 0.5)
        timeout = kwargs.get('timeout', 10e12)
        for node1, node2 in zip(nodes[:-1], nodes[1:]):
            node1.transport_manager.request(node2.owner.name,
                                            size=self.size,
                                            start_time=start_time,
                                            end_time=end_time,
                                            priority=priority,
                                            target_fidelity=target_fidelity,
                                            timeout=timeout)
    
    def __rectify_entanglements__(self, label:str):
        nodes = self.nodes
        manager = self.manager
        for node in nodes[:-1]:
            for info in node.resource_manager.memory_manager:
                if info.state=='ENTANGLED':
                    key = info.memory.qstate_key
                    state = manager.get(key)
                    state = state.state
                    qtc = QutipCircuit(1)
                    if state[0+int(label[1])]==state[3-int(label[1])]==0:
                        if state[1-int(label[1])]==((-1)**-~int(label[0]))*state[2+int(label[1])]: qtc.z(0)
                        qtc.x(0)
                    elif state[0+int(label[1])]==((-1)**-~int(label[0]))*state[3-int(label[1])]: qtc.z(0)
                    manager.run_circuit(qtc, [key])
    
    def __initialize_photons__(self):
        node = self.nodes[0]
        manager = self.manager
        initials = randint(4, size=self.size)
        for info, initial in zip(node.resource_manager.memory_manager, initials):
            key = info.memory.qstate_key
            q, r = divmod(initial, 2)
            qtc = QutipCircuit(1)
            if r: qtc.x(0)
            if q: qtc.h(0)
            manager.run_circuit(qtc, [key])
        self.__initials__ = initials.tolist()
    
    def _get_keys_(self, node_index:int, info_state:str='ENTANGLED'):
        node = self.nodes[node_index]
        manager = self.manager
        keys = []
        for info in node.resource_manager.memory_manager:
            if info.state==info_state:
                key = info.memory.qstate_key
                state = manager.get(key=key)
                keys.append(state.keys)
        self.keys = keys
    
    def _generate_state_(self, state:int=0):
        nodes = self.nodes
        manager = self.manager
        size = self.size
        middle_node = nodes[1]
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        if state: qtc.h(0)
        qtc.measure(1-state)
        qc = QutipCircuit(1)
        if state: qc.z(0)
        else: qc.x(0)
        for info1, info2 in zip(middle_node.resource_manager.memory_manager[:size],
                                middle_node.resource_manager.memory_manager[size:]):
            keys = [info1.memory.qstate_key, info2.memory.qstate_key]
            qstate = manager.get(keys[1-state])
            if manager.run_circuit(qtc, keys).get(keys[1-state]): manager.run_circuit(qc, [key for key in qstate.keys if key!=keys[1-state]])
    
    @staticmethod
    def encode(network:'Network', msg_index:int, node_index:int=0, *args):
        node = network.nodes[node_index]
        message = network.messages[msg_index]
        manager = network.manager
        for char, info in zip(message, node.resource_manager.memory_manager):
            if int(char):
                qtc = QutipCircuit(1)
                qtc.x(0)
                qtc.z(0)
                key = info.memory.qstate_key
                manager.run_circuit(qtc, [key])
    
    @staticmethod
    def superdense_code(network:'Network', msg_index:int, node_index:int=0, *args):
        node = network.nodes[node_index]
        message = network.messages[msg_index]
        manager = network.manager
        for char1, char2, info in zip(message[::2], message[1::2], node.resource_manager.memory_manager):
            qtc = QutipCircuit(1)
            if int(char2): qtc.x(0)
            if int(char1): qtc.z(0)
            key = info.memory.qstate_key
            manager.run_circuit(qtc, [key])
    
    def teleport(self, node_index:int=0, msg_index:int=0):
        alpha = 1/np.sqrt(2)
        node = self.nodes[node_index]
        message = self.messages[msg_index]
        manager = self.manager
        bsa = QutipCircuit(2)
        bsa.cx(0, 1)
        bsa.h(0)
        bsa.measure(0)
        bsa.measure(1)
        corrections = {}
        for char, info in zip(message, node.resource_manager.memory_manager):
            key = info.memory.qstate_key
            new_key = manager.new([alpha, ((-1)**int(char))*alpha])
            state = manager.get(key)
            keys = tuple([k for k in state.keys if k!=key])
            outputs = manager.run_circuit(bsa, [new_key, key])
            corrections[keys] = [outputs.get(new_key), outputs.get(key)]
        self.corrections = corrections
    
    def measure(self):
        outputs = []
        manager = self.manager
        kwargs = self.__kwargs__
        if (initials := self.__initials__):
            node = self.nodes[0]
            for info, initial in zip(node.resource_manager.memory_manager, initials):
                key = info.memory.qstate_key
                qtc = QutipCircuit(1)
                if initial//2: qtc.h(0)
                qtc.measure(0)
                outputs.append(manager.run_circuit(qtc, [key]))
        else:
            corrections = self.corrections
            output = 0
            for keys, value in corrections.items():
                if len(keys)>1:
                    key = max(keys)
                    qtc = QutipCircuit(1)
                    state = kwargs.get('state', 0)
                    if ~state: qtc.h(0)
                    qtc.measure(0)
                    output = manager.run_circuit(qtc, [key]).get(key)
                qtc = QutipCircuit(1)
                if output:
                    if state: qtc.x(0)
                    else: qtc.z(0)
                if value[1]: qtc.x(0)
                if value[0]: qtc.z(0)
                qtc.h(0)
                qtc.measure(0)
                key = min(keys)
                outputs.append(manager.run_circuit(qtc, [key]))
        self.__outputs__ = outputs
    
    @staticmethod
    def decode(networks:List['Network'], *args):
        recv_msgs_list = []
        for network in networks:
            outputs = network.__outputs__
            messages = network.messages
            initials = network.__initials__
            strings = []
            if initials:
                node = network.nodes[0]
                for message in messages:
                    string = ''
                    for info, initial, output in zip(node.resource_manager.memory_manager,
                                                    initials, outputs):
                        char = message[info.index] if len(messages)>1 else '0'
                        key = info.memory.qstate_key
                        string+=str(initial%2^output.get(key)^int(char))
                    strings.append(string)
            else:
                strings = [''.join(str(*output.values()) for output in outputs)]
            recv_msgs = {i:''.join(chr(int(string[j*8:-~j*8], 2)) for j in range(len(string)//8)) for i, string in enumerate(strings, 1)}
            network.strings = strings
            network.recv_msgs = recv_msgs
            print('Received messages!!')
            for k, v in recv_msgs.items():
                print(f'Received message {k}: {v}')
            recv_msgs_list.append(recv_msgs)
        
        return recv_msgs_list
    
    def dump(self, node_name:str, info_state:str=''):
        manager = self.manager
        net_topo = self.net_topo
        for node in [net_topo.nodes.get(node_name)] if node_name else self.nodes:
            print(f'{node.owner.name}\'s memory arrays!!')
            for info in node.resource_manager.memory_manager:
                if not info_state or info.state==info_state:
                    key = info.memory.qstate_key
                    state = manager.get(key)
                    print(state.keys, state.state)
    
    def draw(self):
        self.net_topo.get_virtual_graph()