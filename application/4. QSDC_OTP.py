#!/usr/bin/env python
# coding: utf-8

# # Importing necessary modules

# In[1]:


import qntsim, math
from numpy.random import randint
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ = False
Timeline.bk = True
from qntsim.topology.topology import Topology
from qntsim.components.circuit import QutipCircuit


# # Setting up the device parameters

# In[2]:


def set_params(network:Topology):
    MEMO_FREQ = 2e4
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 0.95
    
    DETECTOR_EFFICIENCY = 0.9
    DETECTOR_COUNT_RATE = 5e7
    DETECTOR_RESOLUTION = 100
    
    SWAP_SUCC_PROB = 0.90
    SWAP_DEGRADATION = 0.99
    
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    
    for node in network.get_nodes_by_type("EndNode"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)
    
    for node in network.get_nodes_by_type("ServiceNode"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)
        
    for node in network.get_nodes_by_type("BSMNode"):
        node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
    
    for router in network.get_nodes_by_type("QuantumRouter"):
        router.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        router.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
    
    for qchannel in network.qchannels:
        qchannel.attenuation = ATTENUATION
        qchannel.frequency = QC_FREQ


# ## Preparing the batches
# 
# The receiver prepares the batches of photons for carrying out the protocol. It initializes each photon with a random state among $|0\rangle, |1\rangle, |+\rangle$ and $|-\rangle$ and sends the photons to the sender for encoding the message into them.

# In[3]:


def prepare(node, size=1):
    from qntsim.components.circuit import QutipCircuit
    """
    Method to prepapre the batch of photons required for carrying out the protocol
    
    Parameters:
    node : <EndNode>
        The receiver node who prepapres the batch of photons
    size : int
        Number of total photons required for communication
    
    Returns:
    node : <EndNode>
        The node with its photon carrying random initial states
    initials : numpy.ndarray
        Array of initial states applied to the batch of photons
    """
    
    initials = randint(4, size=size)
    qm = node.timeline.quantum_manager
    for i in range(size):
        s = initials[i]
        qtc = QutipCircuit(1)
        if s%2==1: qtc.x(0)
        if int(s/2)==1: qtc.h(0)
        info = node.resource_manager.memory_manager[i]
        key = info.memory.qstate_key
        qm.run_circuit(qtc, [key])
    
    return node, initials


# ## Teleporting the message
# 
# The sender encodes their message into the batch of photons through the local operations $I$ and $i\sigma_y$, respectively for 0 and 1 and, then returns back the batch to the receiver.

# In[4]:


def teleport(node, message="01001"):
    from qntsim.components.circuit import QutipCircuit
    """
    Method to the message over the batch of photons
    
    Parameters:
    node : <EndNode>
        The sender node
    message : str
        The message to be teleported
    
    Returns:
    node : <EndNode>
        The updated node carrying the encoded message
    """
    
    size = len(message)
    qm = node.timeline.quantum_manager
    for i in range(size):
        msg = message[i]
        if msg=='1':
            qtc = QutipCircuit(1)
            qtc.x(0)
            qtc.z(0)
            info = node.resource_manager.memory_manager[i]
            key = info.memory.qstate_key
            qm.run_circuit(qtc, [key])
    
    return node


# ## Decoding the message
# 
# The receiver then measure out the photons, and using their initial states, decodes the message conveyed to them.

# In[5]:


def decode(node, initials):
    from qntsim.components.circuit import QutipCircuit
    """
    Method to decode the message received by the other party
    
    Parameters:
    node : <EndNode>
        The node with the encoded message
    initials : list/numpy.ndarray
        List/array of initial states of photons
    """
    
    msg = ''
    size = len(initials)
    qm = node.timeline.quantum_manager
    for i in range(size):
        initial = initials[i]
        info = node.resource_manager.memory_manager[i]
        key = info.memory.qstate_key
        qtc = QutipCircuit(1)
        if int(initial/2)==1: qtc.h(0)
        qtc.measure(0)
        output = qm.run_circuit(qtc, [key])
        msg+=str(int(initial%2!=output.get(key)))
    message = ''.join(chr(int(msg[i:i+7], 2)) for i in range(0, len(msg), 7))
    print("Received: ", message)
    
    return None


# # The main() function
# 
# The main() function is the handler of the protocol. It
# - creates the network,
# - encodes the message into binary and,
# - calls the functions to execute the protocol.

# In[6]:


def main(message="Hello World"):
    """
    Method to execute the whole protocol
    
    Parameters:
    message : str
        The message to be teleported over the network
    """
    
    print("Teleport: ", message)
    stop_time = 10e12
    event = Timeline(stop_time=stop_time, backend="Qutip")
    network = Topology("network", event)
    network.load_config("/Users/aman/QNT/QNTSim/application/test.json")
    set_params(network=network)
    nodes = network.get_nodes_by_type("EndNode")
    words = message.split()
    msg = ''
    for word in words:
        msg+=''.join(bin(ord(w))[2:] for w in word)
        msg+='0'+bin(ord(' '))[2:]
    size = len(msg)
    node, initials = prepare(nodes[0], size=size)
    node = teleport(node, message=msg)
    decode(node, initials)


# In[7]:


main()


# In[ ]:




