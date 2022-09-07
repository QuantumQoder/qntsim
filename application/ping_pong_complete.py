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
import time

network_config = "network_topology.json"

tl = Timeline(10e12)
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)

def set_parameters(topology: Topology):
   
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 1
    #MEMO_FIDELITY = 0.9349367588934053
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

  
    DETECTOR_EFFICIENCY = 1
    #DETECTOR_EFFICIENCY = 0.2
    DETECTOR_COUNT_RATE = 5e7
    #DETECTOR_RESOLUTION = 70
    DETECTOR_RESOLUTION = 100
    for node in topology.get_nodes_by_type("BSMNode"):
        node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)

bob = network_topo.nodes['v0']
alice = network_topo.nodes['v1']

"""print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in bob.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
"""

#I need to request Bell entanglemenets \psi_+ , \psi_-
def request_entanglements(sender, receiver, n=50):
    sender.transport_manager.request(receiver.owner.name,5e12,n,10e12,0,.7,5e12)
    print()

def roles():
    sender=bob
    receiver=alice
    print('sender, receiver',sender.owner.name,receiver.owner.name)
    request_entanglements(bob,alice, n= 200)

roles()

tl.init()
tl.run()

print("bob memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in bob.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
print("alice memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in alice.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

def z_measurement(qm, key):
    """
    Method measures a qubit in the z basis

    Parameters :
    qm : quantum manager on which key is supposed to be measured
    key : key pointing to the qubits prepared 
    
    Returns : Measurement results
    """
    circ=Circuit(1)       #Z Basis measurement
    circ.measure(0)
    output=qm.run_circuit(circ,[key])

    return output

def check_phi_plus(state):
    """
    Method checks if state is  pure phi_plus 

    Parameters :
    state : Of type qutip state which needs to checked

    Returns : True or False
    """
    assert(len(state) == 4)

    if abs(state[0]*np.sqrt(2) - 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) - 1)  < 1e-5:
        return True

    elif abs(state[0]*np.sqrt(2) + 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) + 1)  < 1e-5:
        return True

    else : return False

def create_psi_plus_entanglement():
    """
    Method creates pure psi_plus entanglements between Alice and Bob

    Parameters : None
    
    Returns : None  
    """
    entangled_keys = []
    qm_alice=alice.timeline.quantum_manager

    for info in bob.resource_manager.memory_manager:

        key=info.memory.qstate_key
        state=qm_alice.get(key)

        #Filtering out unentangeled qubits
        if(len(state.keys) == 1) : continue

        #Filtering out phi_minus, created randomly, from phi_plus
        if(not check_phi_plus(state.state)):continue

        print(state)

        to_psi_plus(qm_alice, state.keys)
        entangled_keys.append(key)

    return entangled_keys

def to_psi_plus(qm, keys):
    """
    Method transforms bell pair from phi_plus to psi_plus

    Parameters :
    qm : quantum manager on which bits are stored
    keys : keys pointing to the qubits prepared 
    
    Returns : None 
    """

    circ=Circuit(2)   
    #change to bell basis
    circ.cx(0,1)
    circ.h(0)   

    #Changing to psi_+
    circ.x(1)

    #back to computational basiss
    circ.h(0) 
    circ.cx(0,1)
    qm.run_circuit(circ, keys)

    #return is_psi_plus

def protocol_c(entangled_keys):
    """
    Method runs the Protocol C

    Parameters :
    entangled_keys : keys pointing to the qubits prepared for x_n
    
    Returns : Measurement results of Protocol C
    """

    meas_results_alice, meas_results_bob = [] , [] 
    qm_alice=alice.timeline.quantum_manager

    for info in alice.resource_manager.memory_manager:

        key=info.memory.qstate_key
        state=qm_alice.get(key)

        if (key - 300) not in entangled_keys: continue

        #print(state)

        meas_results_alice.append(z_measurement(qm_alice, key))
        #state=qm_alice.get(key)
        #print(state)
    # print('Alice measuremnt reuslts',meas_results_alice)

    qm_bob=bob.timeline.quantum_manager

    for info in bob.resource_manager.memory_manager:
        key=info.memory.qstate_key
        state=qm_bob.get(key)

        if key not in entangled_keys : continue

        meas_results_bob.append(z_measurement(qm_bob, key))

    return meas_results_alice, meas_results_bob

def encode_and_bell_measure(x_n, qm, keys):
    """
    Method encodes the message on an an entangled pair, and then 
    measures it in bell basis

    Parameters :
    x_n : The bit that needs to be sent
    qm : quantum manager on which key is supposed to be measured
    keys : keys pointing to the qubits prepared 
    
    Returns : Measurement results 
    """
    qc=Circuit(2) 
    if(x_n == '1'):
        qc.z(1)
    qc.cx(0,1)
    qc.h(0)
    qc.measure(0)
    qc.measure(1)
    output=qm.run_circuit(qc,keys)
    print("message -> ", x_n)
    print(output)
    return output

