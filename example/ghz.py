from qntsim.kernel.timeline import Timeline

Timeline.DLCZ=False
Timeline.bk=True
import math

from qiskit import *
from qiskit.extensions import Initialize
#from qiskit.ignis.verification import marginal_counts
from qiskit.quantum_info import random_statevector
from qntsim.components.circuit import Circuit, QutipCircuit
from qntsim.topology.topology import Topology
from qutip.qip.circuit import Gate, QubitCircuit
from qutip.qip.operations import gate_sequence_product
from tabulate import tabulate

#random.seed(0)
network_config = "/home/aman/QNTSim/QNTSim/example/ghz_topo.json"

n,k,lamda=10,6,40

tl = Timeline(10e12,"Qutip")
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)
# network_topo.create_random_topology(n,network_config)



def set_parameters(topology: Topology):
   
    MEMO_FREQ = 2e4
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 0.9349367588934053
    for node in topology.get_nodes_by_type("EndNode"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)
    
    for node in topology.get_nodes_by_type("ServiceNode"):
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
    # for node in topology.get_nodes_by_type("QuantumRouter"):
    #     node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
    #     node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)


node1='a'
node2='b'
node3='c'
node4='s1'

# a ==>s1
tm=network_topo.nodes[node1].transport_manager
tm.request(node4, start_time=5e12,size=1, end_time=10e12, priority=0 , target_fidelity= 0.5, timeout=2e12) 

# b ==>s1
tm=network_topo.nodes[node2].transport_manager
tm.request(node4, start_time=5e12,size=1, end_time=10e12, priority=0 , target_fidelity= 0.5, timeout=2e12) 

# c ==> s1
tm=network_topo.nodes[node3].transport_manager
tm.request(node4, start_time=5e12,size=1, end_time=10e12, priority=0 , target_fidelity= 0.5, timeout=2e12) 




tl.init()
tl.run()



table=[]
# print('a memories')
for info in network_topo.nodes["a"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'a',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])

# print(tabulate(table, headers=['Index','Source node', 'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
# print('b memories')
for info in network_topo.nodes["b"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'b',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])

# print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
# print('c memories')
for info in network_topo.nodes["c"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'c',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])

# print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))

table=[]
# print('s1 memories')
for info in network_topo.nodes["s1"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s1',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])

# print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))








def alice_keys():
    qm_alice = network_topo.nodes[node1].timeline.quantum_manager
    for mem_info in network_topo.nodes[node1].resource_manager.memory_manager:
        if mem_info.state == 'ENTANGLED':
            key=mem_info.memory.qstate_key
            state= qm_alice.get(key)
            # print("alice keys",key, state)
            return qm_alice,key,state

def bob_keys():
    qm_bob = network_topo.nodes[node2].timeline.quantum_manager
    for mem_info in network_topo.nodes[node2].resource_manager.memory_manager:
        if mem_info.state == 'ENTANGLED':
            key=mem_info.memory.qstate_key
            state= qm_bob.get(key)
            # print("bob keys",key,state)
            return qm_bob,key,state

def charlie_keys():
    qm_charlie = network_topo.nodes[node3].timeline.quantum_manager
    for mem_info in network_topo.nodes[node3].resource_manager.memory_manager:
        if mem_info.state == 'ENTANGLED':
            key=mem_info.memory.qstate_key
            state= qm_charlie.get(key)
            # print("charlie keys",key,state)
            return qm_charlie,key,state

def middle_keys():
    qm_middle = network_topo.nodes[node4].timeline.quantum_manager
    for mem_info in network_topo.nodes[node4].resource_manager.memory_manager:
        # # print('middle memory info', mem_info)
        if mem_info.state == 'ENTANGLED':
            key=mem_info.memory.qstate_key
            state= qm_middle.get(key)
            # print("middle keys",key,state)
            return qm_middle,key,state


alice_keys()
bob_keys()
charlie_keys()
middle_keys()

def perform_ghz():

    qm_alice,alice_key,state=alice_keys()
    # print('Alice',qm_alice,alice_key,state)
    qm_bob,bob_key,state=bob_keys()
    qm_charlie,charlie_key,state=charlie_keys()
    qm_middle,middle_key,state=middle_keys()

    circ = QutipCircuit(3)
    circ.cx(0,2)
    circ.cx(0,1)
    circ.h(0)
    circ.measure(0)
    circ.measure(1)
    circ.measure(2)
    output = qm_middle.run_circuit(circ,[alice_key,bob_key,charlie_key])
    # print("Output", output)
    # print("\nState\n",  qm_middle.get(middle_key).state)
    # # print("Output", output, qm_middle.get(alice_key))


perform_ghz()