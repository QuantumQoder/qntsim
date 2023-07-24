import qntsim
from qntsim.components.circuit import Circuit
from qntsim.kernel.timeline import Timeline
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
from qntsim.protocol import Protocol
# from qntsim.topology.node import QuantumRouter
from qntsim.topology.topology import Topology
import string
import sys
import numpy as np
import random
from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
sys.path.insert(0, '/Users/kshitij/Desktop/Internships/QuLabs/Software/QNTSim/QNTSim/kg_protocols/util')
from set_parameters import create_architecture
from post_processing import *


#Currently, network simulator allows one to measure qubits across different nodes.
#This is wrong with respect to the basic physical structure
#Ask 

network_config = "/Users/aman/QNT/QNTSim/example/4node.json"
tl = Timeline(10e12,"Qutip")
network_topo = create_architecture(tl, network_config)


#Note this point and send to Aman and cc Rikteem
alice1 = network_topo.nodes['a']
alice2 = network_topo.nodes['s1']
bob1 = network_topo.nodes['s2']
bob2 = network_topo.nodes['b']

roles(sender = alice1, receiver = alice2, n = 50)
roles(sender = bob1, receiver = bob2, n = 50)

tl.init()
tl.run()

entangled_keys_alice = create_phi_plus_entanglement(alice1)
entangled_keys_bob = create_phi_plus_entanglement(bob1)

def create_sequence_S(node, keys):
	"""
    Method creates sequence S

    Parameters :
    node : node on which qubits created
    keys : list of keys pointing to the qubits prepared 

    Returns : 
    plus_keys : list of keys which were set to the plus state
    """
	qm = node.timeline.quantum_manager
	plus_keys = []
	for key in keys:
		choice = random.randint(0, 1)
		change_bell_state(qm, [key, key + 100], [choice, 1])
		if choice == 0:
			plus_keys.append(key)
	return plus_keys

def create_sequence_C(sequence_S_keys, random_keys):
	"""
    Method creates sequence C

    Parameters :
    sequence_S_keys : list of keys pointing to the qubits prepared for sequence S
    random_keys : list of keys pointing to random qubits prepared

    Returns : 
    sequence_C_keys : list of keys pointing to the qubits prepared for sequence C
    """
	check_bits_pos = random.sample(range(0, len(sequence_S_keys) + len(random_keys)), len(random_keys))
	check_bits_pos.sort()
	sequence_C_keys = []
	c, d = 0, 0
	for i in range(len(sequence_S_keys + random_keys)):
		if i in check_bits_pos:
			sequence_C_keys.append(random_keys[c])
			c = c + 1
		else:
			sequence_C_keys.append(sequence_S_keys[d])
			d = d + 1
	return sequence_C_keys

def insert_random_qubits(node, m):
	"""
    Method creates sequence C

    Parameters :
    node : node on which qubits created
    m : Number of random qubits to be inserted

    Returns : 
    keys : list of keys pointing to the m random qubits prepared 
    bits : bits '0' or '1' which were prepared
    had_basis : bits encoded in hadamard basis
    """
	qm = node.timeline.quantum_manager
	keys, bits, had_basis = [], {}, []
	for i in range(m):
		key = 0
		if random.randint(0,1) == 0:
			key = qm.new([1, 0])
			bits[key] = 0
		else: 
			key = qm.new([0, 1])
			bits[key] = 1
		keys.append(key)
		if random.randint(0,1) == 1:
			hadamard_transform(qm, [key])
			had_basis.append(key)
	return keys, bits, had_basis

def Charlie_measure(node, keys, a_keys, a_qbits, a_basis, b_keys, b_qbits, b_basis):
	"""
    Method implements first of Charlie's measurement step in the protocol

    Parameters :
    node : node on which qubits created
    keys : list of pairs of alice and bob qubits which Charlie will measure
    a(b)_keys : keys corresponding to alice's (bob's) qubits
    a(b)_qbits : bits corresponding to alice's (bob's) qubits
    a(b)_basis : basis corresponding to alice's (bob's) qubits

    Returns : 
    results : dictionary of measurement results for key pairs, with key being alice's key
    """
	qm = node.timeline.quantum_manager
	results = {}
	for key_pairs in keys:
		output = bell_measure(qm, key_pairs)
		results[key_pairs[0]] = output
		check_security(key_pairs, a_keys, a_qbits, a_basis, b_keys, b_qbits, b_basis, output)

	return results

