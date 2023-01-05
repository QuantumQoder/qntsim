#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import numpy as np, matplotlib.pyplot as plt
from numpy.random import randint, uniform
from typing import List
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ = False
Timeline.bk = True
from qntsim.topology.topology import Topology
from qntsim.components.circuit import *
from qutip import Qobj
from statistics import mean, stdev
from IPython.display import clear_output
import os


# %%


class Network:
    def __init__(self, topology:str, messages:List[str], backend:str='Qutip', parameters='parameters.txt', **kwargs):
        self.topology = topology
        self.backend = backend
        all_binary = all(char=='0' or char=='1' for message in messages for char in message)
        messages = messages if all_binary else string_to_binary(messages)
        self.messages = messages
        self.corrections = {}
        self.strings = []
        if callable((size:=kwargs.get('size', len(messages[0])))):
            size = size(messages)
        self.size = size
#         if 'size' in kwargs:
#             for message in messages:
#                 message+='0'
#         print(self.size)
        self.initiate(parameters, **kwargs)
        self.get_keys(kwargs.get('get_keys', 0))
    
    def get_keys(self, node:int):
        keys = []
        node = self.nodes[node]
        manager = self.manager
        keys = []
        for info in node.resource_manager.memory_manager:
            if info.state=='ENTANGLED':
                key = info.memory.qstate_key
                state = manager.get(key)
                keys.append(state.keys)
        self.keys = keys
    
    def initiate(self, parameters:str, **kwargs):
        topology = self.topology
        backend = self.backend
#         print(topology, backend)
        if 'stop_time' not in kwargs: stop_time = 10e12
#         size = self.size
        timeline = Timeline(stop_time=stop_time, backend=backend)
        network = Topology(kwargs.get('name', 'name'), timeline)
        network.load_config(topology)
        self.timeline = timeline
        self.network = network
        self.set_parameters(parameters, network)
        self.nodes = network.get_nodes_by_type('EndNode')
        self.manager = self.nodes[0].timeline.quantum_manager
        if ~-len(self.nodes):
            self.request_entanglements(**kwargs)
            timeline.init()
            timeline.run()
            self.rectify_entanglements(label=kwargs.get('label', '00'))
            self.initials = 0
            clear_output()
            print('EPR pairs generated!!')
        else:
            self.initialize_nodes()
            print('Randomly initialized photons generated!!')
    
    def set_parameters(self, parameters:str, network):
#         network = self.network
        print('parameters', os.getcwd(),parameters)
        with open(parameters, 'r') as file:
            dict = eval(file.read())
            for key, value in dict.items():
                if key!='qchannel':
                    for node in network.get_nodes_by_type(key):
                        for k, v in value.items():
                            if key=='EndNode' or key=='ServiceNode':
                                node.memory_array.update_memory_params(k, v)
                            elif key=='BSMNode':
                                node.bsm.update_detectors_params(k, v)
                            elif key=='QuantumRouter':
                                node.network_manager.protocol_stack[1].set_swapping_success_rate(v) if k=='SWAP_SUCCESS_PROBABILTY' else node.network_manager.protocol_stack[1].set_swapping_degradation(v)
                else:
                    for qchannel in network.qchannels:
                        qchannel.attenuation = value[0]
                        qchannel.frequecy = value[1]
    
    def request_entanglements(self, **kwargs):
        nodes = self.nodes
        start_time = kwargs.get('start_time', 5e12)
        end_time = kwargs.get('end_time', 10e12)
        priority = kwargs.get('priority', 0)
        target_fidelity = kwargs.get('target_fidelity', 0.5)
        timeout = kwargs.get('timeout', 10e12)
        for node1, node2 in zip(nodes[:-1], nodes[1:]):
            node1.transport_manager.request(node2.owner.name,
                                            start_time=start_time,
                                            size=self.size,
                                            end_time=end_time,
                                            priority=priority,
                                            target_fidelity=target_fidelity,
                                            timeout=timeout)
#         self.get_keys()
    
    def rectify_entanglements(self, label:str='00'):
        nodes = self.nodes
        manager = self.manager
        qtc = QutipCircuit(1)
        for node in nodes[:-1]:
