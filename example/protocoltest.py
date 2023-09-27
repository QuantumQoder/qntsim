import qntsim
from numpy import random
from qntsim.kernel.timeline import Timeline
from qntsim.kernel.process import Process
from qntsim.kernel.event import Event
from qntsim.topology.topology import Topology
from qntsim.network_management.reservation import Reservation
import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from pyvis.network import Network
import webbrowser

#random.seed(0)
network_config = "/home/aman/Sequence/test/Quantum-Networking/example/network_topology.json"

n,k,lamda=20,6,40

tl = Timeline(4e12)
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)
# network_topo.create_random_topology(n)



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
        
   
    SWAP_SUCC_PROB = 0.9
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
'''
node1='v0'
node2='v2'
nm=network_topo.nodes[node1].network_manager
nm.createvirtualrequest(node2, start_time=1e12, end_time=10e12, memory_size=3, target_fidelity= 0.5)

node1='v2'
node2='v3'
nm=network_topo.nodes[node1].network_manager
nm.createvirtualrequest(node2, start_time=2e12, end_time=10e12, memory_size=4, target_fidelity= 0.5)
'''
node1='v1'
node2='v2'
nm=network_topo.nodes[node1].network_manager
nm.createvirtualrequest(node2, start_time=2e12, end_time=10e12, memory_size=3, target_fidelity= 0.5)

node1='v3'
node2='v4'
nm=network_topo.nodes[node1].network_manager
nm.createvirtualrequest(node2, start_time=2e12, end_time=10e12, memory_size=3, target_fidelity= 0.5)


# node1='v1'
# node2='v4'
# nm=network_topo.nodes[node1].network_manager
# nm.createvirtualrequest(node2, start_time=3e12, end_time=10e12, memory_size=3, target_fidelity= 0.5)

# node1='v1'
# node2='v3'
# nm=network_topo.nodes[node1].network_manager
# nm.createvirtualrequest(node2, start_time=3e12, end_time=10e12, memory_size=3, target_fidelity= 0.5)


tl.init()
tl.run()

# print("v1 memories")
# print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v1"].resource_manager.memory_manager:
    # print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


tl.stop_time=10e12

node1='v0'
node2='v4'
tm=network_topo.nodes[node1].transport_manager
tm.request(node2,5e12,10,10e12,1,5e9)

# node1='v1'
# node2='v3'
# tm=network_topo.nodes[node1].transport_manager
# tm.request(node2,6e12,3,10e12,1,5e9)

# node1='v2'
# node2='v4'
# tm=network_topo.nodes[node1].transport_manager
# tm.request(node2,7e12,3,10e12,1,5e9)


# tl.init()
tl.run()


# print("v0 memories")
# print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v0"].resource_manager.memory_manager:
    # print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


# print("v1 memories")
# print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v1"].resource_manager.memory_manager:
    # print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

# print("v2 memories")
# print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v2"].resource_manager.memory_manager:
    # print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

# print("v3 memories")
# print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v3"].resource_manager.memory_manager:
    # print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

# print("v4 memories")
# print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v4"].resource_manager.memory_manager:
    # print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

tranmap={}
netmap={}
reqmap={}
def getmaps():
    for i in range(0,5):
        node='v'+str(i)
        for tpid,TpObj in network_topo.nodes[node].transport_manager.transportprotocolmap.items():
            # print('tpid',tpid)
            tranmap[tpid]=TpObj
        for netid,[tpd,status] in network_topo.nodes[node].network_manager.networkmap.items():
            netmap[netid]=[tpd,status]
        for reqid,resobj in network_topo.nodes[node].network_manager.requests.items():
            reqmap[reqid]=resobj
getmaps()
# print(tranmap)
# print(netmap)
# print(reqmap)