import random
import qntsim
from qntsim.components.circuit import Circuit, QutipCircuit
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
from qntsim.protocol import Protocol
# from qntsim.topology.node import QuantumRouter
from qntsim.topology.topology import Topology
import string
import sys
import numpy as np
from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
sys.path.insert(0, '/Users/kshitij/Desktop/Internships/QuLabs/Software/QNTSim/QNTSim/kg_protocols/util')
from set_parameters import create_architecture
from post_processing import roles, print_memories, create_phi_plus_entanglement

network_config = "3node.json"
tl = Timeline(10e12,"Qutip")
network_topo = create_architecture(tl, network_config)

alice = network_topo.nodes['a']
bob = network_topo.nodes['b']

roles(sender = alice, receiver = bob, n = 0)

tl.init()
tl.run()

def z_measurement(qm, keys):
    circ=QutipCircuit(1)       #Z Basis measurement
    circ.measure(0)
    output=qm.run_circuit(circ, keys)
    return list(output.values())[0]

def print_state_vecs(qm, keys):
    for key in keys:
        state=qm.get(key)
        print(state)

def add_bits_to_pos(message, pos, bits):
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
    check_bits_pos = random.sample(range(0, len(message) + c), c)
    check_bits_pos.sort()
    check_bits = []

    for i in check_bits_pos:
        random_bit = str(random.randint(0, 1))
        check_bits.append(random_bit)

    new_message = add_bits_to_pos(message, check_bits_pos, check_bits)
    return new_message, check_bits_pos, check_bits


def initilize_states(qm_alice, message):
    keys = []
    for i in message:
        if i == '0':
            keys.append(qm_alice.new([1, 0]))
        elif i == '1' : 
            keys.append(qm_alice.new([0, 1]))
    return keys

def apply_theta(qm, keys, theta = None):
    if theta == None : 
        theta = random.randint(0, 8)
    for key in keys:
        circ = QutipCircuit(1)
        circ.ry(0, 2*theta/360*np.pi)
        qm.run_circuit(circ, [key])
    return theta

def get_IDs():
    return '0011', '0110'

def hadamard_transform(qm, keys):
    circ = QutipCircuit(len(keys))
    for i in range(len(keys)):
        circ.h(i)
    qm.run_circuit(circ, keys)

def get_IA(qm, IdA):
    IA_keys = []
    for i in range(0, len(IdA), 2):
        keys = initilize_states(qm, IdA[i + 1])
        assert(len(keys) == 1)
        if IdA[i] == '1':
            hadamard_transform(qm, keys)
        IA_keys.append(keys[0])
    return IA_keys

def add_random_keys(keys_to_add, original_keys):
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
    IA_keys = get_IA(qm, IdA)
    Q2A_keys, random_pos = add_random_keys(IA_keys, Q1A_keys)
    return Q2A_keys, random_pos, IA_keys

def get_IdB1(IdB):
    r = ['0' for i in range(len(IdB))]
    for i in range(len(IdB)):
        r[i] = str(random.randint(0,1))

    temp = [str(int(IdB[i])^int(r[i])) for i in range(len(r))]
    IdB1 = ''.join(temp)
    return IdB1, r

def get_IB(qm, IdB1, IdB):
    IB_keys = []

    for i in range(len(IdB1)):
        keys = initilize_states(qm, IdB1[i])
        assert len(keys) == 1
        IB_keys.append(keys[0])
        if (IdB[i] == '1'):
            hadamard_transform(qm, keys)

    return IB_keys

def generate_Q3A(qm, IdB, Q2A_keys):
    IdB1, r = get_IdB1(IdB)
    IB_keys = get_IB (qm, IdB1, IdB)
    Q3A_keys, random_pos = add_random_keys(IB_keys, Q2A_keys)
    return Q3A_keys, random_pos, IdB1, IB_keys, r

def get_theta_keys(qm, theta, IdB1):
    theta_keys = []
    binary_theta = format(theta, "b")
    for i in range(len(binary_theta)):
        keys = initilize_states(qm, binary_theta[i])
        theta_keys.append(keys[0])
        if (IdB1[i] == '1'):
            hadamard_transform(qm, keys)

    return theta_keys