#             manager = node.timeline.quantum_manager
            for info in node.resource_manager.memory_manager:
                if info.state=='ENTANGLED':
                    key = info.memory.qstate_key
                    state = manager.get(key)
        #             keys = state.keys
                    state = state.state
                    qtc = QutipCircuit(1)
                    if state[0+int(label[1])]==state[3-int(label[1])]==0:
                        if state[1-int(label[1])]==((-1)**-~int(label[0]))*state[2+int(label[1])]: qtc.z(0)
                        qtc.x(0)
                    elif state[0+int(label[1])]==((-1)**-~int(label[0]))*state[3-int(label[1])]: qtc.z(0)
                    manager.run_circuit(qtc, [key])
    
    def initialize_nodes(self):
        node = self.nodes[0]
        manager = self.manager
        initials = randint(4, size=self.size)
        for i, initial in enumerate(initials):
            qtc = QutipCircuit(1)
            q, r = divmod(initial, 2)
            if r: qtc.x(0)
            if q: qtc.h(0)
            info = node.resource_manager.memory_manager[i]
            key = info.memory.qstate_key
            manager.run_circuit(qtc, [key])
#         for info, initial in zip(node.resource_manager.memory_manager, initials):
#             print(info, initial)
#             key = info.memory.qstate_key
#             print(key)
#             qtc = QutipCircuit(1)
#             q, r = divmod(initial, 2)
#             if r: qtc.x(0)
#             if q: qtc.h(0)
#             manager.run_circuit(qtc, [key])
        self.initials = initials.tolist()
#         self.timeline.init()
#         self.timeline.run()

    def generate_state(self, state=0):
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
    def encode(network_obj, i:int):
        node = network_obj.nodes[0]
        message = network_obj.messages[i]
        manager = network_obj.manager
        for char, info in zip(message, node.resource_manager.memory_manager):
            if int(char):
                qtc = QutipCircuit(1)
                qtc.x(0)
                qtc.z(0)
                key = info.memory.qstate_key
                manager.run_circuit(qtc, [key])
    
    def teleport(self):
        corrections = {}
        alpha = 1/np.sqrt(2)
        node = self.nodes[0]
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.h(0)
        qtc.measure(0)
        qtc.measure(1)
        manager = self.manager
        message = self.messages[0]
        for char, info in zip(message, node.resource_manager.memory_manager):
            key = info.memory.qstate_key
            state = manager.get(key)
            new_key = manager.new([alpha, ((-1)**int(char))*alpha])
            keys = tuple([k for k in state.keys if k!=key])
            outputs = manager.run_circuit(qtc, [new_key, key])
            corrections[keys] = [outputs.get(new_key), outputs.get(key)]
        self.corrections = corrections
    
    @staticmethod
    def superdense_code(network_obj, message:int, node:int):
        node = network_obj.nodes[node]
        manager = network_obj.manager
        message = network_obj.messages[message]
        for info, char0, char1 in zip(node.resource_manager.memory_manager,
                                      message[::2], message[1::2]):
            key = info.memory.qstate_key
            qtc = QutipCircuit(1)
            if int(char1): qtc.x(0)
            if int(char0): qtc.z(0)
            manager.run_circuit(qtc, [key])
    
    def measure(self, **kwargs):
        outputs = []
        manager = self.manager
