#!/usr/bin/env python
# coding: utf-8

# # Importing necessary modules

# In[1]:


import math
from qntsim.components.circuit import QutipCircuit
from ghz_2 import Centralized_GHZ
from protocols import *


# ## Teleporitng the message
# 
# This function teleports the bit string over the network provided by the user. The function follows the paper by .
# 
# The function takes the teleporting node and the message to be teleported as the inputs and, returns a list of corrections for the entangled qubits from the GHZ triplet.

# In[2]:


def teleport(node, message="01001"):
    """
    Method to teleport the message through the quantum secret sharing protocol
    by Hillery, Buzek and Berthiaume
    
    Parameters:
    node : <EndNode>
        The node sending the message over the network
    message : str
        The bit string of the message to be teleported
    
    Returns:
    corrections : dict
        The dicitonary contains the bell measurements (dict_values) respective
        to the indices (dict_keys)
    """
    
    alpha = complex(1/math.sqrt(2))
    corrections = {}
    
    qtc = QutipCircuit(2)
    qtc.cx(0, 1)
    qtc.h(0)
    qtc.measure(0)
    qtc.measure(1)
    
    qm = node.timeline.quantum_manager
    for i in range(len(message)):
        info = node.resource_manager.memory_manager[i]
        if info.state=='ENTANGLED':
            index = info.memory.qstate_key
            state = qm.get(index)
            keys = state.keys.copy()
            keys.remove(index)
            new_index = qm.new([alpha, ((-1)**int(message[i]))*alpha])
            corrections[tuple(keys)] = list(qm.run_circuit(qtc, [new_index, index]).values())
    
    return corrections


# ## Measuring out the phases
# 
# Apart from the final receiver, the intermediate supporter needs to perform measurements on their qubits, in order to provide the information on the relative phase of the decoded message. The function takes care of the same.
# 
# It takes the supporter node and the list of the correction measurements from the sender as an input and returns the output as a list of corrections that the receiver needs to perfrom local pauli corrections on their qubits to recover the information from the sender.

# In[3]:


def phase_measurement(node, corrections):
    """
    Method to perform the x-basis measurement at the supporter node
    
    Parameters:
    node : <EndNode>
        The node performing the x-measurement to determine the phase of the message
    corrections : dict
        The dictionary contains the bell measurement outcomes and the indices
        to which the outcomes relate to
    
    Returns:
    corrections : dict
        The updated dicitonary containing the bell measurements, together with
        the phase measurements(dict_values) respective to the indices (dict_keys)
    """
    
    qtc = QutipCircuit(1)
    qtc.h(0)
    qtc.measure(0)
    
    qm = node.timeline.quantum_manager
    for info in node.resource_manager.memory_manager:
        if info.state=='ENTANGLED':
            index = info.memory.qstate_key
            output = qm.run_circuit(qtc, [index])
            corrections = dict([([key for key in keys if key!=index][0], values+[output.get(index)]) if isinstance(keys, tuple) and index in keys else (keys, values) for keys, values in corrections.items()])
    
    return corrections


# ## Decoding the message
# 
# This function decodes the message received at the other end node.
# 
# The function takes the receiver node, list of corrections for each bit of message and, prints the message that the block has decoded from the inputs it got.

# In[4]:


def decode(node, corrections):
    """
    Method to decode the message at the receiver node
    
    Parameters:
    node : <EndNode>
        The node receiving the message over the network
    corrections : dict
        The dicitonary containing all the measurement outcomes (dict_values)
        respective to the indices (dict_keys)
    """
    
    output = ''
    
    qm = node.timeline.quantum_manager
    for key, values in corrections.items():
        qtc = QutipCircuit(1)
        if values[0]!=values[2]:
            qtc.z(0)
        if values[1]==1:
            qtc.x(0)
        qtc.h(0)
        qtc.measure(0)
        output = output+str(qm.run_circuit(qtc, [key]).get(key))
    message = ''.join(chr(int(output[i:i+7], 2)) for i in range(0, len(output), 7))
    print("\n\n\n\n\n Received: ", message)


# # The main() function
# 
# The main() function handles all the procedure of
# - message deformation,
# - node creation,
# - entanglement generation,
# - encoding of the message,
# - teleporitng it over the channels,
# - decoding the message and,
# - finally reconstructing it brom its binary form.
# 
# The function takes the message from the sender as an input and returns the receiver-decoded message.

# In[5]:


def main(message="Hello World"):
    """
    Method to execute the whole protocol
    
    Parameters:
    message : str
        The message to be teleported
    """
    
    print("Teleport: ", message, "\n\n\n\n\n")
    words = message.split()
    msg = ''
    for word in words:
        msg += ''.join(bin(ord(w))[2:] for w in word)
        msg += '0'+bin(ord(' '))[2:]
    ghz = Centralized_GHZ(topology="/Users/aman/QNT/QNTSim/example/3n_linear.json", size=len(msg))
    nodes = ghz.nodes.copy()
    corrections = teleport(nodes[0], message=msg)
    corrections = phase_measurement(nodes[1], corrections)
    decode(nodes[2], corrections)


# In[6]:


main()


# In[ ]:




