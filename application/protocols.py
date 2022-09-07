#!/usr/bin/env python
# coding: utf-8
# %%

# %%


def initiate(topology,
             DLCZ=False, bk=True,
             stop_time=10e12, backend="Qutip",
             network_name="name",
             MEMO_FREQ=2e4,
             MEMO_EXPIRE=0,
             MEMO_EFFICIENCY=1,
             MEMO_FIDELITY=0.95,
             DETECTOR_EFFICIENCY=0.9,
             DETECTOR_COUNT_RATE=5e7,
             DETECTOR_RESOLUTION=100,
             SWAP_SUCC_PROB=0.90,
             SWAP_DEGRADATION=0.99,
             ATTENUATION=1e-5,
             QC_FREQ=1e11,
             start_time=5e12, size=1, priority=0, target_fidelity=0.5,
             timeout=5e12,
             correlated=True, relative_phase=False,
             get_graph=False, structure=0):
    import qntsim
    from qntsim.kernel.timeline import Timeline
    Timeline.DLCZ = DLCZ
    Timeline.bk = bk
    from qntsim.topology.topology import Topology
    from qntsim.components.circuit import QutipCircuit
    """
    Method to load the network, request entanglements between nodes and
    initiating the process of simulation.
    
    Parameters:
    topology : string
        String of the json file which contations the topology of the network.
    (optional) DLCZ : bool
        True/False based on the type of entanglement generation.
    (optional) bk : bool
        True/False based on the type of entanglement generation.
    (optional) stop_time : int
        Total runtime of the simulator.
    (optional) backend : string
        Type of the backend on which the simulator would execute.
        Currently, it only supports 'Qutip' backend.
    (optional) network_name : string
        Name of the network.
    (optional, constants) MEMO_FREQ : int
    (optional, constants) MEMO_EXPIRE : int
    (optional, constants) MEMO_EFFICIENCY : int
    (optional, constants) MEMO_FIDELITY : int
    (optional, constants) DETECTOR_EFFICIENCY : int
    (optional, constants) DETECTOR_COUNT_RATE : int
    (optional, constants) DETECTOR_RESOLUTION : int
    (optional, constants) SWAP_SUCC_PROB : float
    (optional, constants) SWAP_DEGRADATION : float
    (optional, constants) ATTENUATION : float
    (optional, constants) QC_FREQ : int
    (optional) start_time : int
        Time to generate the entanglements.
    (optional) size : int
        Number of entanglements requested by protocols.
    (optional) priority : int
        Priority for the request. Lower the value, higher the priority.
    (optional) target_fidelity : float
        Target Fidelity for the request
    (optional) timeout : int
        Timeont for the request.
    (optional) correlated : bool
        Correlation between the qubits in the entanglement. True corresponds
        to correlated spins and False to anti-correlated ones.
    (optional) relative_phase : bool
        Relative phase between the state in the entanglement. True corresponds
        to 180 degree phase difference between the states and False to the
        same phase.
    (optional) get_graph : bool
        Generates the graph of the network
    (optional) structure : int
        Structure for the entanglement between the nodes. '0' corresponds to
        a linear graph and centralized, otherwise.
    
    Returns:
    nodes : list
        List of <EndNode> instances in the network.
    network : Topology
     <Topology> instance of the simulator.
    """
    
    event = Timeline(stop_time=stop_time, backend=backend)
    network = Topology(network_name, event)
    network.load_config(topology)

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
    
    nodes = network.get_nodes_by_type("EndNode")
    if structure:
        for node in nodes[1:]:
            nodes[0].transport_manager.request(node.owner.name,
                                           start_time=start_time, size=size,
                                           end_time=stop_time, priority=priority,
                                           target_fidelity=target_fidelity,
                                           timeout=timeout)
    else:
        for i in range(len(nodes)-1):
            node = nodes[i]
            next_node = nodes[i+1]
            node.transport_manager.request(next_node.owner.name,
                                           start_time=start_time, size=size,
                                           end_time=stop_time, priority=priority,
                                           target_fidelity=target_fidelity,
                                           timeout=timeout)
    
    if get_graph: network.get_virtual_graph()
    event.init()
    event.run()
    
    for node in nodes[:len(nodes)-1]:
        node_qm = node.timeline.quantum_manager
        for info in node.resource_manager.memory_manager:
            try:
                index = info.memory.qstate_key
                pos = node_qm.get(index)
                states = pos.state
                qtc = QutipCircuit(2)
                if correlated:
                    if states[0]==states[3]==0:
                        qtc.x(1)
                        if states[1]==(2*int(relative_phase)-1)*states[2]:
                            qtc.z(0)
                    elif states[0]==(2*int(relative_phase)-1)*states[3]:
                        qtc.z(0)
                else:
                    if states[1]==states[2]==0:
                        qtc.x(1)
                        if states[0]==(2*int(relative_phase)-1)*states[3]:
                            qtc.z(0)
                    elif states[1]==(2*int(relative_phase)-1)*states[2]:
                        qtc.z(0)
                node_qm.run_circuit(qtc, pos.keys)
            except:
                break
                
    return nodes, network

