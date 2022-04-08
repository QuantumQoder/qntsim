import qntsim
from numpy import random
from qntsim.kernel.timeline import Timeline
from qntsim.topology.topology import Topology
from qntsim.network_management.reservation import Reservation
import json
import sys
import matplotlib.pyplot as plt
import numpy as np

network_config = "/home/aman/SeQUeNCe/Quantum-Networking/example/e91_topology.json"

tl = Timeline(20e12)
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)

def set_parameters(topology: Topology):
   
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 0.9349367588934053
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

  
    DETECTOR_EFFICIENCY = 0.9
    DETECTOR_COUNT_RATE = 5e7
    DETECTOR_RESOLUTION = 100
    for node in topology.get_nodes_by_type("BSMNode"):
        node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
        
   
    SWAP_SUCC_PROB = 0.90
    SWAP_DEGRADATION = 0.99
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)


## Create network topology with ALice Bob And Charlie

##
alice=network_topo.nodes['a']
bob=network_topo.nodes['b']
print(alice)

node1='a'
node2='b'
nm = network_topo.nodes[node1].network_manager
nm.request(node2, start_time=3e12 , end_time=20e12, memory_size=10, target_fidelity=0.5)

analyzerAnglesA = [0, np.pi / 4, np.pi / 2]
analyzerAnglesB = [np.pi / 4, np.pi / 2, 3 * np.pi / 4]
privateKey = []
 
def Alice(alice):
	# Simulator gives entanglement to A
	#Local Task
	# Choose n random basis
	# Measure the entangled qubit in chosen basis
    analyzerChoiceA = npr.random_integers(0, 2, n)
    #QSDetectorpolarization
	#Classical Channel
	#Share basis with Bob
     #BB84s recieved msg

	#Local Task
	#Check which basis match and take these values as keys

def Bob(bob):
	# Simulator gives entanglement to B

	#Local Task
	# Choose n random basis
	# Measure the entangled qubit in chosen basis
    analyzerChoiceB = npr.random_integers(0, 2, n)
	#Classical Channel
	#Share basis with Alice

	#Local Task
	#Check which basis match and these values as keys





#push(): recieve request for key generation
#startprotocol(): begin key gen. set hardware params
#entanglement():
#beginphotonpulse():
#setbasislist(): measurement of basis list
#endphotonpulse():
#message():for classical message