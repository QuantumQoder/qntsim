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

class MdiQSDC():
    
    
    def run(self, message, attack):
        
        topo = {
            "cchannels_table": {
                "labels": ["n0", "s0", "n1", "s1", "n2"],
                "table": [[0, 1000000000.0, 1000000000.0, 1000000000.0, 1000000000.0],
                        [1000000000.0, 0, 1000000000.0, 1000000000.0, 1000000000.0],
                        [1000000000.0, 1000000000.0, 0, 1000000000.0, 1000000000.0],
                        [1000000000.0, 1000000000.0, 1000000000.0, 0, 1000000000.0],
                        [1000000000.0, 1000000000.0, 1000000000.0, 1000000000.0, 0]],
                "type": "RT"
            },
            "end_node": {
                "n0": "s0",
                "n1": "s1",
                "n2": "s1"
            },
            "qconnections": [
                {
                    "attenuation": 1e-05,
                    "distance": 70,
                    "node1": "n0",
                    "node2": "s0"
                },
                {
                    "attenuation": 1e-05,
                    "distance": 70,
                    "node1": "s0",
                    "node2": "n1"
                },
                {
                    "attenuation": 1e-05,
                    "distance": 70,
                    "node1": "n1",
                    "node2": "s1"
                },
                {
                    "attenuation": 1e-05,
                    "distance": 70,
                    "node1": "s1",
                    "node2": "n2"
                }
            ],
            "service_node": [
                "s0",
                "s1"
            ]
        }
        messages = ['hi', 'mi']
        protocol = Protocol(platform='qntsim',
                    messages_list=[messages],
                    topology=topo,
                    backend='Qutip', attack='DoS')
        
        print('Received messages:', protocol.recv_msgs)
        print('Error:', mean(protocol.mean_list))
        network = Network(topology=str(topo),
                  messages=message,
                  label='00')
        
        # print(network.dump())
        print(network.size)
        