# %%


def teleport(node, message="01001"):
    import math
    from qntsim.components.circuit import QutipCircuit
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

# %%


def string_to_binary(message):
    words = message.split()
    msg = ''
    for word in words:
        msg += ''.join(bin(ord(w))[2:] for w in word)
        msg += '0'+bin(ord(' '))[2:]
    
    return msg

# %%


def get_correct_keys(a, correlated=True, relative_phase=False):
    correct_keys = []
    a_qm = a.timeline.quantum_manager
    for info in a.resource_manager.memory_manager:
        try:
            key = info.memory.qstate_key
            pair = a_qm.get(key)
            state = pair.state
            #print(pair.keys, state)
            '''
            qtc = QutipCircuit(2)
            if state[1]==state[2]==0:
                if state[0]==-state[3]:
                    qtc.z(0)
                qtc.x(1)
            elif state[1]==-state[2]:
                qtc.z(0)
            '''
            if correlated:
                if state[0]==(1-2*int(relative_phase))*state[3]!=0:
                    correct_keys.append(key)
            else:
                if state[1]==(1-2*int(relative_phase))*state[2]!=0:
                    correct_keys.append(key)
        except:
            print("Terminated")
            break
    
    return correct_keys


# %%


def rectify_entanglements(a, correlated=True, relative_phase=False):
    from qntsim.components.circuit import QutipCircuit
    
    a_qm = a.timeline.quantum_manager
    for info in a.resource_manager.memory_manager:
        try:
            key = info.memory.qstate_key
            pair = a_qm.get(key)
            states = pair.state
            qtc = QutipCircuit(2)
            if correlated:
                if states[0]==states[3]==0:
                    qtc.x(1)
                    if states[1]==(2*int(relative_phase)-1)*states[2]:
                        qtc.z(0)
                elif states[0]==(2*int(relative_phase)-1)*states[3]:
                    qtc.z(0)
            else:
                if states[1]==states[2]==0:
                    qtc.x(1)
                    if states[0]==(2*int(relative_phase)-1)*states[3]:
                        qtc.z(0)
                elif states[1]==(2*int(relative_phase)-1)*states[2]:
                    qtc.z(0)
            a_qm.run_circuit(qtc, pair.keys)
        except:
            break
    
    return a

# %%


def generate_topo_file(num_nodes=2, num_servers=[1]):
    assert num_nodes-1==len(num_servers), "Number of server connections should be 1 less than number of nodes"
    topo = {}
    nodes = []
    i = 0
    for j in num_servers:
        for k in range(j):
            nodes.append("s"+str(i+k))
        i+=j
    topo["service_node"] = nodes
    nodes = {}
    j = -1
    for i in range(num_nodes-1):
        j+=1
        nodes.update({"n"+str(i):topo["service_node"][j]})
        #nodes["n"+str(i)] = topo["service_node"][j]
        j+=(num_servers[i]-1)
        nodes.update({"n"+str(i+1):topo["service_node"][j]})
        #nodes["n"+str(i+1)] = topo["service_node"][j]
        #print(nodes)
    topo["end_node"] = nodes
    labels = []
    j = 0
    for i in range(num_nodes-1):
        labels.append("n"+str(i))
        labels+=topo["service_node"][j:j+num_servers[i]]
        #labels.append(topo["service_node"][j:j+num_servers[i]])
        j+=num_servers[i]
    labels.append("n"+str(num_nodes-1))
    table = []
    for i in range(len(labels)):
        row = []
        for j in range(len(labels)):
            if i==j:
                row.append(0)
            else:
                row.append(1e9)
        table.append(row)
    topo["cchannels_table"] = {"type":"RT", "labels": labels, "table":table}
    connections = []
    for i in range(len(labels)-1):
        connections.append({"node1":labels[i],
                            "node2":labels[i+1],
                            "attenuation":1e-5,
                            "distance":70})
    topo["qconnections"] = connections
    
    return topo