def Bob_secure(node, M_b_keys):
	"""
    Method implements Bob's security step, by applying x gate to some of the qubits

    Parameters :
    node : node on which qubits created
    M_b_keys : keys for sequence M for bob

    Returns : 
    applied_keys : keys on which x gate was applied
    """
	qm = node.timeline.quantum_manager
	applied_keys = []
	for key in M_b_keys:
		if random.randint(0,1) == 1:
			circ = Circuit(1)
			circ.x(0)
			qm.run_circuit(circ, [key])
			applied_keys.append(key)
	return applied_keys

def Charlie_measure_2(node, keys):
	"""
    Method implements second of Charlie's measurement step in the protocol

    Parameters :
    node : node on which qubits created
    keys : list of pairs of alice and bob qubits which Charlie will measure

    Returns : 
    results : dictionary of measurement results for key pairs, with key being alice's key
    """
	qm = node.timeline.quantum_manager
	results = {}
	for key_pairs in keys:
		output = bell_measure(qm, key_pairs)
		results[key_pairs[0]] = output

	return results


def check_security(keys, a_keys, a_qbits, a_basis, b_keys, b_qbits, b_basis, output):
	"""
    This step is for checking security of the protocol

    Parameters :
    keys : list of pairs of alice and bob qubits which Charlie will measure
    a(b)_keys : keys corresponding to alice's (bob's) qubits
    a(b)_qbits : bits corresponding to alice's (bob's) qubits
    a(b)_basis : basis corresponding to alice's (bob's) qubits

    Returns : None
    """
	if (keys[0] not in a_keys) or (keys[1] not in b_keys):
		return

	if (keys[0] in a_basis and keys[1] not in b_basis) or (keys[0] not in a_basis and keys[1] in b_basis):
		return

	if (keys[0] in a_basis and keys[1] in b_basis):
		print("going through hadamard check")
		if a_qbits[keys[0]] == b_qbits[keys[1]]:
			assert (output[0] == 0)
		else : assert (output[0] == 1)

	if (keys[0] not in a_basis) and (keys[1] not in b_basis):
		print("going through computational check")
		if a_qbits[keys[0]] == b_qbits[keys[1]]:
			assert (output[1] == 0)
		else : assert(output[1] == 1)


	print("security checks passed!")



def M_keys(a_seqc, b_seqc, a_seqS, rand_a_keys, rand_a_basis, b_seqS, rand_b_keys, rand_b_basis):
	"""
    This method returns keys for the M sequence

    Parameters :
    a(b)_seqc : keys corresponding to alice's (bob's) sequence C
    a(b)_seqS : : keys corresponding to alice's (bob's) sequence S
    rand_a(b)_keys : keys corresponding to alice's (bob's) qubits
    rand_a(b)_basis : basis corresponding to alice's (bob's) qubits

    Returns : keys corresponding to M_a and M_b
    """
	M_a_keys, M_b_keys = [], []
	assert(len(a_seqc) == len(b_seqc))
	for i in range(len(a_seqc)):
		print(i, a_seqc[i], b_seqc[i])
		if a_seqc[i] in a_seqS and b_seqc[i] in b_seqS:
			M_a_keys.append(a_seqc[i] - 100)
			M_b_keys.append(b_seqc[i] - 100)

	return M_a_keys, M_b_keys

def perform_sigma_z(node, keys):
	"""
    This method performs z gate on given qubits

    Parameters :
    node : node on which qubits created
    keys : : list of keys pointing to qubits which need to be acted on

    Returns : None
    """
	qm = node.timeline.quantum_manager
	for key in keys:
		circ = Circuit(1)
		circ.z(0)
		qm.run_circuit(circ, [key])

