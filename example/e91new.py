from django.dispatch import receiver
import qntsim
from numpy import random
from qntsim.components.circuit import Circuit
from qntsim.kernel.timeline import Timeline
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
from qntsim.protocol import Protocol
from qntsim.topology.node import QuantumRouter
from qntsim.topology.topology import Topology
from qntsim.network_management.reservation import Reservation
from qntsim.resource_management.memory_manager import MemoryInfo
import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister

network_config = "/home/aman/Sequence/test/Quantum-Networking/example/e91_topology.json"

tl = Timeline(10e12)
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
# alice=network_topo.nodes['a']
# bob=network_topo.nodes['b']
# print('alice',alice)

# alice = QuantumRouter("alice", tl, memo_size=50)
# bob = QuantumRouter("bob", tl, memo_size=50)
# print('alice bob',alice.name,bob.name)
# 
node1='v0'
node2='v1'
# tm = network_topo.nodes[node1].transport_manager
# tm.request(node2,5e12,10,20e12,0,5e12)
alice_result=[]
bob_result=[]
alice=network_topo.nodes[node1]
bob = network_topo.nodes[node2]
print("a memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes[node1].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


# tl.stop_time=10e12

# node1='v0'
# node2='v4'
# tm=network_topo.nodes[node1].transport_manager
# qr = QuantumRegister(2, name="qr")
# cr = ClassicalRegister(4, name="cr")

# circuit=QuantumCircuit(qr,cr)
# print('app circuit',tl.quantum_manager.meas_result)


def request_entanglements(sender,receiver):
    sender.transport_manager.request(receiver.owner.name,5e12,49,10e12,0,5e12)
    print()
    





def roles():
    sender=alice
    receiver=bob
    print('sender, receiver',sender.owner.name,receiver.owner.name)
    request_entanglements(sender,receiver)

roles()


tl.init()
tl.run()


print("alice memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes[node1].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    # print('memory array',info.memory.qstate_key)
    key=info.memory.qstate_key
    # print('keyss',key)
    qm=network_topo.nodes[node1].timeline.quantum_manager
    state=qm.get(key)
    print('qm state',state)
    circuit1=Circuit(1)
    circuit1.x(0)
    circuit1.measure(0)
    # print('ck1',circuit1)
    op_alice=qm.run_circuit(circuit1,[key])
    alice_result.append(op_alice)
    op=state.state
    print('output',op_alice)
    mem=MemoryInfo(info.memory,info.index)
    print('meme',mem.memory.result)
    # qm.get(key)
    # print('qstatss',qm.get(key))
    # for memory in info.memory.memories:
    #     print('memories',memory)

print("alice memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes[node2].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    # print('memory array',info.memory.qstate_key)
    key=info.memory.qstate_key
    # print('keyss',key)
    qm=network_topo.nodes[node1].timeline.quantum_manager
    state=qm.get(key)
    print('qm state2',state)
    circuit1=Circuit(1)
    circuit1.x(0)
    circuit1.measure(0)
    # print('ck1',circuit1)
    op_bob=qm.run_circuit(circuit1,[key])
    bob_result.append(op_bob)
    op=state.state
    print('output2',op_bob)

def alice_meas():
    alice_choice=np.random.randint(0,2,40)
    print('alice choice',alice_choice)
    meas_result=[]
    for info in alice.resource_manager.memory_manager:
        list=info.memory.result.values()
        meas_result.append(list)
        print('alice mem result',list,info.memory.result)
    print('list',meas_result)

def bob_meas():
    bob_choice=np.random.randint(0,2,40)
    print('bob choice',bob_choice)
    for info in bob.resource_manager.memory_manager:
        print('bob mem result',info.memory.result)

alice_meas()
bob_meas()

print('alice results',alice_result)
print('bob results',bob_result)

# class Alice(Protocol):

#     def __init__(self,own,role) -> None:
#         self.own=own
#         self.role=role

#     def request(self):

#         print('self',self)

#     def select_basis(n):
#         alice_choice=np.random.randint(0,2,n)

#     def measure_qubits(alice_choice):
#         print()
#         # Returns measurement result list

# class Bob():

#     def __init__(self,own,role) -> None:
#         self.own=own
#         self.role=role

#     def select_basis(n):
#         bob_choice=np.random.randint(0,2,n)

#     def measure_qubits(bob_choice):
#         print()
#         # Returns measurement result list


# class Key():

#     def __init__(self) -> None:
#         alice_key=[]
#         bob_key=[]

#     def compare_keys():
#         print()

# ob=Alice(alice,0)
# ob.request