def protocol_m(x_n, current_keys):
    """
    Method runs the Protocol M for one bit

    Parameters :
    x_n : The bit that needs to be sent
    current_keys : keys pointing to the qubits prepared for x_n
    
    Returns : Measurement results of Protocol M
    """

    meas_results_bob = []
    qm_bob=bob.timeline.quantum_manager

    for info in bob.resource_manager.memory_manager:
        key=info.memory.qstate_key
        if key in current_keys:
            #print("true")
            meas_results_bob.append(encode_and_bell_measure(x_n, qm_bob, [key, key+300]))
    
    return meas_results_bob


def get_percentage_accurate(bell_results, x_n):
    """
    Method takes in Bell basis result and bit to calculate the accuracy 

    Parameters :
    bell_results : takes in the Bell basis measurement result
    x_n : The bit that needs to be sent
    
    Returns : Percentage of results that correspond to the correct bit
    """
    count = 0
    assert x_n in ['0', '1']

    if x_n == '0':
        for result in bell_results:
            if list(result.values()) == [0, 1]:
                count+=1


        return count/len(bell_results)


    elif x_n == '1':
        for result in bell_results:
            if list(result.values()) == [1, 1]:
                count+=1

        return count/len(bell_results)


def decode_bell(bell_results):
    """
    Method takes in Bell basis result and returns bit corresponding to that

    Parameters :
    bell_results : takes in the Bell basis measurement result

    Returns : Bell basis value if among the expected results, '#' otherwise
    """
    list_vals = list(bell_results.values())
    if list_vals == [1,1]:
        return '1'
    elif list_vals == [0,1]:
        return '0'
    else : return '#'

def one_bit_ping_pong(x_n, c, sequence_length, entangled_keys, round_num):

    """
    This method runs the ping-pong protocol for one message bit.
    It raises errors in case of any eavesdropping.

    Parameters :
    x_n : The bit that needs to be sent
    c : probability to switch to Protcol c
    sequence_length : The number of qubits the user wants to use for each message bit
    entangled_keys : The keys pointing to the entangled memories
    round_num : Which round are we on in the ping-pong process
    
    Returns : message decoded and the updated round number
            -1 if Protocol fails
    """

    #print("round_num ", round_num)
    memory_size = 10

    current_keys = entangled_keys[round_num*sequence_length : (round_num + 1)*sequence_length]

    draw = random.uniform(0, 1)
    while (draw < c):
        print("Switching to protocol c ")
        meas_results_alice, meas_results_bob = protocol_c(current_keys)

        for i in range(len(meas_results_alice)):
            if not (list(meas_results_alice[i].values())[0] == 1 - list(meas_results_bob[i].values())[0]):
                print("Alice and Bob get same states -> Stop Protocol!")
                return -1

        print("Protocol c passes through without trouble! No Eve detected yet")
        draw = random.uniform(0, 1)
        #print("meas_results_alice : ", meas_results_alice)
        #print("meas_results_bob : ", meas_results_bob)
        round_num = round_num + 1
        current_keys = entangled_keys[round_num*sequence_length : (round_num + 1)*sequence_length]

    if (draw > c) : 
        bell_results = protocol_m(x_n, current_keys)
        round_num = round_num + 1
        print("HERE", bell_results)
        accuracy = get_percentage_accurate(bell_results, x_n)
        print(accuracy)
        if accuracy == 1 :
            return decode_bell(bell_results[0]), round_num

        else : 
            print("protocol m has some impurities; accuracy of transmission is ", accuracy)
            return -1

def run_ping_pong(message = "0"):
    """
    This method just runs the ping-pong protocol and calls all the methods.
    It raises errors in case of any eavesdropping.

    Parameters :
    message : The message that needs to be sent via the QSDC Protocol

    Returns : None
    """
    n = 0
    c = 0.2
    sequence_length = 4
    bob_message = ""
    entangled_keys = create_psi_plus_entanglement()
    round_num = 0
    
    #print(entangled_keys)

    while(n < len(message)):
        n = n+1

        result, round_num = one_bit_ping_pong(message[n-1], c, sequence_length, entangled_keys, round_num)

        if(result == -1): 
            print("Protocol doesn't run because of the aforesaid mistakes!")

        bob_message = bob_message + result

    print(f"Message transmitted : {message}")
    print(f"Message recieved : {bob_message}")

start = time.time()
run_ping_pong(message = "010110100")
end = time.time()
print("time took : ",  end - start)

# In the request if the runtime is till the simulation, then memory will be sequentially allotted 
# For quantum router , you can directly change memory size

# Ask if we can divide task for different slots
# Ask if we can increase memory for each node (currently it is 100)
# Ask how to take care of phi plus vs phi minus generation
# generalize to multiple bits


# if (aliceMeasurementChoices[i] == 2 and bobMeasurementChoices[i] == 1) or (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 2):
#         aliceKey.append(aliceResults[i]) # record the i-th result obtained by Alice as the bit of the secret key k

## Initilize new state as required, and you get key corresponding to these states
# key = qm_alice.new([amp1, amp2])