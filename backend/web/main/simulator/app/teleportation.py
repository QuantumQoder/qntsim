import logging
import math
from copy import deepcopy
from typing import Dict, List, Literal, Optional, Tuple, Union

from qiskit import *
from qntsim.communication import ATTACK_TYPE, Noise, OnMemoryAttack
from qntsim.kernel import QiskitManager, QutipCircuit, QutipManager
from qntsim.kernel.quantum_kernel import KetState
from qntsim.topology import EndNode
from qntsim.utils import log

# from tabulate import tabulate

# logger = logging.getLogger("main_logger.application_layer." + "teleportation")






class Teleportation():

    def request_entanglements(self, sender: EndNode, receiver: EndNode) -> Tuple[EndNode, List[str]]:
        sender.transport_manager.request(receiver.owner.name,5e12,1,20e12,0,.5,5e12)
        source_node_list=[sender.name]
        return sender,receiver,source_node_list

    def roles(self, alice: EndNode, bob: EndNode) -> Tuple[EndNode, List[str]]:
        sender=alice
        receiver=bob
        print('sender, receiver',sender.owner.name,receiver.owner.name)
        log.logger.info('sender, receiver: '+sender.owner.name+ " " + receiver.owner.name)
        return self.request_entanglements(sender,receiver)



    def alice_keys(self, alice: EndNode) -> Tuple[Union[QiskitManager, QutipManager], int, KetState]:
        qm_alice = alice.timeline.quantum_manager
        for mem_info in alice.resource_manager.memory_manager:
            key=mem_info.memory.qstate_key
            state= qm_alice.get(key)
            print("alice entangled state",state.state)
            return qm_alice,key,state

    def bob_keys(self, bob: EndNode) -> Tuple[Union[QiskitManager, QutipManager], int, KetState]:
        qm_bob = bob.timeline.quantum_manager
        for mem_info in bob.resource_manager.memory_manager:
            key=mem_info.memory.qstate_key
            state= qm_bob.get(key)
            #print("bob keys",key,state)
            return qm_bob,key,state
        

    def  alice_measurement(self,A_0,A_1,alice: EndNode, noise: Dict[str, List[float]] = {}):

        case="psi"
        qm_alice,key,alice_state=self.alice_keys(alice)
        #key_0=qm_alice.new([complex(1/math.sqrt(2)), complex(1/math.sqrt(2))])
        key_0=qm_alice.new([A_0, A_1])
        if (alice_state.state[1]==0 and alice_state.state[2]==0):
            if (alice_state.state[0].real>0 and alice_state.state[3].real>0):
                case="psi+"
                print("00+11")
            elif (alice_state.state[0].real<0 and alice_state.state[3].real<0):
                case="-psi+"
                print("-(00+11)")
            elif (alice_state.state[0].real>0 and alice_state.state[3].real<0):
                case="psi-"
                print("00-11")  
            elif (alice_state.state[0].real<0 and alice_state.state[3].real>0):
                case="-psi-"
                print("-00+11")  
        if (alice_state.state[0]==0 and alice_state.state[3]==0):
            if (alice_state.state[1].real>0 and alice_state.state[2].real>0):
                case="phi+"
                print("01+10")
            elif (alice_state.state[1].real>0 and alice_state.state[2].real<0):
                case="phi-"
                print("01-10") 
            elif (alice_state.state[1].real<0 and alice_state.state[2].real<0):
                case="-phi+"
                print("-01-10") 
            elif (alice_state.state[1].real<0 and alice_state.state[2].real>0):
                case="-phi-"
                print("-01+10") 
            
        print("random qubit alice sending",qm_alice.get(key_0).state)
        random_qubit = qm_alice.get(key_0).state
        circ=QutipCircuit(2)
        circ.cx(0,1)
        circ.h(0)
        readout = noise.pop("readout", [0, 0])
        Noise.implement(noise, circuit = circ, keys = key, quantum_manager = qm_alice)
        circ.measure(0)
        circ.measure(1)
        
        output=qm_alice.run_circuit(circ,[key_0,key])
        # print('output',key_0,key,output)
        Noise.readout(readout, result = output)
        crz=output.get(key_0)
        crx=output.get(key)
        return crz,crx,case, random_qubit,alice_state
        

    def bob_gates(self,crz,crx,case,bob: EndNode, noise: Dict[str, List[float]] = {}):
        readout = noise.pop("readout", [0, 0])
        gatesl=[]
        qm_bob,key,state=self.bob_keys(bob)
        circ=QutipCircuit(1)
        if case=="psi+":

            if crx==1:
                circ.x(0)
                gatesl.append('x')
            if crz==1:
                circ.z(0)
                gatesl.append('z')
                #circ.measure(0)
            
        if case=="-psi+":
            if crz==0 and crx==0:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
                gatesl=['z','x','z','x']

                #circ.measure(0)
            elif crz==0 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)  
                gatesl=['z','x','z']

            elif crz==1 and crx==0:
                circ.x(0)
                circ.z(0)
                circ.x(0)
                gatesl=['x','z','x']

            elif crz==1 and crx==1:
                circ.z(0)
                circ.x(0)
                gatesl=['z','x']

        if case=="psi-":
            if crz==0 and crx==0:
                circ.z(0)
                gatesl=['z']

            elif crz==0 and crx==1:  
                circ.z(0)
                circ.x(0)
                gatesl=['z','x']

            elif crz==1 and crx==0:
                gatesl=[]
                pass

            elif crz==1 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                gatesl=['z','x','z']

        if case=="-psi-":
            if crz==0 and crx==0:
                circ.x(0)
                circ.z(0)
                circ.x(0)
                #circ.measure(0)
                gatesl=['x','z','x']

            elif crz==0 and crx==1:
                circ.x(0)
                circ.z(0)
                gatesl=['x','z']

            elif crz==1 and crx==0:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
                gatesl=['z','x','z','x']

            elif crz==1 and crx==1:
                circ.x(0)
                gatesl=['x']

        if case=="phi+":
            if crz==0 and crx==0:
                circ.x(0)
                gatesl=['x']    
            elif crz==0 and crx==1:
                gatesl=[]
                pass
            elif crz==1 and crx==0:
                circ.x(0)
                circ.z(0)
                gatesl=['x','z']
            elif crz==1 and crx==1:
                circ.z(0)
                gatesl=['z']
        
        if case=="-phi+":
            if crz==0 and crx==0:

                circ.z(0)
                circ.x(0)
                circ.z(0)
                gatesl=['z','x','z']
                
            elif crz==0 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
                gatesl=['z','x','z','x']

            elif crz==1 and crx==0:
                circ.z(0)
                circ.x(0)
                gatesl=['z','x']

            elif crz==1 and crx==1:
                circ.x(0)
                circ.z(0)
                circ.x(0)
                gatesl=['x','z','x']
                
        if case=="-phi-":
            if crz==0 and crx==0:
                print('crz 1')
                circ.x(0)
                circ.z(0)
                gatesl=['x','z']
                    
            elif crz==0 and crx==1:
                print('crz 1')
                circ.x(0)
                circ.z(0)
                circ.x(0)
                gatesl=['x','z','x']

            elif crz==1 and crx==0:
                circ.x(0)
                gatesl=['x']
                
            elif crz==1 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
                gatesl=['z','x','z','x']
        
        if case=="phi-":
            if crz==0 and crx==0:
                print('crz 1') 
                circ.z(0)
                circ.x(0)
                gatesl=['z','x']
                #circ.measure(0)
            elif crz==0 and crx==1:
                print('crz 1')
                circ.z(0)
                gatesl=['z']

            elif crz==1 and crx==0:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                gatesl=['z','x','z']

            elif crz==1 and crx==1:
                gatesl=[]
                pass
        Noise.implement(noise, circuit = circ, keys = key, quantum_manager = qm_bob)
        circ.measure(0)
        
        output=qm_bob.run_circuit(circ,[key])
        print(output, "fuck")
        Noise.readout(readout, result = output)
        print("Bob's state before corrective measures",state.state)
        print('bob final state after corrective measures',qm_bob.get(key).state)
        return state.state, qm_bob.get(key).state,gatesl

    def run(self, alice: EndNode, bob: EndNode, A_0, A_1,
            noise: Dict[str, List[float]] = {},
            attack: Optional[Literal["DS", "EM", "IR"]] = None):
        crz,crx,case, random_qubit,alice_state=self.alice_measurement(A_0,A_1,alice, deepcopy(noise))
        print("Measurement result of random qubit crz",crz)
        log.logger.info(alice.owner.name + " sent measurement results")
        #print("Measurement result of random qubit crz",crz)
        print("Measurement result of alice qubit crx",crx)
        bob_initial_state, bob_final_state,gatesl = self.bob_gates(crz,crx,case,bob, deepcopy(noise))
        log.logger.info(bob.owner.name + " received the final state")
        leaked_bins: List[Optional[str]] = []
        if attack:
            leaked_bins = [OnMemoryAttack.implement(node, node.timeline.quantum_manager, ATTACK_TYPE[attack].value)
                           for node in [alice, bob]]
        
        # initial entanglement alice_bob_entanglement: alice_bob_entangled_state
        # measurement_result_of_random_qubit near alice's end : meas_rq
        # measurement_result_of_alice_qubit  near alice's end :meas_r1
        # bob_initial_state_before_corrective_measures: bob_initial_state
        # bob_final_state_after_corrective_measures:bob_final_state
        res = {
            "alice_bob_entanglement": alice_state.state,
            "random_qubit" : random_qubit,
            "meas_rq":crz,
            "meas_alice":crx,
            "Corrective_operation":gatesl,
            "bob_initial_state" : bob_initial_state,
            "bob_final_state" : bob_final_state
        }
        print(res)
        return res

#################################################################################################

if __name__ == "__main__":
    import json

    topology = json.load(open("topology.json", 'r'))

    from qntsim.layers.application_layer.communication import Network

    network = Network(topology=topology,messages = {('node1','node2'):'hello'})
    node = network.nodes
    alice = node[0]
    bob = node[1]

    aa = Teleportation()
    aa.run(alice,bob,1/math.sqrt(2), 1/math.sqrt(2),noise ={"amp_dmp":[0.9]} )