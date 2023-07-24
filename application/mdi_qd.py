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

network_config = "/Users/aman/QNT/QNTSim/example/3node.json"
tl = Timeline(10e12,"Qutip")
network_topo = create_architecture(tl, network_config)

alice = network_topo.nodes['a']
bob = network_topo.nodes['b']

roles(sender = alice, receiver = bob, n = 50)

tl.init()
tl.run()

def prepare_qubit(node, message_bit, key_bit):
	"""
    Method prepares qubits according to the message bit and key bit

    Parameters :
    node : node on which qubits to be created
    message_bit : message bit to be encoded
	key_bit : key bit corresponding to message bit

    Returns :
    key : key pointing to qubit created
    """
	qm = node.timeline.quantum_manager
	if message_bit == '0':
		key = qm.new([1, 0])
	else : key = qm.new([0, 1])
	if key_bit == '1':
		hadamard_transform(qm, [key])
	return key

def Charlie_measure(node, alice_keys, bob_keys):
	"""
    Method implements Charlie's measurement step in the protocol

    Parameters :
    node : node on which qubits created
    alice_keys : keys corresponding to alice's qubits
    bob_keys : keys corresponding to bob's qubits

    Returns : 
    results : list of measurement results 
    """
	qm = node.timeline.quantum_manager
	results = []
	for i in range(len(alice_keys)):
		output = bell_measure(qm, [alice_keys[i], bob_keys[i]])
		results.append(output)
	return results

def decode_messages(results, alice_message, bob_message, shared_key):
	"""
    Method implements the first way to decode. This method is not completely secure though.

    Parameters :
    results : node on which qubits created
    alice_message : alice's message
    bob_message : bob's message 
    shared_key : key shared between alice and bob

    Returns : 
    alice_decode : alice's guess of bob's message
    bob_decode : bob's guess of alice's message
    """

	alice_decode, bob_decode = "", ""
	print("RES", results)
	for i in range(len(results)):
		if results[i] == [0,0] or results[i] == [1,1]: 

			continue

		if results[i] == [1,0]:
			print(alice_message[i], shared_key[i])
			if shared_key[i] == '0': 
				alice_decode += alice_message[i]
				bob_decode += bob_message[i]

			else : 
				alice_decode += str(1 - int(alice_message[i]))
				bob_decode += str(1 - int(bob_message[i]))

		if results[i] == [0,1]:
			if shared_key[i] == '0':
				alice_decode += str(1 - int(alice_message[i]))
				bob_decode += str(1 - int(bob_message[i]))
			else : 
				alice_decode += alice_message[i]
				bob_decode += bob_message[i]

	return alice_decode, bob_decode

def get_key():
	"""
    Method is for getting key shared between alice and bob. Later, we want to use
    a QKD protocol here

    Parameters : None

    Returns : 
    key : key shared between alice and bob
    c : value of c for the key
    """
	key = "000101010"
	c = 0
	for i in range(len(key) - 1):
		c = c + int(key[i]) ^ int(key[i+1])
	return key, c

def check_for_error(gammma, alice_keys, bob_keys, shared_key, alice_message, bob_message, results):
	"""
    Method checks for noise and error in the protocol

    Parameters :
    gammma : node on which qubits created
    alice_keys : keys corresponding to alice's qubits
    bob_keys : keys corresponding to bob's qubits

    Returns : 
    results : list of measurement results 
    """
	num = int(gammma*len(alice_keys))
	to_check = random.sample(range(0, len(alice_keys)), num)
	for i in to_check:
		output = bell_measure(alice.timeline.quantum_manager, [alice_keys[i], bob_keys[i]])
		if shared_key[i] == '0':
			if results[i] == [0,0] or results[i] == [1,0]:
				assert alice_message[i] == bob_message[i]
			else : assert int(alice_message[i]) == 1 - int(bob_message[i])

		else : 
			if results[i] == [0,0] or results[i] == [0,1]:			
				assert alice_message[i] == bob_message[i]
			else : assert int(alice_message[i]) == 1 - int(bob_message[i])
	print("checks successful!")
	return to_check

def calculate_X(checked_pos, results):
	"""
    Method calculates string X

    Parameters :
    checked_pos : list of positions which were checked for error
    results : results in Bell basis from Charlie's measurement 

    Returns : 
    M : results for checked positions
    X : string X
    """
	X = ""
	M = []
	for i in range(len(results)):
		if i in checked_pos: continue
		M.append(results[i])
		if results[i] == [0,1] or results[i] == [1,0] :
			X += "1"
		else : X +="0"
	return M, X

def generate_Y(X, shared_key, c):
	"""
    Method calculates string Y

    Parameters :
    X : string X
    shared_key : key shared between alice and bob
    c : value of c from the key

    Returns : 
	Y : string Y
    """
	j = 0
	Y = ""
	for x_i in X : 
		if x_i == "1": Y+= "0"
		else :
			if c == 1:
				Y += shared_key[j]
			else : Y += str(1 - int(shared_key[j]))
			j += 1
	return Y

def decode_messages_2(M, alice_message, bob_message, X, Y, shared_key):
	"""
    Method implements the second way to decode. This method is secure.

    Parameters :
    M : values of M
    alice_message : alice's message
    bob_message : bob's message 
    X : string X
    Y : string Y
    shared_key : key shared between alice and bob

    Returns : 
    alice_guess : alice's guess of bob's message
    bob_guess : bob's guess of alice's message
    """

	alice_guess, bob_guess = "", ""
	#print(len(M), len(X), len(Y))
	for i in range(len(M)):
		if int(X[i]) ^ int(Y[i]) == 1:
			if shared_key[i] == '0':
				if M[i] == [0,0] or M[i] == [1, 0]:
					alice_guess += alice_message[i]
					bob_guess += bob_message[i]
				else : 
					alice_guess += str(1 - int(alice_message[i]))
					bob_guess += str(1 - int(bob_message[i]))
			else :
				if M[i] == [0,0] or M[i] == [0, 1]:
					alice_guess += alice_message[i]
					bob_guess += bob_message[i]
				else : 
					alice_guess += str(1 - int(alice_message[i]))
					bob_guess += str(1 - int(bob_message[i]))

	return alice_guess, bob_guess


def run_mdi_qd(alice_message, bob_message):
	"""
    Method to run mdi_qd protocol
    """
	assert(len(alice_message) == len(bob_message))
	shared_key, c = get_key()
	alice_keys, bob_keys = [], []
	for i, bit in enumerate(alice_message):
		alice_keys.append(prepare_qubit(alice, bit, shared_key[i]))

	for i, bit in enumerate(bob_message):
		bob_keys.append(prepare_qubit(bob, bit, shared_key[i]))

	results = Charlie_measure(alice, alice_keys, bob_keys)
	gamma = 0.2
	checked_pos = check_for_error(gamma, alice_keys, bob_keys, shared_key, alice_message, bob_message, results)
	M, X = calculate_X(checked_pos, results)
	Y = generate_Y(X, shared_key, c)
	print(Y)

	#alice_decode, bob_decode = decode_messages(results, alice_message, bob_message, shared_key)
	alice_decode, bob_decode = decode_messages_2(M, alice_message, bob_message, X, Y, shared_key)
	print("Alice's original message : ", alice_message)
	print("Bob's original message : ", bob_message)
	print("Alice's guess of Bob's message : ", alice_decode)
	print("Bob's guess of Alice's message : ", bob_decode)

# Take two memories for the same node
# and then create entanglement locally


run_mdi_qd("000101010", "001111001")