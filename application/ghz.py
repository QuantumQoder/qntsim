from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.topology.topology import Topology
from tabulate import tabulate
from qntsim.components.circuit import QutipCircuit
from qiskit import *
from qutip.qip.operations import gate_sequence_product
#from qiskit.ignis.verification import marginal_counts
from qiskit.quantum_info import random_statevector
import math

class GHZ():
    def request_entanglements(self,endnode1,endnode2,endnode3,middlenode):
        endnode1.transport_manager.request(middlenode.owner.name, 5e12,1, 20e12, 0 , 0.5,2e12) 
        endnode2.transport_manager.request(middlenode.owner.name, 5e12,1, 20e12, 0 , 0.5,2e12) 
        endnode3.transport_manager.request(middlenode.owner.name, 5e12,1, 20e12, 0 , 0.5,2e12) 

        
        return endnode1,endnode2,endnode3,middlenode

    def roles(self,alice,bob,charlie,middlenode):
        endnode1=alice
        endnode2=bob
        endnode3=charlie
        print('endnode1,endnode2,endnode3,middle',endnode1.owner.name,endnode2.owner.name,endnode3.owner.name,middlenode.owner.name)
        return self.request_entanglements(endnode1,endnode2,endnode3,middlenode)


    def alice_keys(self,alice):
        qm_alice = alice.timeline.quantum_manager
        for mem_info in alice.resource_manager.memory_manager:
            if mem_info.state == 'ENTANGLED':
                key=mem_info.memory.qstate_key
                state= qm_alice.get(key)
                print("alice state ",key, state.state)
                return qm_alice,key,state

    def bob_keys(self,bob):
        qm_bob = bob.timeline.quantum_manager
        for mem_info in bob.resource_manager.memory_manager:
            if mem_info.state == 'ENTANGLED':
                key=mem_info.memory.qstate_key
                state= qm_bob.get(key)
                print("bob state",key,state.state)
                return qm_bob,key,state

    def charlie_keys(self,charlie):
        qm_charlie = charlie.timeline.quantum_manager
        for mem_info in charlie.resource_manager.memory_manager:
            if mem_info.state == 'ENTANGLED':
                key=mem_info.memory.qstate_key
                state= qm_charlie.get(key)
                print("charlie state",key,state.state)
                return qm_charlie,key,state

    def middle_keys(self,middlenode):
        qm_middle = middlenode.timeline.quantum_manager
        for mem_info in middlenode.resource_manager.memory_manager:
            # print('middle memory info', mem_info)
            if mem_info.state == 'ENTANGLED':
                key=mem_info.memory.qstate_key
                state= qm_middle.get(key)
                print("middlenode state",key,state.state)
                return qm_middle,key,state


    #alice_keys()
    #bob_keys()
    #charlie_keys()
    #middle_keys()

    def perform_ghz(self,alice,bob,charlie,middlenode):

        qm_alice,alice_key,state=self.alice_keys(alice)
        #print('Alice',qm_alice,alice_key,state)
        qm_bob,bob_key,state=self.bob_keys(bob)
        qm_charlie,charlie_key,state=self.charlie_keys(charlie)
        qm_middle,middle_key,state=self.middle_keys(middlenode)

        circ = QutipCircuit(3)
        circ.cx(0,2)
        circ.cx(0,1)
        circ.h(0)
        circ.measure(0)
        circ.measure(1)
        circ.measure(2)
        output = qm_middle.run_circuit(circ,[alice_key,bob_key,charlie_key])
        print("Output", output)
        print("\nGHZ State\n",  qm_middle.get(middle_key).state)
        # print("Output", output, qm_middle.get(alice_key))


    #perform_ghz()

# network_config : String : File path for json configuration file
# endnode1 : String : GHZ end node 1 name
# endnode2 : String : GHZ end node 2 name
# endnode3 : String : GHZ end node 3 name
# middlenode : String : GHZ middlenode name

# def ghz(network_config, endnode1,endnode2,endnode3,middlenode):
#     from qntsim.kernel.timeline import Timeline
#     Timeline.DLCZ=False
#     Timeline.bk=True
#     from qntsim.topology.topology import Topology

#     tl = Timeline(4e12,"Qiskit")

#     network_topo = Topology("network_topo", tl)
#     network_topo.load_config(network_config)

#     alice=network_topo.nodes[endnode1]
#     bob = network_topo.nodes[endnode2]
#     charlie=network_topo.nodes[endnode3]
#     middlenode=network_topo.nodes[middlenode]
#     ghz= GHZ()
#     alice,bob,charlie,middlenode=ghz.roles(alice,bob,charlie,middlenode)
#     tl.init()
#     tl.run()  
#     ghz.perform_ghz(alice,bob,charlie,middlenode)

# ghz("../example/4node.json", "a", "b", "s1", "s2")