#!/usr/bin/env python
# coding: utf-8
# %%

# There are two classes in this module. The classes generate ghz states, but each one based on a different structure. As is evident from their names, 'Centralized_GHZ' creates nodes in a way that all the involved parties are entangled to a central node among them. The second class, 'Linearized_GHZ' follows a different approach. There's no central node in this picture. Each node is entangled to the next in a linear fashion, just like a chain.
# 
# In the 'Centralized_GHZ', the central node creates bell entanglements with all the remaining parties, performs some local unitary operations on its extra qubits and filtering them out through measurement, thus, creating a ghz state among the remaining set of qubits.
# 
# In the 'Linearized_GHZ', there are no central nodes. All the nodes are connected one after the another, just like in a chain. Thus, all the parties except the ones at the end of the chains performs local unitary operatins thus, linking up the qubits in a chain.

# %%


class Centralized_GHZ:
    
    """
    The class represents GHZ generation protocol from a collection of Bell
    pairs, using the central node structure.
    """
    
    def __init__(self, topology, size=1, get_graph=False):
        from protocols import initiate

        nodes, network = initiate(topology=topology, size=size,
                                  get_graph=get_graph, structure=1)
        corrections = self._to_ghz(nodes, size=size)
        self._apply_corrections(nodes[0], corrections)
        self.nodes = nodes
        self.network = network
    
    def __get_keys(self, nodes):
        """
        Method to request the keys of all the nodes in the network.
        
        Parameters:
        nodes : list(Type)
            List of <EndNode> instances from the network.
        
        Returns:
        all_keys : list(Type)
            List of list of keys of each node.
        """
        
        all_keys = []
        qm = nodes[0].timeline.quantum_manager
        for node in nodes:
            keys = []
            for info in node.resource_manager.memory_manager:
                if info.state=='ENTANGLED':
                    key = info.memory.qstate_key
                    keys.append(key)
            all_keys.append(keys)

        return all_keys
    
    def _to_ghz(self, nodes, size=1):
        from qntsim.components.circuit import QutipCircuit
        """
        Method to convert the Bell pairs into GHZ states.
        
        Parameters:
        nodes : list(Type)
            List of <EndNode> instances from the network.
        (optional) size : int(Type)
            Number of entanglements required/present in the network.
        
        Returns:
        corrections : list(Type)
            List of measurement outcomes of the filtered out qubits.
            Based on these measurement outcomes, the remaining nodes would
            perform Pauli corrections to their qubits.
        """

        qtc = QutipCircuit(len(nodes)-1)
        for i in range(1, len(nodes)-1):
            qtc.cx(0, i)
            qtc.measure(i)

        corrections = []
        all_keys = self.__get_keys(nodes[1:])
        qm = nodes[0].timeline.quantum_manager
        for i in range(size):
            correction = {}
            middle_keys = []
            for key in all_keys:
                state = qm.get(key[i])
                keys = state.keys.copy()
                keys.remove(key[i])
                middle_keys.append(keys[0])
            output = qm.run_circuit(qtc, middle_keys)
            for keys in all_keys[1:]:
                correction[keys[i]] = output.get(middle_keys.pop(1))
            corrections.append(correction)

        return corrections
    
    def _apply_corrections(self, node, corrections):
        from qntsim.components.circuit import QutipCircuit
        """
        Method to apply Pauli corrections to the remaining qubits.
        
        Parameters:
        node : EndNode(Type)
            Central <EndNode> instance from the network.
        corrections : list(Type)
            List of measurement outcomes of the filtered out qubits.
        """
        
        qm = node.timeline.quantum_manager
        qtc = QutipCircuit(1)
        qtc.x(0)
        for i in range(len(corrections)):
            for key, value in corrections[i].items():
                if value==1:
                    qm.run_circuit(qtc, [key])


# %%


'''
c_ghz = Centralized_GHZ("ghz (1).json", size=2)
nodes = c_ghz.nodes
network = c_ghz.network

qm = nodes[0].timeline.quantum_manager
for node in nodes:
    print(node.owner.name)
    for info in node.resource_manager.memory_manager:
        if info.state=='ENTANGLED':
            key = info.memory.qstate_key
            state = qm.get(key)
            print(state.keys, state.state)

network.get_virtual_graph()
'''


# %%


class Linearized_GHZ:
    
    """
    The class represents GHZ generation protocol from a collection of Bell
    pairs, using the linear structure.
    """
    
    def __init__(self, topology, size=1, get_graph=False):
        from protocols import initiate

        nodes, network = initiate(topology=topology, size=size,
                                  get_graph=get_graph)
        corrections = self._to_ghz(nodes, size=size)
        self._apply_corrections(nodes[0], corrections)
        self.nodes = nodes
        self.network = network
    
    def __get_keys(self, node):
        """
        Method to request the keys of next node in the network.
        
        Parameters:
        node : EndNode(Type)
            Next <EndNode> instance from the network.
        
        Returns:
        indices : list(Type)
            List of the keys of the next node.
        """
        indices = []
        qm = node.timeline.quantum_manager
        for info in node.resource_manager.memory_manager:
            try:
                key = info.memory.qstate_key
                state = qm.get(key)
                keys = state.keys.copy()
                keys.remove(key)
                indices.append(keys[0])
            except:
                return indices

        return indices
    
    def _to_ghz(self, nodes, size=1):
        from qntsim.components.circuit import QutipCircuit
        """
        Method to convert the Bell pairs into GHZ states.
        
        Parameters:
        nodes : list(Type)
            List of <EndNode> instances from the network.
        (optional) size : int(Type)
            Number of entanglements required/present in the network.
        
        Returns:
        corrections : list(Type)
            List of measurement outcomes of the filtered out qubits.
            Based on these measurement outcomes, the next node would
            perform Pauli corrections to their qubits.
        """

        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.measure(1)

        indices = self.__get_keys(nodes[0])
        qm = nodes[0].timeline.quantum_manager
        corrections = []
        for node in nodes[1:len(nodes)-1]:
            correction = {}
            for i in range(size):
                info = node.resource_manager.memory_manager[i]
                key = info.memory.qstate_key
                if key in indices: continue
                state = qm.get(key)
                keys = state.keys.copy()
                keys.remove(key)
                output = qm.run_circuit(qtc, [indices[i], key])
                correction[keys[0]] = output.get(key)
            corrections.append(correction)

        return corrections

    def _apply_corrections(self, node, corrections):
        from qntsim.components.circuit import QutipCircuit
        """
        Method to apply Pauli corrections to the next qubit.
        
        Parameters:
        node : EndNode(Type)
            <EndNode> instance from the network.
        corrections : list(Type)
            List of measurement outcomes of the filtered out qubits.
        """
        
        qm = node.timeline.quantum_manager
        qtc = QutipCircuit(1)
        qtc.x(0)
        for i in range(len(corrections)):
            for key, value in corrections[i].items():
                if value==1:
                    qm.run_circuit(qtc, [key])


# %%


'''
l_ghz = Linearized_GHZ(topology="ghz_qss(1).json", size=2)
nodes = l_ghz.nodes

qm = nodes[0].timeline.quantum_manager
for node in nodes:
    print(node.owner.name)
    for info in node.resource_manager.memory_manager:
        if info.state=='ENTANGLED':
            key = info.memory.qstate_key
            state = qm.get(key)
            print(state.keys, state.state)

l_ghz.network.get_virtual_graph()
'''


# %%




