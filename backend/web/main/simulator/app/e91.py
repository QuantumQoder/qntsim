import logging
import math
import random
from copy import deepcopy
from typing import Dict, List, Tuple, Union

import numpy as np
from qntsim.communication.noise import Noise
from qntsim.kernel.circuit import BaseCircuit
from qntsim.kernel.quantum_kernel import QiskitManager, QutipManager
from qntsim.topology.node import EndNode

logger = logging.getLogger("main_logger.application_layer." + "e91")


_psi_minus = [complex(0) , complex(math.sqrt(1 / 2)), -complex(math.sqrt(1 / 2)), complex(0)]


class E91():

    # Request transport manager  for entanglements
    def request_entanglements(self, sender: EndNode, receiver: EndNode, n: int) -> Tuple[EndNode, List[str]]:
        sender.transport_manager.request(receiver.owner.name,3e12,n,20e12,0,.7,5e12)
        source_node_list=[sender.name]
        return sender,receiver,source_node_list
    

    # Sets the sender and receiver as alice and bob respectively, and request entanglements 
    def roles(self, alice: EndNode, bob: EndNode, n: int) -> Tuple[EndNode, List[str]]:
        sender=alice
        receiver=bob
        print('sender, receiver',sender.owner.name,receiver.owner.name)
        logger.info('sender, receiver are '+sender.owner.name+" "+receiver.owner.name)
        return self.request_entanglements(sender,receiver,n)

    # circuit measurements
    def measurement(self, qm: Union[QiskitManager, QutipManager],
                    choice: int, key: int, noise: Dict[str, List[float]] = {}) -> Dict[int, int]:
        readout = noise.pop("readout", [0, 0])
        circ = BaseCircuit("Qutip", 1)
        if choice % 2 == 0:
            circ.s(0)
            circ.h(0)
        if choice == 2:  
            circ.t(0)
        if choice == 4: 
            circ.tdg(0)
        if choice != 3: circ.h(0)
        Noise.implement(noise, circuit = circ, keys = key, quantum_manager = qm)
        circ.measure(0)
        output = qm.run_circuit(circ, [key])
        Noise.readout(readout, result = output)
        return output
    
   
    ###Set  entangled state to psi_minus 
    ###TODO: Unitary Operations to change state instead of hard coding value

    def set_state_psi_minus(self, alice: EndNode, bob: EndNode):
        
        qm_alice=alice.timeline.quantum_manager
        qm_bob=bob.timeline.quantum_manager
        bob_entangled_key=[] ##Entangled states/ of Bob Nodes
        alice_bob_map={}  ### Bob key<---->Alice key Map of entanglement
        
        for info in bob.resource_manager.memory_manager:
            
            if info.state=='ENTANGLED':

                key=info.memory.qstate_key
                state0=qm_bob.get(key) 
                
                ##Update bob's state in all keys associated with the state at bob node
                for key1 in state0.keys:
                    qm_bob.states[key1].state = _psi_minus
                
                bob_entangled_key.append(key) 
        

        for info in alice.resource_manager.memory_manager:
            if info.state=='ENTANGLED':
                
                key=info.memory.qstate_key
                state0=qm_alice.get(key) 
               
                ##Update alice's state in all keys associated with the state at alice node
                for key1 in state0.keys:
                    qm_alice.states[key1].state = _psi_minus
                    if key1!=key :
                        alice_bob_map[key1]=key          

        return alice,bob,alice_bob_map,bob_entangled_key


    ### Alice measurement of entangled qubits
    def alice_measurement(self, alice: EndNode, noise: Dict[str, List[float]] = {}):
        choice=[1,2,3]
        qm_alice=alice.timeline.quantum_manager
        meas_results_alice={} ###entangled key <---> measure result at that qubit MAP
        alice_choice_list={} ###entangled key <---> Random Basis Choice of Alice MAP
        # noise = {"pauli": [0,0.9,0,0], "reset": [], "amp_damp": [], "readout": []}

        for info in alice.resource_manager.memory_manager:
            if info.state=='ENTANGLED':
                
                key=info.memory.qstate_key 
                state1=qm_alice.get(key)
                
                ##Alice Random Basis Choice and measure result for a particular entangled qubit
                alice_choice=random.randint(1, 3)
                meas_results_alice[key]=self.measurement(qm_alice,alice_choice,key, noise)
                alice_choice_list[key]=alice_choice
        Noise.reset(noise.get("reset", 0), alice.resource_manager.memory_manager, BaseCircuit("Qutip", 1), qm_alice)

        return alice_choice_list,meas_results_alice

   
    ### Bob measurement of entangled qubits
    def bob_measurement(self, bob: EndNode, bob_entangled_key: List[int], noise: Dict[str, List[float]] = {}):
        choice=[2,3,4]
        qm_bob=bob.timeline.quantum_manager
        meas_results_bob={} ###entangled key <---> measure result at that qubit: MAP
        bob_choice_list={} ###entangled key <---> Random Basis Choice of Bob :MAP
        # noise = {"pauli": [0,0.9,0,0], "reset": [], "amp_damp": [], "readout": []}
          
        for info in bob.resource_manager.memory_manager:
            
            key=info.memory.qstate_key
            state0=qm_bob.get(key) 

            ##Bob Random Basis Choice and measure result for a particular entangled qubit
            if key in bob_entangled_key:
                bob_choice=random.randint(2, 4)
                meas_results_bob[key]=self.measurement(qm_bob,bob_choice,key, noise)
                bob_choice_list[key]=bob_choice
        Noise.reset(noise.get("reset", 0), bob.resource_manager.memory_manager, BaseCircuit("Qutip", 1), qm_bob)
        return bob_choice_list,meas_results_bob

    

    ### ACTION OF EVE:
        ##Eve has access to both Alice Qubit or Bob Qubit Or Both Qubits( Hence have access to the node's quantum memory information)
            #Eve detects/measures those Qubits 
            #where alice and bob doesnt have knowledge of eve's presence  
            #Hence ALice and Bob Continues to measure the qubits     
    def eve_measurement(self, alice: EndNode, bob: EndNode,
                        alice_bob_map: Dict[int, int], bob_entangled_key: List[int]):
               # eveMeasurementChoices = []

        

        choice=[2,3] ### These basis choices are involved in Secret key detection
        qm_alice=alice.timeline.quantum_manager
        qm_bob=bob.timeline.quantum_manager
        eve_meas_results_alice={} ##Eve measurement of Alice side Qubit
        eve_alice_choice_list={}  ## Random Basis Choice for Above
        eve_meas_results_bob={} ##Eve measurement of Bob side Qubit
        eve_bob_choice_list={}  ##Random Basis Choice for Above

        

        for bob_key in bob_entangled_key:
            alice_key=alice_bob_map[bob_key]
            if random.uniform(0, 1) <= 0.5:
                eve_alice_choice_list[alice_key]=2
                eve_bob_choice_list[bob_key]=2
            else:
                eve_alice_choice_list[alice_key]=3
                eve_bob_choice_list[bob_key]=3
          
        
        for info in alice.resource_manager.memory_manager:  
            if info.state=='ENTANGLED': 
                key=info.memory.qstate_key 
                eve_alice_choice= eve_alice_choice_list[key]
                eve_meas_results_alice[key]=self.measurement(qm_alice,eve_alice_choice,key)
                
       
        for info in bob.resource_manager.memory_manager:
            key=info.memory.qstate_key
            if key in bob_entangled_key:
                eve_bob_choice= eve_bob_choice_list[key]
                eve_meas_results_bob[key]=self.measurement(qm_bob,eve_bob_choice,key)
               
       
        return eve_meas_results_alice,eve_alice_choice_list,eve_meas_results_bob,eve_bob_choice_list
        
    
    def chsh_correlation(self,alice_meas,bob_meas,alice_choice,bob_choice,bob_entangled_key,alice_bob_map):

        countA1B2=[0,0,0,0]
        countA1B4=[0,0,0,0]
        countA3B2=[0,0,0,0]
        countA3B4=[0,0,0,0]
        check_list = ['00','01','10','11']
        res=[]

        for bob_key in bob_entangled_key:

            bob_meas_i=list(bob_meas[bob_key].items())
            alice_key=alice_bob_map[bob_key]
            alice_meas_i=list(alice_meas[alice_key].items())

            res2=str(alice_meas_i[0][1])+str(bob_meas_i[0][1])
           
            if (alice_choice[alice_key]==1 and bob_choice[bob_key]==2):
                for j in range(4):
                    if res2 == check_list[j]:
                        countA1B2[j] +=1
            if (alice_choice[alice_key]==1 and bob_choice[bob_key]==4):
                for j in range(4):
                    if res2 == check_list[j]:
                        countA1B4[j] +=1

            if (alice_choice[alice_key]==3 and bob_choice[bob_key]==2):
                for j in range(4):
                    if res2 == check_list[j]:
                        countA3B2[j] +=1
            
            if (alice_choice[alice_key]==3 and bob_choice[bob_key]==4):
                for j in range(4):
                    if res2 == check_list[j]:
                        countA3B4[j] +=1

        total12=sum(countA1B2)
        total14=sum(countA1B4)
        total32=sum(countA3B2)
        total34=sum(countA3B4)

        try:
            expect12 = (countA1B2[0]-countA1B2[1]-countA1B2[2]+countA1B2[3])/total12
            expect14 = (countA1B4[0]-countA1B4[1]-countA1B4[2]+countA1B4[3])/total14
            expect32 = (countA3B2[0]-countA3B2[1]-countA3B2[2]+countA3B2[3])/total32
            expect34 = (countA3B4[0]-countA3B4[1]-countA3B4[2]+countA3B4[3])/total34
            corr=expect12-expect14+expect32+expect34

            return corr
        except ZeroDivisionError:
            print(f'Error occured,Retry e91 again')
            return 0


    ####TODO: Generalise Eve's Access to qubits
                ## All entangled qubits /only few entangled qubits
                ## Only Alice or bob or Both
    def eve_run(self,alice,bob,n):

        alice,bob,alice_bob_map,bob_entangled_key=self.set_state_psi_minus(alice,bob)

        eve_meas_alice,eve_alice_choice_list,eve_meas_bob,eve_bob_choice_list=self.eve_measurement(alice,bob,alice_bob_map, bob_entangled_key)

        alice_choice,alice_meas=self.alice_measurement(alice)

        bob_choice,bob_meas=self.bob_measurement(bob,bob_entangled_key)

        key_mismatch=0

        alicechoice , bobchoice ,evealicechoice ,evebobchoice = [],[] ,[],[]
        aliceresults ,bobresults ,evealiceresults ,evebobresults = [],[] ,[],[]
   
        alice_keyl, bob_keyl,eve_keyl=[],[],[] ###Alice , Bob ,Eve Key List
        alice_results,bob_results,eve_alice_results,eve_bob_results ={},{},{},{} ### Qubit Key <---> Meas results MAPs

        for bob_key in bob_entangled_key:
           
            bob_meas_i=list(bob_meas[bob_key].items())
            alice_key=alice_bob_map[bob_key]
            alice_meas_i=list(alice_meas[alice_key].items())
            eve_meas_bob_i=list(eve_meas_bob[bob_key].items())
            eve_meas_alice_i=list(eve_meas_alice[alice_key].items())

            if alice_meas_i[0][1]==0 and bob_meas_i[0][1] ==0:
                alice_results[alice_key]=-1 
                bob_results[bob_key]=-1

            if alice_meas_i[0][1]==0 and bob_meas_i[0][1] ==1:
                alice_results[alice_key]=1 
                bob_results[bob_key]=-1

            if alice_meas_i[0][1]==1 and bob_meas_i[0][1] ==0:
                alice_results[alice_key]=-1 
                bob_results[bob_key]=1

            if alice_meas_i[0][1]==1 and bob_meas_i[0][1] ==1:
                alice_results[alice_key]=1  
                bob_results[bob_key]=1
            
            if eve_meas_alice_i[0][1]==0 and eve_meas_bob_i[0][1] ==0:
                eve_alice_results[alice_key]=-1 
                eve_bob_results[bob_key]=-1
                
            if eve_meas_alice_i[0][1]==0 and eve_meas_bob_i[0][1] ==1:
                eve_alice_results[alice_key]=1 
                eve_bob_results[bob_key]=-1
                
            if eve_meas_alice_i[0][1]==1 and eve_meas_bob_i[0][1] ==0:
                eve_alice_results[alice_key]=-1 
                eve_bob_results[bob_key]=1
                
            if eve_meas_alice_i[0][1]==1 and eve_meas_bob_i[0][1] ==1:
                eve_alice_results[alice_key]=1 
                eve_bob_results[bob_key]=1
                

            if (alice_choice[alice_key]==2 and bob_choice[bob_key]==2) or (alice_choice[alice_key]==3 and bob_choice[bob_key]==3):
                print('Base match',alice_meas[alice_key],bob_meas[bob_key])
                eve_keyl.append([str(eve_alice_results[alice_key]),str(eve_bob_results[bob_key])])
                alice_keyl.append(str(alice_results[alice_key]))
                bob_keyl.append(str(-bob_results[bob_key]))
                
            alicechoice.append(str(alice_choice[alice_key]))
            aliceresults.append(str(alice_results[alice_key]))
            bobchoice.append(str(bob_choice[bob_key]))
            bobresults.append(str(bob_results[bob_key]))
            evealicechoice.append(str(eve_alice_choice_list[alice_key]))
            evebobchoice.append(str(eve_bob_choice_list[bob_key]))
            evealiceresults.append(str(eve_alice_results[alice_key]))
            evebobresults.append(str(eve_bob_results[bob_key]))
            
            alicechoice= list(map(lambda x: x.replace('1', 'X'), alicechoice))
            alicechoice= list(map(lambda x: x.replace('2', 'W'), alicechoice))
            alicechoice= list(map(lambda x: x.replace('3', 'Z'), alicechoice))
            alicechoice= list(map(lambda x: x.replace('4', 'V'), alicechoice))
            aliceresults= list(map(lambda x: x.replace('-1', '0'), aliceresults))
            alice_keyl= list(map(lambda x: x.replace('-1', '0'), alice_keyl))
           
           
            bobchoice= list(map(lambda x: x.replace('1', 'X'), bobchoice))
            bobchoice= list(map(lambda x: x.replace('2', 'W'), bobchoice))
            bobchoice= list(map(lambda x: x.replace('3', 'Z'), bobchoice))
            bobchoice= list(map(lambda x: x.replace('4', 'V'), bobchoice))
            bobresults= list(map(lambda x: x.replace('-1', '0'), bobresults))
            bob_keyl= list(map(lambda x: x.replace('-1', '0'), bob_keyl))


            evealicechoice= list(map(lambda x: x.replace('1', 'X'), evealicechoice))
            evealicechoice= list(map(lambda x: x.replace('2', 'W'), evealicechoice))
            evealicechoice= list(map(lambda x: x.replace('3', 'Z'), evealicechoice))
            evealicechoice= list(map(lambda x: x.replace('4', 'V'), evealicechoice))
            evealiceresults= list(map(lambda x: x.replace('-1', '0'),evealiceresults))

            evebobchoice= list(map(lambda x: x.replace('1', 'X'), evebobchoice))
            evebobchoice= list(map(lambda x: x.replace('2', 'W'), evebobchoice))
            evebobchoice= list(map(lambda x: x.replace('3', 'Z'), evebobchoice))
            evebobchoice= list(map(lambda x: x.replace('4', 'V'), evebobchoice))
            evebobresults= list(map(lambda x: x.replace('-1', '0'),evebobresults))
        
        key_error=0

        if len(alice_keyl)!=0:
            checkKeyIndexl=random.sample(range(1, len(alice_keyl)), math.ceil(0.2*len(alice_keyl)))
            for j in checkKeyIndexl:
                if alice_keyl[j] != bob_keyl[j]:
                    key_error= key_error+1
            test_error_rate=key_error/len(checkKeyIndexl)
                
            keyLength=len(alice_keyl)
            abKeyMismatches = 0 # number of mismatching bits in the keys of Alice and Bob
            eaKeyMismatches = 0 # number of mismatching bits in the keys of Eve and Alice
            ebKeyMismatches = 0 # number of mismatching bits in the keys of Eve and Bob

            for j in range(len(alice_keyl)):
                if alice_keyl[j] != bob_keyl[j]:
                    abKeyMismatches += 1
                if eve_keyl[j][0]!= alice_keyl[j]:
                    eaKeyMismatches += 1
                if eve_keyl[j][1]!= bob_keyl[j]:
                    ebKeyMismatches +=1

                
            eaKnowledge = (keyLength - eaKeyMismatches)/keyLength # Eve's knowledge of Alice's key
            ebKnowledge = (keyLength - ebKeyMismatches)/keyLength

            error_rate=abKeyMismatches/len(alice_keyl)
                
            print('Alice keys', alice_keyl)
            print('Bob keys', bob_keyl)
            print('Eve keys',eve_keyl)
            print('Key length',len(alice_keyl))
            print('ab Mismatched keys', abKeyMismatches)
            print('ab check key error',key_error)
            print('Eve\'s knowledge of Alice\'s key: ' + str(round(eaKnowledge * 100, 2)) + ' %')
            print('Eve\'s knowledge of Bob\'s key: ' + str(round(ebKnowledge * 100, 2)) + ' %')  
            chsh_value=self.chsh_correlation(alice_meas,bob_meas,alice_choice,bob_choice,bob_entangled_key,alice_bob_map)
            print('Correlation value', chsh_value, round(chsh_value,2))
            

            res = {
                "sender_basis_list":alicechoice,
                "sender_meas_list":aliceresults,
                "eve_sender_basis_list":evealicechoice,
                "eve_sender_meas_list":evealiceresults,
                "receiver_basis_list":bobchoice,
                "receiver_meas_list":bobresults,
                "eve_receiver_basis_list":evebobchoice,
                "eve_receiver_meas_list":evebobresults,
                "sender_keys": alice_keyl,
                "receiver_keys": bob_keyl,
                "keyLength": len(alice_keyl),
                'keymismatch': abKeyMismatches,
                'Error_rate': error_rate,
                'Testkeylength':math.ceil(0.2*len(alice_keyl)),
                'Testkeymismatch':key_error,
                'Testerror_rate':test_error_rate,
                'correlation': str(round(chsh_value,3)),
                'Success':True
            }
            #print(res)
            return res
        else :

            res = {
                "sender_basis_list":alicechoice,
                "sender_meas_list":aliceresults,
                "eve_sender_basis_list":evealicechoice,
                "eve_sender_meas_list":evealiceresults,
                "receiver_basis_list":bobchoice,
                "receiver_meas_list":bobresults,
                "eve_receiver_basis_list":evebobchoice,
                "eve_receiver_meas_list":evebobresults,
                "sender_keys": alice_keyl,
                "receiver_keys": bob_keyl,
                "keyLength": len(alice_keyl),
                "Success":False   
            }
            return res
            


    def run(self,alice,bob,n, noise: Dict[str, List[float]] = {}):

        alice,bob,alice_bob_map,bob_entangled_key=self.set_state_psi_minus(alice,bob)
        alice_choice,alice_meas=self.alice_measurement(alice,deepcopy(noise))
        bob_choice,bob_meas=self.bob_measurement(bob,bob_entangled_key,deepcopy(noise))
        key_mismatch=0
        alice_keyl,bob_keyl=[],[]
        alice_results, bob_results ={},{}
        alicechoice , bobchoice = [],[]
        aliceresults ,bobresults = [],[]

        print('Alice Measurements',alice_meas)
        print('Alice choice',alice_choice)
        print('Bob Measuremenst', bob_meas)
        print('Bob choice',bob_choice)
        print(bob_entangled_key)
        print("e91 check",n)

        
        
        for bob_key in bob_entangled_key:

            
            
            bob_meas_i=list(bob_meas[bob_key].items())
            alice_key=alice_bob_map[bob_key]
            alice_meas_i=list(alice_meas[alice_key].items())

            if alice_meas_i[0][1]==0 and bob_meas_i[0][1] ==0:
                alice_results[alice_key]=-1 
                bob_results[bob_key]=-1
            elif alice_meas_i[0][1]==0 and bob_meas_i[0][1] ==1:
                alice_results[alice_key]=1 
                bob_results[bob_key]=-1
            elif alice_meas_i[0][1]==1 and bob_meas_i[0][1] ==0:
                alice_results[alice_key]=-1 
                bob_results[bob_key]=1
            elif alice_meas_i[0][1]==1 and bob_meas_i[0][1] ==1:
                alice_results[alice_key]=1  
                bob_results[bob_key]=1
            
            if (alice_choice[alice_key]==2 and bob_choice[bob_key]==2) or (alice_choice[alice_key]==3 and bob_choice[bob_key]==3):
                print('Base match',alice_meas[alice_key],bob_meas[bob_key])
                alice_keyl.append(str(alice_results[alice_key]))
                bob_keyl.append(str(-bob_results[bob_key]))
                
            alicechoice.append(str(alice_choice[alice_key]))
            aliceresults.append(str(alice_results[alice_key]))
            bobchoice.append(str(bob_choice[bob_key]))
            bobresults.append(str(bob_results[bob_key]))
            
            alicechoice= list(map(lambda x: x.replace('1', 'X'), alicechoice))
            alicechoice= list(map(lambda x: x.replace('2', 'W'), alicechoice))
            alicechoice= list(map(lambda x: x.replace('3', 'Z'), alicechoice))
            alicechoice= list(map(lambda x: x.replace('4', 'V'), alicechoice))
            aliceresults= list(map(lambda x: x.replace('-1', '0'), aliceresults))
            alice_keyl= list(map(lambda x: x.replace('-1', '0'), alice_keyl))
           
           
            bobchoice= list(map(lambda x: x.replace('1', 'X'), bobchoice))
            bobchoice= list(map(lambda x: x.replace('2', 'W'), bobchoice))
            bobchoice= list(map(lambda x: x.replace('3', 'Z'), bobchoice))
            bobchoice= list(map(lambda x: x.replace('4', 'V'), bobchoice))
            bobresults= list(map(lambda x: x.replace('-1', '0'), bobresults))
            bob_keyl= list(map(lambda x: x.replace('-1', '0'), bob_keyl))
           
        for j in range(len(alice_keyl)):
            if alice_keyl[j] != bob_keyl[j]:
                key_mismatch += 1
       
        print('Alice keys', alice_keyl)
        print('Bob keys', bob_keyl)
        print('Alice res', alice_results)
        print('Bob res', bob_results)
        print('Mismatched keys', key_mismatch)
        chsh_value=self.chsh_correlation(alice_meas,bob_meas,alice_choice,bob_choice,bob_entangled_key,alice_bob_map)
        print('Correlation value', chsh_value, round(chsh_value,3))
        error_rate=key_mismatch/len(alice_keyl)

        key_error=0
        if len(alice_keyl)!=0:
            checkKeyIndexl=random.sample(range(1, len(alice_keyl)), math.ceil(0.2*len(alice_keyl)))
            for j in checkKeyIndexl:
                if alice_keyl[j] != bob_keyl[j]:
                    key_error= key_error+1
            test_error_rate=key_error/len(checkKeyIndexl)

            res = {
                "sender_basis_list":alicechoice,
                "sender_meas_list":aliceresults,
                "receiver_basis_list":bobchoice,
                "receiver_meas_list":bobresults,
                "sender_keys": alice_keyl,
                "receiver_keys": bob_keyl,
                "keyLength": len(alice_keyl),
                'keymismatch': key_mismatch,
                'Error_rate': error_rate,
                'Testkeylength':math.ceil(0.2*len(alice_keyl)),
                'Testkeymismatch':key_error,
                'Testerror_rate':test_error_rate,
                'correlation': str(round(chsh_value,3)),
                'Success':True
            }    
            print(res)
            return res

        else:

            res = {
                "sender_basis_list":alicechoice,
                "sender_meas_list":aliceresults,
                "receiver_basis_list":bobchoice,
                "receiver_meas_list":bobresults,
                "sender_keys": alice_keyl,
                "receiver_keys": bob_keyl,
                "keyLength": len(alice_keyl),
                'keymismatch': key_mismatch,
                'Success':False
            }