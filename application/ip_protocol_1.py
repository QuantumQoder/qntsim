import random
import qntsim
from qntsim.components.circuit import Circuit
from qntsim.kernel.timeline import Timeline
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
from qntsim.protocol import Protocol
from qntsim.topology.node import QuantumRouter
from qntsim.topology.topology import Topology
import string
import sys
import numpy as np
from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
sys.path.insert(0, '/Users/kshitij/Desktop/Internships/QuLabs/Software/QNTSim/QNTSim/kg_protocols/util')
from set_parameters import create_architecture
from post_processing import roles, print_memories, create_phi_plus_ment

network_config = "network_topology.json"
tl = Timeline(10e12)
network_topo = create_architecture(tl, network_config)

alice = network_topo.nodes['v0']
bob = network_topo.nodes['v1']

roles(sender = alice, receiver = bob, n = 0)

tl.init()
tl.run()

def z_measurement(qm, keys):
    """
    Method measures a qubit in the z basis

    Parameters :
    qm : quantum manager on which key is supposed to be measured
    key : key pointing to the qubits prepared 
    
    Returns : Measurement results
    """
    circ=Circuit(1)       #Z Basis measurement
    circ.measure(0)
    output=qm.run_circuit(circ, keys)
    return list(output.values())[0]

def print_state_vecs(qm, keys):
    """
    Method prints states for a list of keys. For debugging purposes

    Parameters :
    qm : quantum manager on which key is supposed to be measured
    keys : list of keys pointing to the qubits prepared 
    
    Returns : None
    """
    for key in keys:
        state=qm.get(key)
        print(state)

def add_bits_to_pos(message, pos, bits):
    """
    Method adds decoy bits to given positions in a message

    Parameters :
    message : Original message
    pos : list of positions to which bits need to be added
    bits : Bits that need to be added
    
    Returns : 
    temp : new message with added decoy bits
    """
    assert(len(pos) == len(bits))
    new_message = '0'* (len(message) + len(pos))
    temp = list(new_message)

    c, d = 0, 0
    for i in range(len(new_message)):
        if i in pos:
            temp[i] = str(bits[c])
            c = c + 1
        else : 
            temp[i] = message[d]
            d = d + 1

    return temp

def generate_Q1A(message, c):
    """
    Method generates Q_1^A

    Parameters :
    message : message from which Q_1^A is generated
    c : value of number of decoy bits to add
    
    Returns : new message with added decoy bits
    """
    check_bits_pos = random.sample(range(0, len(message) + c), c)
    check_bits_pos.sort()
    check_bits = []

    for i in check_bits_pos:
        random_bit = str(random.randint(0, 1))
        check_bits.append(random_bit)

    new_message = add_bits_to_pos(message, check_bits_pos, check_bits)
    return new_message, check_bits_pos, check_bits


def initilize_states(qm_alice, message):
    """
    Method prepares qubits for the message bits

    Parameters :
    qm_alice : quantum manager of alice
    message : message with decoy bits in it from which qubits are prepared

    Returns : 
    keys : list of keys pointing to the qubits prepared 
    """
    keys = []
    for i in message:
        if i == '0':
            keys.append(qm_alice.new([1, 0]))
        elif i == '1' : 
            keys.append(qm_alice.new([0, 1]))
    return keys

def apply_theta(qm, keys, theta = None):
    """
    Method applies theta gate to prepared qubits

    Parameters :
    qm : quantum manager on which keys are prepared
    keys : list of keys pointing to the qubits prepared 
    theta : value of theta applied 

    Returns : 
    theta : value of theta if randomly chosen
    """
    if theta == None : 
        #Note number 8 is random, can be changed!
        theta = random.randint(0, 8)
    for key in keys:
        circ = Circuit(1)
        circ.ry(0, 2*theta/360*np.pi)
        qm.run_circuit(circ, [key])
    return theta

def get_IDs():
    """
    Method returns IDs. Currently these are hard coded, 
    but in the future we can use QKD to generate these?

    Parameters : None

    Returns : IdA, IdB 
    """
    return '0011', '0110'

def hadamard_transform(qm, keys):
    """
    Method performs hadamard transformation on given qubits

    Parameters : 
    qm : quantum manager on which keys are prepared
    keys : list of keys pointing to the qubits prepared 

    Returns : None
    """

    circ = Circuit(len(keys))
    for i in range(len(keys)):
        circ.h(i)
    qm.run_circuit(circ, keys)