def generate_Q4A(qm, theta, Q3A_keys, IdB1):
    theta_keys = get_theta_keys(qm, theta, IdB1)
    Q4A_keys, random_pos = add_random_keys(theta_keys, Q3A_keys)
    return Q4A_keys, random_pos, theta_keys

# There's one subtelety in the way decoy qubits work
# I am putting them in anywhere randomly, yet their results that I save I save in an ordered fashion
# Thus results and positions do not have a 1-1 correspondance necessarily
# To change this, I make the random assignment sorted.
def generate_decoy_qubits(qm, m):
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
    decoy_keys, decoy_results = generate_decoy_qubits(qm, m)
    Q5A_keys, random_pos = add_random_keys(decoy_keys, Q4A_keys)
    return Q5A_keys, random_pos, decoy_results

def run_encoding_process(message, IdA, IdB):
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

    local_IdB1 = []

    assert(len(IB_keys) == len(IdB)), " Mismatch in IB_keys and IdB! "
    for i, key in enumerate(IB_keys):
        if IdB[i] == '1':
            hadamard_transform(qm, [key])

        local_IdB1.append(z_measurement(qm, [key]))

    return local_IdB1

def check_r(IdB, Bobs_IdB1, r):
    Bobs_r = [str(int(IdB[i])^int(Bobs_IdB1[i])) for i in range(len(IdB))]
    print("Bobs_r that he gets : ", Bobs_r)
    print("Alice's encoded r : ", r)
    assert (Bobs_r == r), "Bob's r is different from Alice's r! Some error!"
    print("Bob's r is same as Alice's r! Authentication procedure passed")

def authenticate_r(qm, IB_keys, Q5A_keys, IdB, r):
    local_IdB1 = Bobs_IdB1(qm, IB_keys, Q5A_keys, IdB)
    check_r(IdB, local_IdB1, r)

def run_authentication_procedure(qm, IdA, IdB, IA_keys, IB_keys, Q5A_keys, r):
    authenticate_IdA(qm, IA_keys, Q5A_keys, IdA)
    authenticate_r(qm, IB_keys, Q5A_keys, IdB, r)

def Bob_get_theta(qm, IdB, theta_keys):
    bin_theta = []
    for i, key in enumerate(theta_keys):
        if IdB[i] == '1':
            hadamard_transform(qm, [key])

        bin_theta.append(str(z_measurement(qm, [key])))
    str_bin_theta = str("".join(bin_theta))
    theta = int(str_bin_theta, 2)
    return theta

def Bob_decode_theta(qm, Q1A_keys, Bob_theta):
    apply_theta(qm, Q1A_keys, -1*Bob_theta)
    Bob_message = []
    for key in Q1A_keys:
        Bob_message.append(str(z_measurement(qm, [key])))

    return "".join(Bob_message)

def Bob_remove_check_bits(message, check_bits_pos, check_bits):
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
    Bob_theta = Bob_get_theta(qm, IdB, theta_keys)
    Bob_message_with_check_bits = Bob_decode_theta(qm, Q1A_keys, Bob_theta)
    Bob_final_message = Bob_remove_check_bits(Bob_message_with_check_bits, check_bits_pos, check_bits)
    return "".join(Bob_final_message)


def copy_Q5A(Q5A_keys, alice, bob):
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
    keys_to_update = [Q5A_keys, IA_keys, IB_keys, theta_keys, Q1A_keys]
    new_keys = [[], [], [], [], []]
    for i, batch in enumerate(keys_to_update):
        for key in batch:
            new_keys[i].append(alice_to_bob_dict[key])

    return new_keys



def run_ip_protocol(message = "0"):
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

# One question - technically all of this is happening on Alice's nodes. How do 
# I send everything to Bob's nodes
# I don't know
run_ip_protocol(message = "010010")



# key = qm_alice.new([amp1, amp2])