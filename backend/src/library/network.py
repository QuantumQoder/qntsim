import numpy as np, logging, inspect, sys
from pandas import DataFrame
from joblib import Parallel, wrap_non_picklable_objects, delayed
from functools import partial, reduce
from typing import Any, List, Dict
from IPython.display import clear_output
from numpy.random import randint

from ..kernel.timeline import Timeline
Timeline.bk = True
Timeline.DLCZ = False
from ..topology.topology import Topology
from ..components.circuit import QutipCircuit
from .circuits import bell_type_state_analyzer

def string_to_binary(messages:Dict[int, str]):
    strings = [''.join('0'*(8-len(bin(ord(char))[2:]))+bin(ord(char))[2:] for char in message) for _, message in messages.items()]
    logging.info('converted')
    
    return strings

class Network:
    _funcs:List[partial] = []
    def __init__(self,
                 topology:str,
                 messages:Dict[int, str],
                 name:str='network',
                 backend:str='Qutip',
                 parameters:str='parameters.txt',
                 **kwargs) -> None:
        self.__name = name
        self._topology = topology
        self._backend = backend
        self._parameters = parameters
        self.messages = messages
        is_binary = all(char=='0' or char=='1' for _, message in messages.items() for char in message)
        self.bin_msgs = list(messages.values()) if is_binary else string_to_binary(messages=messages)
        if callable((size:=kwargs.get('size', len(self.bin_msgs[0])))): size=size(len(self.bin_msgs[0]))
        self.size = size
        self._kwargs = kwargs
        stack = inspect.stack()
        caller = stack[1][0].f_locals.get('self').__class__.__name__
        from .protocol import Protocol
        if caller!=Protocol.__name__:
            print('Configuring logger!')
            logging.basicConfig(filename=self.__name+'.log', filemode='w', level=logging.INFO, format='%(pathname)s %(threadName)s %(module)s %(funcName)s %(message)s')
        self.__initiate__()
        self._get_keys_(node_index=kwargs.get('keys_of', 0), info_state='ENTANGLED')
    
    def __call__(self, id_:int=0):
        self.__id = id_
        self.__name+=str(self.__id)
        return self
    
    def __iter__(self):
        for node in self.nodes:
            yield node
    
    def __getitem__(self, item):
        return self.nodes[item]
    
    def __initiate__(self):
        stop_time = self._kwargs.get('stop_time', 10e12)
        self._timeline = Timeline(stop_time=stop_time, backend=self._backend)
        self._net_topo = Topology(name=self._kwargs.get('name', 'network'), timeline=self._timeline)
        self._net_topo.load_config(self._topology)
        self.__set_parameters__()
        self.nodes = self._net_topo.get_nodes_by_type('EndNode')
        self.qchannels = self._net_topo.qchannels
        self.cchannels = self._net_topo.cchannels
        self.manager = self._timeline.quantum_manager
        self._bell_pairs = {}
        self._initials = 0
        if len(self.nodes)>1:
            self.__request_entanglements__()
            self._timeline.init()
            self._timeline.run()
            self.__identify_states__()
            self.__rectify_entanglements__(label=self._kwargs.get('label', '00'))
            clear_output()
            logging.info('epr pair generator')
        else:
            self.__initialize_photons__()
    
    def __set_parameters__(self):
        with open(self._parameters, 'r') as file:
            dict = eval(file.read())
            for key, value in dict.items():
                for component in self._net_topo.get_nodes_by_type(key) if key!='qchannel' else self._net_topo.qchannels:
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
        start_time = self._kwargs.get('start_time', 5e12)
        end_time = self._kwargs.get('end_time', 10e12)
        priority = self._kwargs.get('priority', 0)
        target_fidelity = self._kwargs.get('target_fidelity', 0.5)
        timeout = self._kwargs.get('timeout', 10e12)
        for node1, node2 in zip(self[:-1], self[1:]):
            node1.transport_manager.request(node2.owner.name,
                                            size=self.size,
                                            start_time=start_time,
                                            end_time=end_time,
                                            priority=priority,
                                            target_fidelity=target_fidelity,
                                            timeout=timeout)
    
    def __identify_states__(self):
        for node in self[:-1]:
            for info in node.resource_manager.memory_manager:
                if info.state!='ENTANGLED': break
                key = info.memory.qstate_key
                state = self.manager.get(key).state
                j = 0 if state[1]==state[2]==0 else 1
                i = (1-int(state[j]/state[3-j]))//2
                print(tuple(self.manager.get(key).keys), (i, j))
                self._bell_pairs[tuple(self.manager.get(key).keys)] = (i, j)

    def __rectify_entanglements__(self, label:str):
        for (key1, key2), (i, j) in self._bell_pairs.items():
            qtc = QutipCircuit(1)
            if j^int(label[1]): qtc.x(0)
            if i^int(label[0]): qtc.z(0)
            self.manager.run_circuit(qtc, [key1])
            self._bell_pairs[(key1, key2)] = (int(label[0]), int(label[1]))
    
    def __initialize_photons__(self):
        self._initials = randint(4, size=self.size)
        for info, initial in zip(self[0].resource_manager.memory_manager, self._initials):
            key = info.memory.qstate_key
            q, r = divmod(initial, 2)
            qtc = QutipCircuit(1)
            if r: qtc.x(0)
            if q: qtc.h(0)
            self.manager.run_circuit(qtc, [key])
        self._initials = self._initials.tolist()
        logging.info('for encoding message')
    
    def _get_keys_(self, node_index:int, info_state:str='ENTANGLED'):
        keys = []
        for info in self[node_index].resource_manager.memory_manager:
            if info.state==info_state:
                key = info.memory.qstate_key
                state = self.manager.get(key=key)
                keys.append(state.keys)
        self.keys = keys
    
    def generate_state(self, returns:Any, state:int=0, label:str=None):
        middle_node = self[1]
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        if state: qtc.h(0)
        qtc.measure(1-state)
        qc = QutipCircuit(1)
        if state: qc.z(0)
        else: qc.x(0)
        for info1, info2 in zip(middle_node.resource_manager.memory_manager[:self.size],
                                middle_node.resource_manager.memory_manager[self.size:]):
            keys = [info1.memory.qstate_key, info2.memory.qstate_key]
            qstate = self.manager.get(keys[1-state])
            if self.manager.run_circuit(qtc, keys).get(keys[1-state]): self.manager.run_circuit(qc, list(set(qstate.keys)-set([keys[1-state]])))
        if label:
            for info in self[0].resource_manager.memory_manager:
                if info.state!='ENTANGLED': break
                keys = self.manager.get(info.memory.qstate_key).keys
                for key, (i, lbl) in zip(keys, enumerate(label)):
                    qtc = QutipCircuit(1)
                    if int(lbl): _ = qtc.x(0) if i else qtc.z(0)
                    self.manager.run_circuit(qtc, [key])
    
    @staticmethod
    def encode(network:'Network', returns:Any, msg_index:int, node_index:int=0):
        for bin, info in zip(network.bin_msgs[msg_index], network.nodes[node_index].resource_manager.memory_manager):
            if int(bin):
                qtc = QutipCircuit(1)
                qtc.x(0)
                qtc.z(0)
                key = info.memory.qstate_key
                network.manager.run_circuit(qtc, [key])
        logging.info('message bits into qubits')
    
    @staticmethod
    def superdense_code(network:'Network', returns:Any, msg_index:int, node_index:int=0):
        for bin1, bin2, info in zip(network.bin_msgs[msg_index][::2], network.bin_msgs[msg_index][1::2], network.nodes[node_index].resource_manager.memory_manager):
            qtc = QutipCircuit(1)
            if int(bin2): qtc.x(0)
            if int(bin1): qtc.z(0)
            key = info.memory.qstate_key
            network.manager.run_circuit(qtc, [key])
        logging.info('message bits into the channel')
    
    def teleport(self, returns:Any, node_index:int=0, msg_index:int=0):
        alpha = complex(1/np.sqrt(2))
        bsa = bell_type_state_analyzer(2)
        corrections = {}
        for bin, info in zip(self.bin_msgs[msg_index], self[node_index].resource_manager.memory_manager):
            key = info.memory.qstate_key
            self.manager.new()
            new_key = self.manager.new([alpha, ((-1)**int(bin))*alpha])
            state = self.manager.get(key)
            keys = tuple(set(state.keys)-set([key]))
            outputs = self.manager.run_circuit(bsa, [new_key, key])
            corrections[keys] = [outputs.get(new_key), outputs.get(key)]
        self._corrections = corrections
        logging.info('message states')
    
    def measure(self, returns:Any):
        outputs = []
        if self._initials:
            node = self[0]
            for info, initial in zip(node.resource_manager.memory_manager, self._initials):
                key = info.memory.qstate_key
                qtc = QutipCircuit(1)
                if initial//2: qtc.h(0)
                qtc.measure(0)
                outputs.append(self.manager.run_circuit(qtc, [key]))
        else:
            corrections = self._corrections
            output = 0
            for keys, value in corrections.items():
                if len(keys)>1:
                    key = max(keys)
                    qtc = QutipCircuit(1)
                    state = self._kwargs.get('state', 0)
                    if ~state: qtc.h(0)
                    qtc.measure(0)
                    output = self.manager.run_circuit(qtc, [key]).get(key)
                qtc = QutipCircuit(1)
                if output:
                    if state: qtc.x(0)
                    else: qtc.z(0)
                if value[1]: qtc.x(0)
                if value[0]: qtc.z(0)
                qtc.h(0)
                qtc.measure(0)
                key = min(keys)
                outputs.append(self.manager.run_circuit(qtc, [key]))
        self._outputs = outputs
    
    @staticmethod
    @delayed
    @wrap_non_picklable_objects
    def _decode(network:'Network', *args):
        strings = []
        if network._initials:
            node = network.nodes[0]
            for bin_msg in network.bin_msgs:
                string = ''
                for info, initial, output in zip(node.resource_manager.memory_manager, network._initials, network._outputs):
                    bin = bin_msg[info.index] if len(network.bin_msgs)>1 else '0'
                    key = info.memory.qstate_key
                    string+=str(initial%2^output.get(key)^int(bin))
                strings.append(string)
        else:
            strings = [''.join(str(*output.values()) for output in network._outputs)]
        recv_msgs = {i:''.join(chr(int(string[j*8:-~j*8], 2)) for j in range(len(string)//8)) for i, string in enumerate(strings, 1)}
        network.strings = strings
        network.recv_msgs = recv_msgs
        for k, v in recv_msgs.items():
            logging.info(f'Received message {k}: {v}')
        
        return recv_msgs
    
    @classmethod
    def decode(cls, networks:List['Network'], *args):
        logging.info('messages')
        return Parallel(n_jobs=-1, prefer='threads')(cls._decode(*arg, network=network) for arg, network in zip([args for _ in range(len(networks))], networks))
    
    def dump(self, returns:Any, node_name:str='', info_state:str=''):
        logging.basicConfig(filename=self.__name+'.log', filemode='w', level=logging.INFO, format='%{funcName}s %(message)s')
        for node in [self._net_topo.nodes.get(node_name)] if node_name else self.nodes:
            logging.info(f'{node.owner.name}\'s memory arrays')
            keys, states = [], []
            for info in node.resource_manager.memory_manager:
                if not info_state or info.state==info_state:
                    key = info.memory.qstate_key
                    state = self.manager.get(key)
                    keys.append(state.keys)
                    states.append(state.state)
                dataframe = DataFrame({'keys':keys, 'states':states})
        logging.info(dataframe.to_string())
    
    def draw(self, returns:Any):
        self._net_topo.get_virtual_graph()
    
    @staticmethod
    @delayed
    @wrap_non_picklable_objects
    def _execute(network:'Network'):
        _ = reduce(lambda returns, func:func(network, returns), network._funcs, ())
    
    # def __call__(self, *args: Any, **kwds: Any) -> Any:
    #     _ = Parallel(n_jobs=-1, prefer='threads')(self._execute(network=network) for network in networks)
    
    @classmethod
    def execute(cls, networks:List['Network']):
        _ = Parallel(n_jobs=-1, prefer='threads')(cls._execute(network=network) for network in networks)