#         initials = self.initials
        if (initials := self.initials):
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
                if ~-len(keys):
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
        self.outputs = outputs
    
    @staticmethod
    def decode(network_objs:list):
        for network_obj in network_objs:
            node = network_obj.nodes[0]
            outputs = network_obj.outputs
            messages = network_obj.messages
            initials = network_obj.initials
            strings = []
            if initials:
                for message in messages:
                    string = ''
                    for info, initial, output in zip(node.resource_manager.memory_manager,
                                                    initials, outputs):
                        char = message[info.index] if ~-len(messages) else '0'
                        key = info.memory.qstate_key
                        string+=str(initial%2^output.get(key)^int(char))
                    strings.append(string)
            else:
                strings = [''.join(str(*output.values()) for output in outputs)]
            network_obj.strings = strings
            print('Received messages!!')
            for i, string in enumerate(strings, 1):
                print(f'Received message {i}', ''.join(chr(int(string[j*8:-~j*8], 2)) for j in range(len(string)//8)))
    
    def dump(self, info_state='ENTANGLED'):
        manager = self.manager
        for node in self.nodes:
            print("{}'s memory nodes:".format(node.owner.name))
            for info in node.resource_manager.memory_manager:
                if info.state==info_state:
                    key = info.memory.qstate_key
                    state = manager.get(key)
                    print(state.keys, state.state)
    
    def draw(self):
        self.network.get_virtual_graph()


# %%


class Protocol:
    def __init__(self,
                 messages_list:list,
                 topology:str,
                 backend='Qutip',
                 **kwargs):
        networks = []
        attack = kwargs.get('attack')
        encode_params, decode_params = [], []
        encode = kwargs.get('encode', Network.encode)
        if isinstance(encode, list):
            encode_params = encode[1:]
            encode = encode[0]
        decode = kwargs.get('decode', Network.decode)
        if isinstance(decode, list):
            decode_params = decode[1:]
            decode = decode[0]
        for messages in messages_list:
            network = Network(topology=topology,
                              messages=messages,
                              backend=backend,
                              **kwargs)
            print('Bell pairs generated!!')
            network.dump()
            if 'state' in kwargs: network.generate_state(state=kwargs.get('state'))
            if 'encode' not in kwargs and 'label' in kwargs or 'state' in kwargs:
                network.teleport()
                print('Message teleported!!')
            else:
                encode(network, 0, *encode_params)
                print('Message encoded!!')
            network.dump()
            i = range(1, len(network.nodes)) if ~-len(network.nodes) else [0]
            if attack=='DoS': Attack.denial_of_service(network, i)
            if attack=='EM': Attack.entangle_and_measure(network, i)
            if attack=='IR': Attack.intercept_and_resend(network, i)
            if 'encode' in kwargs:
                for i in range(len(messages[1:])):
                    encode(network, -~i, *encode_params)
                print('Rest messages encoded!!')
            if 'decode' not in kwargs:
                print('fuck')
                network.measure(state=kwargs.get('state', 0))
            network.dump()
            print(network.keys)
            decode(network, *decode_params)
            print('Values decoded!!')
#             print(network.strings)
            networks.append(network)
        self.networks = networks
        self.messages_list = messages_list
        full_err_list, mean_list, sd_list = ErrorAnalyzer.analyse(self)
        self.full_err_list = full_err_list
        self.mean_list = mean_list
        self.sd_list = sd_list
    
#     @ignore
#     @staticmethod
#     def execute(topology:str, messages:list, backend='Qutip', threshold=0.5, **kwargs):
#         assert all(len(messages[0])==len(message) for message in messages[1:]), 'The length of all the messages must be equal.'
#         print('Messages for transmission:', messages)
#         messages = messages if all(char=='0' or char=='1' for message in messages for char in message) else string_to_binary(messages)
#         secure = kwargs.get('secure')
#         if not secure:
#             func = kwargs.get('security_function')
#             err_list, mean, sd = check_bits() if not func else func()
#             if mean>threshold:
#                 plt.figure(figsize=(20, 5))
#                 plt.plot(range(1, -~len(err_list)), err_list)
#                 plt.xlabel('Number of Iterations')
#                 plt.ylabel('Mean error percentage per iteration')
#                 print("error in the network:", mean)
#                 print('deviation in the error:', sd)
#         protocol = Protocol(topology=topology)
            
            
            
#             msgs = [''.join(str(randint(2)) for i in range(100)) for i in range(len(messages))]
#             protocol = Protocol(topology=topology,
#                                 messages_list=[msgs],
#                                 backend=backend,
#                                 **kwargs)
#         else:
#             func = kwargs.get('security_function')
#             msgs, indices = check_bits(messages) if not func else func(messages)
#             protocol = Protocol(topology=topology,
#                                 messages_list=[msgs],
#                                 backend=backend,
#                                 indices=indices, **kwargs)
#         network = protocol.networks[0]
#         err_list = protocol.full_err_list[0]
#         mn = protocol.mean_list[0]
#         std = protocol.sd_list[0]
#         if mn>threshold:
#             plt.figure(figsize=(20, 5))
#             plt.plot(range(1, -~len(err_list)), err_list)
#             plt.xlabel('Number of Iterations')
#             plt.ylabel('Mean error percentage per iteration')
#         else:
#             if not secure:
#                 protocol = Protocol(topology=topology,
#                                     messages_list=[messages],
#                                     backend=backend,
#                                     **kwargs)
#             network = protocol.networks[0]
#             strings = network.strings
#             for i, string in enumerate(strings):
#                 print(f'Decoded by {i}:', ''.join(chr(int(string[i*8:-~i*8], 2)) for i in range(len(string)//8)))

# %%
def ignore(func):
    def _():
        pass
    return _

# %%


def check_bits(topology:str, backend:str='Qutip', **kwargs):
    protocol = Protocol()

# %% [markdown]
# # Error Calculation (single iteration)
#
# \begin{array}{c c c c c c c c}
# 1 & 0 & 1 & 1 & 0 & 1 & 0 & 0\\
# 0 & 0 & 0 & 0 & 1 & 0 & 0 & 1\\
# 0 & 1 & 0 & 1 & 0 & 1 & 0 & 1\\
# 0 & 0 & 1 & 0 & 1 & 0 & 1 & 0\\
# 1 & 1 & 0 & 1 & 0 & 1 & 0 & 1\\
# 0 & 1 & 0 & 0 & 1 & 0 & 1 & 0
# \end{array}
# \begin{array}{c c c c c c c c}
# \hline
# 2 & 3 & 2 & 3 & 3 & 3 & 2 & 3\\
# \frac{1}{3} & \frac{1}{2} & \frac{1}{3} & \frac{1}{2} & \frac{1}{2} & \frac{1}{2} & \frac{1}{3} & \frac{1}{2}
# \end{array}

# %%


class ErrorAnalyzer:
    @staticmethod
    def analyse(protocol_obj):
        networks = protocol_obj.networks
        full_err_list, mean_list, sd_list = [], [], []
        for i, network in enumerate(networks, 1):
            messages = network.messages
            strings = network.strings[::-1]
            err_list = np.zeros(len(messages[0]))
            for message, string in zip(messages, strings):
                err_list+=np.array([int(m)^int(s) for m, s in zip(message, string)])
            err_list/=len(messages)
            print(err_list)
            err_prct = mean(err_list)*100
            err_sd = stdev(err_list)
            full_err_list.append(err_list)
            mean_list.append(err_prct)
            sd_list.append(err_sd)
            print(f'Average error for iteration {i}: {err_prct}')
            print(f'Deviation in the error for iteration {i}: {err_sd}')
        
        return full_err_list, mean_list, sd_list
    
    @staticmethod
    def full_error_analysis(r:int, topology:str, iterations:int, message_length:int, backend='Qutip', attack=None, **kwargs):
        full_err_list, mean_list, sd_list = [], [], []
        messages_list = [[''.join(str(randint(2)) for i in range(message_length)) for i in range(r)] for i in range(iterations)]
        protocol = Protocol(topology=topology, backend=backend,
                            messages_list=messages_list, attack=attack, **kwargs)
        full_err_list = protocol.full_err_list
        mean_list = protocol.mean_list
        sd_list = protocol.sd_list
        print(mean_list)
        print(f'Error analysis for {attack}')
        full_err_list = np.array(full_err_list)
        plt.figure(figsize=(20, 5))
        bit_error = sum(full_err_list)
        plt.bar(range(len(bit_error)), bit_error)
        plt.xlabel('Bits')
        plt.ylabel(f'Error per bit for {iterations} iterations')
        plt.figure(figsize=(20, 5))
        plt.plot(range(len(mean_list)), mean_list)
        plt.xlabel('Number of Iterations')
        plt.ylabel('Mean error percentage per iteration')
        plt.figure(figsize=(20, 5))
        plt.plot(range(len(sd_list)), sd_list)
        plt.xlabel('Number of Iterations')
        plt.ylabel('Error stdev per iteration')
        plt.show()
        # print(mean_list, sd_list)
        print(f'Total error in the bits over all the {iterations} iterations: {mean(bit_error)}')
        print("Total mean error over all the {} iterations: {}".format(iterations, mean(mean_list)))
        print("Total error stdev over all the {} iterations: {}".format(iterations, mean(sd_list)))


# %%


def string_to_binary(messages):
    print("Converting to binary...")
    strings = [''.join('0'*(8-len(bin(ord(char))[2:]))+bin(ord(char))[2:] for char in message) for message in messages]
    print("Conversion completed")
    
    return strings