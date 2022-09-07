import itertools
from random import choices
import random
import qntsim
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

network_config = "network_topo_2.json"

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
        
   
   #What is swap probabilities
    SWAP_SUCC_PROB = 0.90
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

n=100

alice = network_topo.nodes['v0']
bob = network_topo.nodes['v1']

print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in bob.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


#I need to request Bell entanglemenets \psi_+ , \psi_-
def request_entanglements(sender, receiver):
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
print("bob memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in bob.resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

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

def create_entanglement():
    """
    Method creates pure phi plus entanglement between alice and bob nodes

    Parameters : None

    Returns : entangled keys, and a dictionary between alice's keys and bob's keys
    connecting their respective entangled keys
    """
    entangled_keys = []
    qm_alice=alice.timeline.quantum_manager
    qm_bob=bob.timeline.quantum_manager
    alice_bob_keys_dict = {}

    for info in alice.resource_manager.memory_manager:

        key=info.memory.qstate_key
        state=qm_alice.get(key)

        #Filtering out unentangeled qubits
        if(len(state.keys) == 1) : continue

        #Filtering out wrong states created
        if(not check_phi_plus(state.state)):continue

        entangled_keys.append(key)

    for info in bob.resource_manager.memory_manager:

        key=info.memory.qstate_key
        state=qm_bob.get(key)


        if(len(state.keys) == 1) : continue

        # I have to do both order because sometimes 
        # keys come in the form of [alice_key, bob_key]
        # and sometimes [bob_key, alice_key]
        # and I don't know why they happen either way
        if state.keys[0] in entangled_keys :
            alice_bob_keys_dict[state.keys[0]] = state.keys[1]

        if state.keys[1] in entangled_keys :
            alice_bob_keys_dict[state.keys[1]] = state.keys[0]

    return entangled_keys, alice_bob_keys_dict


def single_message_QSDC_entngl(qm, message, keys):
    """
    Method creates bell pair for particular choice of bit pair

    Parameters :
    qm : quantum manager on which key is supposed to be measured
    message : message bits to be encoded
    keys : keys pointing to the qubits prepared 

    Returns : None
    """
    circ=Circuit(2)   
    #change to bell basis
    circ.cx(0,1)
    circ.h(0)   


    #entangling choices!
    if message[0] == '1':circ.x(0)
    if message[1] == '1':circ.x(1)

    #back to computational basis
    circ.h(0) 
    circ.cx(0,1)

    qm.run_circuit(circ, keys)


def generate_QSDC_entanglement(qm, message, entangled_keys, alice_bob_keys_dict):
    """
    Method generates all entanglements for QSDC protocol, corresponding to entire 
    message length

    Parameters :
    qm : quantum manager on which key is supposed to be measured
    message : entire message to be encoded
    entangled_keys : keys pointing to the entangled qubits prepared 
    alice_bob_keys_dict : dictionary between alice's entangled keys and bob's entangled keys

    Returns : keys used for message encoding
    """
    sequence_len = 1
    used_keys = []
    message_transmitted = ""
    for n in range(0, int(len(message)/2)) : 
        keys = entangled_keys[n:n+sequence_len]
        key_pair = [[key, alice_bob_keys_dict[key]] for key in keys]
        for pairs in key_pair:
            single_message_QSDC_entngl(qm, message[2*n:2*n+2], pairs)

        for key in keys:
            used_keys.append(key)
    return used_keys
        

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

def eavesdrop_check(entangled_keys, message, alice_bob_keys_dict):
    """
    Method checks for eavesdrop in the protocol

    Parameters :
    entangled_keys : keys pointing to the entangled qubits prepared 
    message : message bits to be encoded
    alice_bob_keys_dict : dictionary between alice's entangled keys and bob's entangled keys
    
    Returns : Keys chosen to measure for eavesdrop check
    """
    qm_alice = alice.timeline.quantum_manager
    qm_bob = bob.timeline.quantum_manager
    alice_meas, bob_meas = [], []
    choose_pos = random.sample(range(len(entangled_keys)), int(len(entangled_keys)/4))
    choose_keys = []
    print("message thrown out because we measure it for eavesdrop check : ", )
    thrown_message = []
    for pos in choose_pos:
        alice_meas.append(z_measurement(qm_alice, entangled_keys[pos]))
        bob_meas.append(z_measurement(qm_bob, alice_bob_keys_dict[entangled_keys[pos]]))
        print(message[2*pos:2*pos+2], " at position ", 2*pos)
        thrown_message.append(message[2*pos:2*pos+2])
        choose_keys.append(entangled_keys[pos])

    for i in range(len(alice_meas)):
        a_val = list(alice_meas[i].values())[0]
        b_val = list(bob_meas[i].values())[0]

        if thrown_message[i] == "00" or thrown_message[i] == "10":
            assert a_val == b_val
        else : assert a_val == 1 - b_val

    print("eavesdrop check passed!")
    print(alice_meas, bob_meas)
    return choose_keys

def bell_measure(qm, keys):
    """
    Method returns measurement in ball basis

    Parameters :
    qm : quantum manager on which key is supposed to be measured
    keys : keys pointing to the qubits prepared 
    
    Returns : Measurement result
    """
    qc=Circuit(2) 
    qc.cx(0,1)
    qc.h(0)
    qc.measure(0)
    qc.measure(1)
    output=qm.run_circuit(qc,keys)
    #print(output)
    #print(list(output.values()))
    return output

def run_first_QSDC():
    """
    This method just runs the first QSDC protocol and calls all the methods.
    It raises errors in case of any eavesdropping.

    Parameters : None

    Returns : None
    """
    message = "110011001001010101010100"
    assert len(message)%2 == 0
    entangled_keys, alice_bob_keys_dict = create_entanglement()
    qm_alice = alice.timeline.quantum_manager

    protocol_keys = generate_QSDC_entanglement(qm_alice, message, entangled_keys, alice_bob_keys_dict)
    message_received = ""
    c = 0
    sequence_len = 1
    measured_keys = eavesdrop_check(protocol_keys, message, alice_bob_keys_dict)

    for keys in protocol_keys:
        if keys in measured_keys:
            message_received += "__"
            continue
        #if (c == len(message)):break

        output = bell_measure(qm_alice, [keys, alice_bob_keys_dict[keys]])
        message_received += str(output[keys]) + str(output[alice_bob_keys_dict[keys]])
        c+=2

    final_key = message_received.replace("__", "")
    print(f"key transmitted : \t{message}")
    print(f"key shared received : \t{message_received}")
    print(f"Final key : {final_key}")

run_first_QSDC()

# In the request if the runtime is till the simulation, then memory will be sequentially allotted 
# For quantum router , you can directly change memory size

# Ask if we can divide task for different slots
# Ask if we can increase memory for each node (currently it is 100)
# Ask how to take care of phi plus vs phi minus generation
# generalize to multiple bits


# if (aliceMeasurementChoices[i] == 2 and bobMeasurementChoices[i] == 1) or (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 2):
#         aliceKey.append(aliceResults[i]) # record the i-th result obtained by Alice as the bit of the secret key k