def get_IA(qm, IdA):
    """
    Method generates IA, and returns keys pointing to those qubits

    Parameters : 
    qm : quantum manager on which keys are prepared
    IdA : IdA string

    Returns : 
    IA_keys : list of keys pointing to IA_qubits
    """
    IA_keys = []
    for i in range(0, len(IdA), 2):
        keys = initilize_states(qm, IdA[i + 1])
        assert(len(keys) == 1)
        if IdA[i] == '1':
            hadamard_transform(qm, keys)
        IA_keys.append(keys[0])
    return IA_keys

def add_random_keys(keys_to_add, original_keys):
    """
    Method adds keys to original list of keys. The keys are added in a sorted manner,
    that is, the first element in keys to add will appear in the list
    before the second element and so on.

    Parameters : 
    keys_to_add : list of keys to add
    original_keys : original list 

    Returns : 
    new_list : new list of keys 
    random_pos : the positions to which the keys were added
    """
    new_list = ['0' for i in range(len(keys_to_add) + len(original_keys))]
    random_pos = random.sample(range(0, len(new_list)), len(keys_to_add))
    random_pos.sort()
    c, d = 0, 0 
    for i in range(len(new_list)):
        if i in random_pos:
            new_list[i] = keys_to_add[c]
            c = c + 1
        else : 
            new_list[i] = original_keys[d]
            d = d + 1
    return new_list, random_pos

def generate_Q2A(qm, IdA, Q1A_keys):
    """
    Method generates Q_2^A

    Parameters :
    qm : quantum manager on which keys are prepared
    IdA : IdA string
    Q1A_keys : list of keys pointing to Q_1^A
    
    Returns : 
    Q2A_keys : list of keys pointing to Q_2^A
    random_pos : the positions to which the keys were added
    IA_keys : list of keys pointing to IA_qubits
    """
    IA_keys = get_IA(qm, IdA)
    Q2A_keys, random_pos = add_random_keys(IA_keys, Q1A_keys)
    return Q2A_keys, random_pos, IA_keys

def get_IdB1(IdB):
    """
    Method generates IdB1

    Parameters :
    IdB : IdB string
    
    Returns : 
    IdB1 : IdB1 string
    r : list of random bits that Alice uses in the protocol
    """
    r = ['0' for i in range(len(IdB))]
    for i in range(len(IdB)):
        r[i] = str(random.randint(0,1))

    temp = [str(int(IdB[i])^int(r[i])) for i in range(len(r))]
    IdB1 = ''.join(temp)
    return IdB1, r

def get_IB(qm, IdB1, IdB):
    """
     Method generates IB, and returns keys pointing to those qubits

    Parameters :
    qm : quantum manager on which keys are prepared
    IdB1 : IdB1 string
    IdB : IdB string
    
    Returns : 
    IB_keys : list of keys pointing to IB_qubits
    """

    IB_keys = []

    for i in range(len(IdB1)):
        keys = initilize_states(qm, IdB1[i])
        assert len(keys) == 1
        IB_keys.append(keys[0])
        if (IdB[i] == '1'):
            hadamard_transform(qm, keys)

    return IB_keys

def generate_Q3A(qm, IdB, Q2A_keys):
    """
    Method generates Q_3^A

    Parameters :
    qm : quantum manager on which keys are prepared
    IdB : IdB string
    Q2A_keys : list of keys pointing to Q_2^A
    
    Returns : 
    Q3A_keys : list of keys pointing to Q_3^A
    random_pos : the positions to which the keys of IB were added randomly to
    IdB1 : IdB1 string
    IB_keys : list of keys pointing to IB_qubits
    r : list of random bits that Alice uses in the protocol
    """
    IdB1, r = get_IdB1(IdB)
    IB_keys = get_IB (qm, IdB1, IdB)
    Q3A_keys, random_pos = add_random_keys(IB_keys, Q2A_keys)
    return Q3A_keys, random_pos, IdB1, IB_keys, r

def get_theta_keys(qm, theta, IdB1):
    """
    Method encodes value of theta as qubits

    Parameters :
    qm : quantum manager on which keys are prepared
    theta : value of theta applied 
    IdB1 : IdB1 string

    Returns : 
    theta_keys : list of keys poitning to qubits encoding 
                 value of theta
    """
    theta_keys = []
    binary_theta = format(theta, "b")
    for i in range(len(binary_theta)):
        keys = initilize_states(qm, binary_theta[i])
        theta_keys.append(keys[0])
        if (IdB1[i] == '1'):
            hadamard_transform(qm, keys)

    return theta_keys

def generate_Q4A(qm, theta, Q3A_keys, IdB1):
    """
    Method generates Q_4^A

    Parameters :
    qm : quantum manager on which keys are prepared
    theta : value of theta applied 
    Q3A_keys : list of keys pointing to Q_3^A
    IdB1 : IdB1 string
    
    Returns : 
    Q4A_keys : list of keys pointing to Q_4^A
    random_pos : the positions to which the keys of theta_keys were added randomly to
    theta_keys : list of keys poitning to qubits encoding 
                 value of theta
    """
    theta_keys = get_theta_keys(qm, theta, IdB1)
    Q4A_keys, random_pos = add_random_keys(theta_keys, Q3A_keys)
    return Q4A_keys, random_pos, theta_keys

# There's one subtelety in the way decoy qubits work
# I am putting them in anywhere randomly, yet their results that I save I save in an ordered fashion
# Thus results and positions do not have a 1-1 correspondance necessarily
# To change this, I make the random assignment sorted.
def generate_decoy_qubits(qm, m):
    """
    Method generates decoy qubits

    Parameters :
    qm : quantum manager on which keys are prepared
    m : number of decoy qubits generated
    
    Returns : 
    decoy_keys : list of keys pointing to decoy qubits
    decoy_results : list of what the results of decoy qubits should be

    """
    decoy_keys = []
    decoy_results = []
    for i in range(m):
        random_bit = random.randint(0, 1)
        keys = initilize_states(qm, str(random_bit))
        decoy_results.append(str(random_bit))
        random_bit = random.randint(0, 1)
        if (random_bit == 1):
            hadamard_transform(qm, keys)
        decoy_keys.append(keys[0])
        decoy_results[i] += str(random_bit)

    return decoy_keys, decoy_results

def generate_Q5A(qm, Q4A_keys, m):
    """
    Method generates Q_5^A

    Parameters :
    qm : quantum manager on which keys are prepared
    Q4A_keys : list of keys pointing to Q_4^A
    m : number of decoy qubits generated
    
    Returns : 
    Q5A_keys : list of keys pointing to Q_5^A
    random_pos : the positions to which the keys of decoy qubits were added randomly to
    decoy_results : list of what the results of decoy qubits should be
    """
    decoy_keys, decoy_results = generate_decoy_qubits(qm, m)
    Q5A_keys, random_pos = add_random_keys(decoy_keys, Q4A_keys)
    return Q5A_keys, random_pos, decoy_results

def run_encoding_process(message, IdA, IdB):
    """
    Method runs encoding process and generates Q5A from message and Ids
    """
    qm_alice=alice.timeline.quantum_manager
    Q1A, check_bits_pos, check_bits = generate_Q1A(message, 3)
    Q1A_keys = initilize_states(qm_alice, Q1A)
    theta = apply_theta(qm_alice, Q1A_keys)
    
    Q2A_keys, IA_pos, IA_keys = generate_Q2A(qm_alice, IdA, Q1A_keys)
    Q3A_keys, IB_pos, IdB1, IB_keys, r = generate_Q3A(qm_alice, IdB, Q2A_keys)
    Q4A_keys, theta_keys_pos, theta_keys = generate_Q4A(qm_alice, theta, Q3A_keys, IdB1)
    Q5A_keys, decoy_pos, decoy_results = generate_Q5A(qm_alice, Q4A_keys, m = 3)
    return Q5A_keys, decoy_pos, decoy_results, IA_keys, IB_keys, r, theta_keys, Q1A_keys, check_bits_pos, check_bits

def run_security_check(qm, Q5A_keys, decoy_pos, decoy_results):
    """
    Method runs secutiy check step

    Parameters :
    qm : quantum manager on which keys are prepared
    Q5A_keys : list of keys pointing to Q_5^A
    decoy_pos : the positions to which the keys of decoy qubits were added randomly to
    decoy_results : list of what the results of decoy qubits should be

    Returns : 
    list of keys left after decoy keys were measured from Q5A_keys

    """
    to_remove = []
    for i, pos in enumerate(decoy_pos):
        if decoy_results[i][1] == '1':
            hadamard_transform(qm, [Q5A_keys[pos]])
        output = z_measurement(qm, [Q5A_keys[pos]])
        print("key : ", Q5A_keys[pos], " output : ", output, " expected output : ", decoy_results[i][0])
        assert(output == int(decoy_results[i][0])), "Security check did not pass!"
        to_remove.append(Q5A_keys[pos])

    print("Security check successful!")
    return list(set(Q5A_keys) - set(to_remove))


def authenticate_IdA(qm, IA_keys, Q5A_keys, IdA):
    """
    Method runs IdA authentication
    
    Parameters :
    qm : quantum manager on which keys are prepared
    IA_keys : list of keys pointing to IA
    Q5A_keys : list of keys pointing to Q_5^A
    IdA : IdA string

    Returns : None

    """
    c = 0
    for key in Q5A_keys:
        if key not in IA_keys:
            continue

        if IdA[c] == '1':
            hadamard_transform(qm, [key])

        output = z_measurement(qm, [key])
        assert(output == int(IdA[c + 1])), "IdA authentication did not pass!"

        c = c + 2
    print("IdA authenticated!")

def Bobs_IdB1(qm, IB_keys, Q5A_keys, IdB):
    """
    Method gets Bob's IdB1
    
    Parameters :
    qm : quantum manager on which keys are prepared
    IB_keys : list of keys pointing to IB
    Q5A_keys : list of keys pointing to Q_5^A
    IdB : IdB string

    Returns : 
    local_IdB1 : Bob's IdB1

    """

    local_IdB1 = []

    assert(len(IB_keys) == len(IdB)), " Mismatch in IB_keys and IdB! "
    for i, key in enumerate(IB_keys):
        if IdB[i] == '1':
            hadamard_transform(qm, [key])

        local_IdB1.append(z_measurement(qm, [key]))

    return local_IdB1

def check_r(IdB, Bobs_IdB1, r):
    """
    Method used by Bob to check if r is same as Alice used
    
    Parameters :
    IdB : IdB string
    Bobs_IdB1 : Bob's IdB1
    r : list of random bits that Alice uses in the protocol

    Returns : None

    """
    Bobs_r = [str(int(IdB[i])^int(Bobs_IdB1[i])) for i in range(len(IdB))]
    print("Bobs_r that he gets : ", Bobs_r)
    print("Alice's encoded r : ", r)
    assert (Bobs_r == r), "Bob's r is different from Alice's r! Some error!"
    print("Bob's r is same as Alice's r! Authentication procedure passed")

def authenticate_r(qm, IB_keys, Q5A_keys, IdB, r):
    """
    Method to authenticate r
    
    Parameters :
    qm : quantum manager on which keys are prepared
    IB_keys : list of keys pointing to IB
    Q5A_keys : list of keys pointing to Q_5^A
    IdB : IdB string
    r : list of random bits that Alice uses in the protocol

    Returns : None

    """
    local_IdB1 = Bobs_IdB1(qm, IB_keys, Q5A_keys, IdB)
    check_r(IdB, local_IdB1, r)

def run_authentication_procedure(qm, IdA, IdB, IA_keys, IB_keys, Q5A_keys, r):
    """
    Method to run authentication procedure
    """

    authenticate_IdA(qm, IA_keys, Q5A_keys, IdA)
    authenticate_r(qm, IB_keys, Q5A_keys, IdB, r)

def Bob_get_theta(qm, IdB, theta_keys):
    """
    Method for Bob to get value of theta

    Parameters :
    qm : quantum manager on which keys are prepared
    IdB : IdB string
    theta_keys : list of keys pointing to encoded theta by Alice

    Returns : 
    theta : Bob's expected value of theta
    """
    bin_theta = []
    for i, key in enumerate(theta_keys):
        if IdB[i] == '1':
            hadamard_transform(qm, [key])

        bin_theta.append(str(z_measurement(qm, [key])))
    str_bin_theta = str("".join(bin_theta))
    theta = int(str_bin_theta, 2)
    return theta

def Bob_decode_theta(qm, Q1A_keys, Bob_theta):
    """
    Method for Bob to apply inverse of theta to get bits

    Parameters :
    qm : quantum manager on which keys are prepared
    Q1A_keys : list of keys pointing to Q_1^A
    Bob_theta : Bob's expected value of theta

    Returns : Bob's message decoded
    """
    apply_theta(qm, Q1A_keys, -1*Bob_theta)
    Bob_message = []
    for key in Q1A_keys:
        Bob_message.append(str(z_measurement(qm, [key])))

    return "".join(Bob_message)

