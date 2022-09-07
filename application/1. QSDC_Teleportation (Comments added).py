#!/usr/bin/env python
# coding: utf-8

# # Importing necessary modules

# In[2]:


import math
from protocols import *
from qntsim.components.circuit import QutipCircuit


# ## Teleporitng the message
# 
# This function teleports the bit string over the network provided by the user. The function follows the paper by .
# 
# The function takes the teleporting node and the message to be teleported as the inputs and, returns a list of indices of the receiver's nodes over which the message was teleported with the list of the x and z measurements on the photons of the sender.

# In[3]:


def teleport(a, message="01001"):
    """
    Method to perform the teleportation protocol based on the Yan-Zhang protocol
    
    Parameters:
    a : <EndNode>
        This is the sender node which performs the teleportation
    message : str
        This is the bit string which needs to be teleported over the channels
    
    Returns:
    indices : list
        List of indices respective to which bell measurements have been done
    crx : list
        List of bell measurements for Pauli-X corrections
    crz : list
        List of bell measurements for Pauli-Z corrections
    """
    
    a_qm = a.timeline.quantum_manager # quantum manager of the node 'a'
    indices, crz, crx = [], [], []
    # Qutip Circuit for performing Bell measurement
    qtc = QutipCircuit(2)
    qtc.cx(0, 1)
    qtc.h(0)
    qtc.measure(0)
    qtc.measure(1)
    # The loop travles throughout the whole message extracting 1-bit at a time
    # and, teleporting it over the channels
    for i in range(len(message)):
        m = message[i]
        info = a.resource_manager.memory_manager[i]
        index = info.memory.qstate_key
        state = a_qm.get(index)
        keys = state.keys.copy()
        keys.remove(index)
        indices.append(keys[0])
        if m=="0" or m==0:
            new_index = a_qm.new([complex(1/math.sqrt(2)), complex(1/math.sqrt(2))])
        else:
            new_index = a_qm.new([complex(1/math.sqrt(2)), complex(-1/math.sqrt(2))])
        result = a_qm.run_circuit(qtc, [new_index, index])
        crz.append(result.get(new_index))
        crx.append(result.get(index))
    
    return indices, crx, crz


# ## Decoding the message
# 
# This function decodes the message received at the other end node.
# 
# The function takes the other end node, list of the bell states at the end node and, the list of the x and z measurements for each bit of message and, returns the message that the block has decoded from the inputs it got.

# In[4]:


def decode(b, indices, crx, crz):
    """
    Method to decode the message at the receiver node
    
    Parameters:
    b : <EndNode>
        The reciver node
    indices : list
        List of indices respective to which bell measurements have been done
    crx : list
        List of bell measurements for Pauli-X corrections
    crz : list
        List of bell measurements for Pauli-Z corrections
    
    Returns:
    message : str
        This is the bit string which was decoded after performing local Pauli
        corrections.
    """
    
    message = ''
    b_qm = b.timeline.quantum_manager # quantum manager of node 'b'
    # The loop travels through the list of indices and applies Pauli
    # corrections to the respective key, one at a time
    for index in indices:
        stb = b_qm.get(index)
        i = indices.index(index)
        qtc = QutipCircuit(1)
        if crx[i]==1:
            qtc.x(0)
        if crz[i]==1:
            qtc.z(0)
        qtc.h(0)
        qtc.measure(0)
        result = b_qm.run_circuit(qtc, [index])
        message = message+str(result.get(index))
    
    return message


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

# In[11]:


def main(message='Hello World'):
    """
    Method to handle the whole execution of the protocol
    Parameters:
    message : str
        The message to be teleported over the network
    """
    print('Teleport:', message, '\n\n\n\n\n\n\n\n\n')
    words = message.split()
    msg = ''
    for word in words:
        msg += ''.join(bin(ord(w))[2:] for w in word)
        msg += '0'+bin(ord(' '))[2:]
    nodes, network = initiate(topology="/Users/aman/QNT/QNTSim/example/3n_linear.json",size=len(msg))
    #a = rectify_entanglements(a)
    indices, crx, crz = teleport(nodes[0], message=msg)
    msg = decode(nodes[1], indices, crx, crz)
    message = ''.join(chr(int(msg[i:i+7], 2)) for i in range(0, len(msg), 7))
    
    return message


# In[12]:


message = main()


# In[13]:


print("Received: ", message)


# In[ ]:





# In[ ]:




