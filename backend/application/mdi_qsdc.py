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
        protocol = Protocol(platform='qntsim',
                    messages_list=[message],
                    topology=topo,
                    backend='Qutip', attack=attack)
        
        print('Received messages:', protocol.recv_msgs)
        print('Error:', mean(protocol.mean_list))
        # network = Network(topology=json.dumps(json_topo),
        #           messages=message,
        #           label='00')
        
        # # print(network.dump())
        # print(network.size)
        