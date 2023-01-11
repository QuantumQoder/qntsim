from random import choices
import random
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.topology.topology import Topology
from qntsim.components.circuit import QutipCircuit
import numpy as np
import math
from qntsim.library.components.qntsim_network import Network
from qntsim.library.protocol_handler.protocol_handler import Protocol
import json
import os


class MdiQSDC():
    
    def random_encode_photons(network:Network):
        print('inside random encode')
        node = network.network.nodes['n1']
        manager = network.manager
        basis = {}
        for info in node.resource_manager.memory_manager:
            if info.state=='RAW':
                key = info.memory.qstate_key
                base = randint(4)
                basis.update({key:base})
                q, r = divmod(base, 2)
                qtc = QutipCircuit(1)
                if r: qtc.x(0)
                if q: qtc.h(0)
                manager.run_circuit(qtc, [key])
            if info.index==2*(network.size+75): break
        
        print('output', network,basis)
        return network, basis

    def authenticate_party(network:Network):
        manager = network.manager
        node = network.network.nodes['n1']
        keys = [info.memory.qstate_key for info in node.resource_manager.memory_manager[:2*network.size+150]]
        keys1 = keys[network.size-25:network.size]
        keys1.extend(keys[2*network.size:2*network.size+75])
        shuffle(keys1)
        keys2 = keys[2*network.size-25:2*network.size]
        keys2.extend(keys[2*network.size+75:])
        shuffle(keys2)
        # print(keys1)
        # print(keys2)
        all_keys = []
        outputs = []
        for keys in zip(keys1, keys2):
            all_keys.append(keys)
            qtc = QutipCircuit(2)
            qtc.cx(0, 1)
            qtc.h(0)
            qtc.measure(0)
            qtc.measure(1)
            outputs.append(manager.run_circuit(qtc, list(keys)))
        err, counter = 0, 0
        for output in outputs:
            (key1, key2) = tuple(output.keys())
            base1 = basis.get(key1)
            base2 = basis.get(key2)
            out1 = output.get(key1)
            out2 = output.get(key2)
            if base1!=None!=base2 and base1//2==base2//2:
                counter+=1
                if (out1 if base1//2 else out2)!=(base1%2)^(base2%2): err+=1
        print(err/counter*100)
        
        return network, err/counter*100

    def swap_entanglement(network:Network):
        node = network.network.nodes['n1']
        manager = network.manager
        e_keys = []
        for info0, info1 in zip(node.resource_manager.memory_manager[:network.size-25],
                                node.resource_manager.memory_manager[network.size:2*network.size-25]):
            qtc = QutipCircuit(2)
            qtc.cx(0, 1)
            qtc.h(0)
            qtc.measure(0)
            qtc.measure(1)
            keys = [info0.memory.qstate_key, info1.memory.qstate_key]
            print(keys)
            e_key = [k for key in keys for k in manager.get(key).keys if k!=key]
            output = manager.run_circuit(qtc, keys)
            c1, c2 = True, False
            for e_k, value in zip(e_key, output.values()):
                qtc = QutipCircuit(1)
                if c1 and value:
                    qtc.x(0)
                    c1, c2 = False, True
                elif c2 and value:
                    qtc.z(0)
                    c1, c2 = True, False
                manager.run_circuit(qtc, [e_k])
            e_keys.append(e_key)
        
        return e_keys
    
    
    def run(self, json_topo,message, attack):
        
        # topo = json.dumps(json_topo, indent = 4)
        # print('json topo', topo,)
        print('pwd', os.getcwd())
        with open('network_topo.json','w') as fp:
            json.dump(json_topo,fp, indent=4)
        # f = open('/code/web/network_topo.json')
        topo = '/code/web/network_topo.json'
        # topo = code/backend/web/network_topo.json
        print("topo", topo)
        network = Network(topology=topo,
                  messages=[message],
                  label='00',
                  size=lambda x:len(x[0])+100,
                  attack=attack)
        
        print('network', network)
        # networks, basis = random_encode_photons(network=network)
        # networks, err_prct = self.authenticate_party(network=network)
        
        print('output', basis, err_prct)
        # protocol = Protocol(platform='qntsim',
        #             messages_list=[message],
        #             topology=topo,
        #             backend='Qutip', attack=attack)
        
        # print('Received messages:', protocol.recv_msgs)
        # print('Error:', mean(protocol.mean_list))
        # network = Network(topology=json.dumps(json_topo),
        #           messages=message,
        #           label='00')
        
        # # print(network.dump())
        # print(network.size)
        