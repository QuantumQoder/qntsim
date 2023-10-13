import json
import logging
from typing import Dict, List, Literal, Optional, Tuple, Union

from qiskit import *
from qntsim.communication import (ATTACK_TYPE, ErrorAnalyzer, Noise,
                                  OnMemoryAttack)
from qntsim.kernel import (DensityManager, QiskitManager, QutipCircuit,
                           QutipManager)
from qntsim.kernel.quantum_kernel import KetState
from qntsim.topology import EndNode
from qntsim.utils import log

# from tabulate import tabulate

# logger = logging.getLogger("main_logger.application_layer." + "ghz")
# logger = log.logger


class GHZ():

    #Requesting transport manager for entanglements
    def request_entanglements(self,
                              endnode1: EndNode,
                              endnode2: EndNode,
                              endnode3: EndNode,
                              middlenode: EndNode) -> Tuple[EndNode, EndNode, EndNode, EndNode, List[str]]:
        log.logger.info("Requesting three two-party entanglements")
        endnode1.transport_manager.request(middlenode.owner.name, 5e12,1, 20e12, 0 , 0.5,2e12) 
        endnode2.transport_manager.request(middlenode.owner.name, 5e12,1, 20e12, 0 , 0.5,2e12) 
        endnode3.transport_manager.request(middlenode.owner.name, 5e12,1, 20e12, 0 , 0.5,2e12) 
        source_node_list: List[str] = [endnode1.name,endnode2.name,endnode3.name]
        return endnode1,endnode2,endnode3,middlenode, source_node_list

    # set's alice , bob ,charlie and middlenode 
    def roles(self,
              alice: EndNode,
              bob: EndNode,
              charlie: EndNode,
              middlenode: EndNode) -> Tuple[EndNode, EndNode, EndNode, EndNode, List[str]]:
        endnode1=alice
        endnode2=bob
        endnode3=charlie
        log.logger.info('endnode1 , endnode2, endnode3, middlenode are '+endnode1.owner.name+ ", "+endnode2.owner.name+ ", "+endnode3.owner.name+ ", "+middlenode.owner.name)
        
        return self.request_entanglements(endnode1,endnode2,endnode3,middlenode)

    # Gets alice's entangled memory state
    def alice_keys(self, alice: EndNode) -> Optional[Tuple[Union[QiskitManager, QutipManager, DensityManager], int, KetState]]:
        qm_alice = alice.timeline.quantum_manager
        for mem_info in alice.resource_manager.memory_manager:
            print(f"\n\n\n {mem_info.state}")
            key=mem_info.memory.qstate_key
            state= qm_alice.get(key)
            print(f"{state} \n\n\n")
            if mem_info.state == 'ENTANGLED':
                print("alice state ",key, state.state)
                return qm_alice,key,state
    
    # Gets bob's entangled memory state
    def bob_keys(self, bob: EndNode) -> Optional[Tuple[Union[QiskitManager, QutipManager, DensityManager], int, KetState]]:
        qm_bob = bob.timeline.quantum_manager
        for mem_info in bob.resource_manager.memory_manager:
            if mem_info.state == 'ENTANGLED':
                key=mem_info.memory.qstate_key
                state= qm_bob.get(key)
                print("bob state",key,state.state)
                return qm_bob,key,state

    # Gets charlie's entangled memory state
    def charlie_keys(self, charlie: EndNode) -> Optional[Tuple[Union[QiskitManager, QutipManager, DensityManager], int, KetState]]:
        qm_charlie = charlie.timeline.quantum_manager
        for mem_info in charlie.resource_manager.memory_manager:
            if mem_info.state == 'ENTANGLED':
                key=mem_info.memory.qstate_key
                state= qm_charlie.get(key)
                print("charlie state",key,state.state)
                return qm_charlie,key,state
    
    #Gets middlenode's entangled memory state
    def middle_keys(self, middlenode: EndNode) -> Optional[Tuple[Union[QiskitManager, QutipManager, DensityManager], int, KetState]]:
        qm_middle = middlenode.timeline.quantum_manager
        middle_entangled_keys=[]
        for mem_info in middlenode.resource_manager.memory_manager:
            # print('middle memory info', mem_info)
            if mem_info.state == 'ENTANGLED':
                key=mem_info.memory.qstate_key
                state= qm_middle.get(key)
                middle_entangled_keys.append(key)
                print("middlenode state",key,state.state,middle_entangled_keys)
        return qm_middle,key,state,middle_entangled_keys


    #alice_keys()
    #bob_keys()
    #charlie_keys()
    #middle_keys()

    def run(self, alice: EndNode, bob: EndNode, charlie: EndNode, middlenode: EndNode,
            noise: Dict[str, List[float]] = {},
            attack: Optional[Literal["DS", "EM", "IR"]] = None):
        readout = noise.pop("readout", [0, 0])
        qm_alice,alice_key,ialicestate=self.alice_keys(alice)
        print('Alicerun',qm_alice,alice_key,ialicestate.state)
        qm_bob,bob_key,ibobstate=self.bob_keys(bob)
        qm_charlie,charlie_key,icharliestate=self.charlie_keys(charlie)
        qm_middle,middle_key,state,middle_entangled_keys=self.middle_keys(middlenode)
        leaked_bins: List[Optional[str]] = []
        if attack:
            leaked_bins = [OnMemoryAttack.implement(node, quantum_manager, ATTACK_TYPE[attack].value)
                           for node, quantum_manager in zip([alice, bob, charlie, middlenode],
                                                            [qm_alice, qm_bob, qm_charlie, qm_middle])]

        circ = QutipCircuit(3)
        circ.cx(0,2)
        circ.cx(0,1)
        circ.h(0)
        Noise.implement(noise, circuit = circ)
        circ.measure(0)
        circ.measure(1)
        circ.measure(2)

        output = qm_middle.run_circuit(circ,middle_entangled_keys)
        Noise.implement(readout = readout, result = output)
        print("Output", output)
        ghz_state = qm_middle.get(middle_key).state
        print("\nGHZ State\n",  qm_middle.get(middle_key).state)
        log.logger.info("obtained GHZ state: " + str(qm_middle.get(alice_key).state))
        print("\nGHZ State alice\n",  qm_middle.get(alice_key).state)
        print("\nGHZ State bob\n",  qm_middle.get(bob_key).state)
        print("\nGHZ State charlie\n",  qm_middle.get(charlie_key).state)
        res = {
            "initial_alice_state":ialicestate.state,          
            "initial_bob_state":ibobstate.state,
            "initial_charlie_state":icharliestate.state,          
            "final_alice_state":qm_alice.get(alice_key).state ,
            "final_bob_state": qm_bob.get(bob_key).state,
            "final_charlie_state":qm_charlie.get(charlie_key).state,
            
            "alice_state":qm_middle.get(alice_key).state ,
            "bob_state": qm_middle.get(bob_key).state,
            "charlie_state":qm_middle.get(charlie_key).state,
            "ghz_state" : ghz_state
        }
        print(res)
        return res
        # print("Output", output, qm_middle.get(alice_key))

if __name__=="__main__":
    import json
    topology = json.load(open("topology.json", 'r'))
    # print(topology)
    from qntsim.core.kernel.timeline import Timeline
    from qntsim.core.topology.topology import Topology
    net_topo = Topology("", Timeline(10e12, "Qutip"))
    net_topo.load_config_json(topology)
    # net_topo.get_virtual_graph()
    aa = GHZ()
    alice,bob,charlie, service_node = aa.roles(net_topo.nodes.get("node1"),
                                               net_topo.nodes.get("node2"),
                                               net_topo.nodes.get("node3"),
                                               net_topo.nodes.get("service"))
    aa.run(alice,bob,charlie, service_node)
    # print(node)