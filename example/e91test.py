
import itertools
from random import choices
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

network_config = "/home/aman/Sequence/test/Quantum-Networking/example/network_topology.json"

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

n=99

alice=network_topo.nodes['v0']
bob = network_topo.nodes['v1']

print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in alice.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


def request_entanglements(sender,receiver):
    sender.transport_manager.request(receiver.owner.name,5e12,n,10e12,0,.7,5e12)
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
for info in alice.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("alice memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in bob.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

def measurement(qm,choice, key):
    
    if choice == 1:       #X observable
        circ=Circuit(1)
        circ.h(0)
        circ.measure(0)
        output=qm.run_circuit(circ,[key])
    if choice == 2:         #W observable
        circ=Circuit(1)
        circ.s(0)
        # circ.
        circ.h(0)
        circ.t(0)
        circ.h(0)
        circ.measure(0)
        output=qm.run_circuit(circ,[key])
    if choice == 3:         #Z observable
        circ=Circuit(1)
        circ.measure(0)
        output=qm.run_circuit(circ,[key])
    if choice == 4:         #V observable
        circ=Circuit(1)
        circ.s(0)
        circ.h(0)
        circ.tdg(0)
        circ.h(0)
        circ.measure(0)
        output=qm.run_circuit(circ,[key])
    print('output',output)
    return output


def alice_measurement():
    choice=[1,2,3]
    qm_alice=alice.timeline.quantum_manager
    meas_results_alice=[]
    alice_choice_list=[]
    for info in alice.resource_manager.memory_manager:
        key=info.memory.qstate_key
        state=qm_alice.get(key)
        # print('initial state',info.index,info.state,type(state))
        alice_choice=np.random.choice(choice)
        # print('keys',key)
        # print('alice choice',alice_choice)
        meas_results_alice.append(measurement(qm_alice,alice_choice,key))
        alice_choice_list.append(alice_choice)
    # print('Alice measuremnt reuslts',meas_results_alice)
    return alice_choice_list,meas_results_alice
  

def bob_measurement():
    qm_bob=bob.timeline.quantum_manager
    meas_results_bob=[]
    bob_choice_list=[]
    choice=[2,3,4]
    for info in alice.resource_manager.memory_manager:
        key=info.memory.qstate_key
        bob_choice=np.random.choice(choice)
        # print('keys',key)
        # print('bob choice',bob_choice)
        meas_results_bob.append(measurement(qm_bob,bob_choice,key))
        bob_choice_list.append(bob_choice)
    # print('Bob measuremnt results',meas_results_bob)
    return bob_choice_list,meas_results_bob
# qm_alice=alice.timeline.quantum_manager
# qm_bob=bob.timeline.quantum_manager
# for i in range(5):
#     j=0
#     meas_results_alice=measurement(qm_alice,1,j)
#     meas_results_alice=measurement(qm_bob,2,j+50)
#     j+=1

def chsh_correlation(alice_results,bob_results,alice_choice,bob_choice):

    countA1B2=[0,0,0,0]
    countA1B4=[0,0,0,0]
    countA3B2=[0,0,0,0]
    countA3B4=[0,0,0,0]
    check_list = ['00','01','10','11']
    res=[]
    # print('alcie results',alice_results)
    # for pair in itertools.product(alice_results,bob_results):
    #     res.append(''.join(map(str,pair)))
    for i in range(len(alice_results)):
        # res[i]=str(alice_results[i])+str(bob_results[i])
        res.append((alice_results[i],bob_results[i]))
    print('reslist',res)
    for i in range(n):
        res2=''.join(map(str,res[i]))
        # print('aa',res[i],alice_choice[i],bob_choice[i])
        if (alice_choice[i]==1 and bob_choice[i]==2):
            for j in range(4):
                # print('rs and check',res[i],check_list[j])
                if res2 == check_list[j]:
                    countA1B2[j] +=1
        if (alice_choice[i]==1 and bob_choice[i]==4):
            for j in range(4):
                if res2 == check_list[j]:
                    countA1B4[j] +=1

        if (alice_choice[i]==3 and bob_choice[i]==2):
            for j in range(4):
                if res2 == check_list[j]:
                    countA3B2[j] +=1
        
        if (alice_choice[i]==3 and bob_choice[i]==4):
            for j in range(4):
                if res2 == check_list[j]:
                    countA3B4[j] +=1

    print('countA1B2', countA1B2)
    print('countA1B2', countA1B4)
    print('countA1B2', countA3B2)
    print('countA1B2', countA3B4)

    total12=sum(countA1B2)
    total14=sum(countA1B4)
    total32=sum(countA3B2)
    total34=sum(countA3B4)

    expect12 = (countA1B2[0]-countA1B2[1]-countA1B2[2]+countA1B2[3])/total12
    expect14 = (countA1B4[0]-countA1B4[1]-countA1B4[2]+countA1B4[3])/total14
    expect32 = (countA3B2[0]-countA3B2[1]-countA3B2[2]+countA3B2[3])/total32
    expect34 = (countA3B4[0]-countA3B4[1]-countA3B4[2]+countA3B4[3])/total34

    corr=expect12-expect14+expect32+expect34

    return corr

def runE91():
    alice_choice,alice_meas=alice_measurement()
    bob_choice,bob_meas=bob_measurement()
    key_mismatch=0
    alice_key,bob_key=[],[]
    alice_results, bob_results =[],[]
    print('Alice Measurements', alice_meas)
    print('Bob Measuremenst', bob_meas)
    for i in range(n):
        alice_results.append(alice_meas[i].get(i)) 
        bob_results.append(bob_meas[i].get(i))
        if (alice_choice[i]==2 and bob_choice[i]==2) or (alice_choice[i]==3 and bob_choice[i]==3):
            print('Base match',alice_meas[i].get(i),bob_meas[i].get(i))
            alice_key.append(alice_meas[i].get(i))
            bob_key.append(bob_meas[i].get(i))
    for j in range(len(alice_key)):
        if alice_key[j] != bob_key[j]:
            key_mismatch += 1
    print('Alice choicec',alice_choice)
    print('Bob choicec',bob_choice)
    print('Alice results',alice_results)
    print('Bob results',bob_results)
    print('Alice keys', alice_key)
    print('Bob keys', bob_key)
    print('Key length',len(alice_key))
    print('Mismatched keys', key_mismatch)
    chsh_value=chsh_correlation(alice_results,bob_results,alice_choice,bob_choice)
    print('Correlation value', str(round(chsh_value,3)))
runE91()

# if (aliceMeasurementChoices[i] == 2 and bobMeasurementChoices[i] == 1) or (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 2):
#         aliceKey.append(aliceResults[i]) # record the i-th result obtained by Alice as the bit of the secret key k