def apply_encoding_gates(node, key, message):
	"""
    This method performs encoding operation for alice for each message bit pair

    Parameters :
    node : node on which qubits created
    message : 2 bit pairs according to which encoding is done
    key : key pointing to qubits which need to be acted on

    Returns : None
    """
	if message == "00":
		return
	qm = node.timeline.quantum_manager
	circ = Circuit(1)
	if message == "01":
		circ.x(0)
	if message == "11":
		circ.z(0)

	#\sigma_z \times \sigma_x = i\sigma_y
	if message == "10":
		circ.z(0)
		circ.x(0)
	qm.run_circuit(circ, [key])

def alice_encode(node, message, M_keys):
	"""
    This method performs complete encoding operation for alice 

    Parameters :
    node : node on which qubits created
    message : full message to be encoded
    M_keys : key pointing to qubits for sequence M

    Returns : list of keys on the M sequence used for message encoding
    """
	for i in range(len(message)//2):
		bits = message[2*i:2*i+2]
		apply_encoding_gates(node, M_keys[i], bits)
	return M_keys[0:i+1]

def decode(results1, results2, encoded_keys, M_b_keys, bob_plus_keys, applied_keys):
	"""
    This method represents Bob's decoding process for QSDC protocol

    Parameters :
    results1 : results from Charlie's first measurement
    results2 : results from Charlie's second measurement
    encoded_keys : list of keys pointing to qubits on Alice's sequence M on which encoding was done
    M_b_keys : keys pointing to bob's sequence M
    bob_plus_keys : keys on Bob's sequence on which + state was encoded
    applied_keys : keys on which z gate was applied by Bob

    Returns : message decoded by Bob
    """
	message = ""
	for i, key in enumerate(encoded_keys):
		result = results1[key + 100]
		if M_b_keys[i] in bob_plus_keys:
			expected = [1 - result[0], result[1]]

		else : expected = [result[0], result[1]]
		bits = [abs(results2[key][0] - expected[0]), abs(results2[key][1] - expected[1])]
		print(bits)
		if bits[0] == 1:
			bits[1] = 1 - bits[1]
		if M_b_keys[i] in applied_keys:
			bits[1] = 1 - bits[1]
		message = message + str(bits[0]) + str(bits[1])
	return message

def run_mdi_qsdc(m, n):
	"""
    Method to run mdi_qsdc protocol
    """
	alice_seqS_keys, bob_seqS_keys =  entangled_keys_alice[:m],  entangled_keys_bob[:m]
	alice_plus_keys = create_sequence_S(alice1, alice_seqS_keys)
	random_alice_keys, random_alice_qbits, random_alice_basis = insert_random_qubits(alice2, n)
	alice_seqc = create_sequence_C([key + 100 for key in alice_seqS_keys], random_alice_keys)
	bob_plus_keys = create_sequence_S(bob1, bob_seqS_keys)
	random_bob_keys, random_bob_qbits, random_bob_basis = insert_random_qubits(bob2, n)
	bob_seqc = create_sequence_C([key + 100 for key in bob_seqS_keys], random_bob_keys)
	results1 = Charlie_measure(alice2, [[alice_seqc[i], bob_seqc[i]] for i in range(len(alice_seqc))], 
								random_alice_keys, random_alice_qbits, random_alice_basis, random_bob_keys, random_bob_qbits, random_bob_basis)
	M_a_keys, M_b_keys = M_keys(alice_seqc, bob_seqc, [key + 100 for key in alice_seqS_keys], random_alice_keys, random_alice_basis, 
													[key + 100 for key in bob_seqS_keys], random_bob_keys, random_bob_basis)
	perform_sigma_z(alice1, alice_plus_keys)
	alice_message = "111100100100"
	encoded_keys = alice_encode(alice1, alice_message, M_a_keys)
	applied_keys = Bob_secure(bob1, M_b_keys)
	results2 = Charlie_measure_2(alice1, [[M_a_keys[i], M_b_keys[i]] for i in range(len(encoded_keys))])
	Bobs_message = decode(results1, results2, encoded_keys, M_b_keys, bob_plus_keys, applied_keys)
	print("Alice's message is : \t", alice_message)
	print("Bobs message is : \t", Bobs_message)

run_mdi_qsdc(15, 10)