def Bob_remove_check_bits(message, check_bits_pos, check_bits):
    """
    Method for Bob to remove check bits Alice added

    Parameters :
    message : Original message
    check_bits_pos : list of positions to which bits were added
    check_bits : Bits that were added

    Returns : 
    final_message : Bob's final message decoded, which is what 
                    Alice should have sent ideally, sent as a list of bits
    """
    final_message = []
    c = 0
    for pos in range(len(message)):
        if pos in check_bits_pos:
            assert(message[pos] == check_bits[c]), "Check bits not the same!"
            c = c + 1
            continue
        final_message.append(message[pos])

    print("Check bits protocol passed!")
    return final_message

def run_decoding_process(qm, IdB, theta_keys, Q5A_keys, Q1A_keys, check_bits_pos, check_bits):
    """
    Method to run decoding procedure
    """
    Bob_theta = Bob_get_theta(qm, IdB, theta_keys)
    Bob_message_with_check_bits = Bob_decode_theta(qm, Q1A_keys, Bob_theta)
    Bob_final_message = Bob_remove_check_bits(Bob_message_with_check_bits, check_bits_pos, check_bits)
    return "".join(Bob_final_message)


def copy_Q5A(Q5A_keys, alice, bob):
    """
    Method to copy Q5A_keys from alice's node to bob's node
    This is because we do not yet have a quantum channel
    to transmit alice's prepared qubits to bob.
    
    Parameters :
    Q5A_keys : ist of keys pointing to Q_5^A
    alice : alice's node
    bob : bob's node

    Returns : 
    alice_to_bob_dict : dictionary which gives bob's keys corresponding to alice's keys
    That is, it gives states in bob's keys corresponding to states in alice's keys

    """
    qm_alice = alice.timeline.quantum_manager
    qm_bob = bob.timeline.quantum_manager
    bob_keys = []
    alice_to_bob_dict = {}

    for alice_key in Q5A_keys:
        state=qm_alice.get(alice_key)
        new_key = qm_bob.new(state.state)
        bob_keys.append(new_key)
        alice_to_bob_dict[alice_key] = new_key

    return alice_to_bob_dict


def update_keys(alice_to_bob_dict, Q5A_keys, IA_keys, IB_keys, theta_keys, Q1A_keys):
    """
    Method to update keys from pointing to alice's nodes to pointing to bob's.
    Takes in all keys to be updated, and spits out list of new keys
    """
    keys_to_update = [Q5A_keys, IA_keys, IB_keys, theta_keys, Q1A_keys]
    new_keys = [[], [], [], [], []]
    for i, batch in enumerate(keys_to_update):
        for key in batch:
            new_keys[i].append(alice_to_bob_dict[key])

    return new_keys

def run_ip_protocol(message = "0"):
    """
    Method to run ip protocol
    """
    qm_alice=alice.timeline.quantum_manager
    qm_bob=bob.timeline.quantum_manager
    IdA, IdB = get_IDs()
    Q5A_keys, decoy_pos, decoy_results, IA_keys, IB_keys, r, theta_keys, Q1A_keys, check_bits_pos, check_bits = run_encoding_process(message, IdA, IdB)
    
    ## Sends qubits to bobs node
    alice_to_bob_dict = copy_Q5A(Q5A_keys, alice, bob)
    Q5A_keys, IA_keys, IB_keys, theta_keys, Q1A_keys = update_keys(alice_to_bob_dict, Q5A_keys, IA_keys, IB_keys, theta_keys, Q1A_keys)
    ## Maybe use identity gates. Currently simulating it by copying keys

    run_security_check(qm_bob, Q5A_keys, decoy_pos, decoy_results)
    run_authentication_procedure(qm_bob, IdA, IdB, IA_keys, IB_keys, Q5A_keys, r)
    Bob_message = run_decoding_process(qm_bob, IdB, theta_keys, Q5A_keys, Q1A_keys, check_bits_pos, check_bits)
    print(f"input message : {message}")
    print(f"Bob_message : {Bob_message}")

run_ip_protocol(message = "010010")



# key = qm_alice.new([amp1, amp2])