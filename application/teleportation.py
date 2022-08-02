
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True

from tabulate import tabulate
from qntsim.components.circuit import Circuit,QutipCircuit
from qiskit import *
from qutip.qip.circuit import QubitCircuit, Gate
from qutip.qip.operations import gate_sequence_product
from qiskit.extensions import Initialize
#from qiskit.ignis.verification import marginal_counts
from qiskit.quantum_info import random_statevector
import math






class Teleportation():

    def request_entanglements(self,sender,receiver):
        sender.transport_manager.request(receiver.owner.name,5e12,1,20e12,0,.5,5e12)
        return sender,receiver

    def roles(self,alice,bob):
        sender=alice
        receiver=bob
        print('sender, receiver',sender.owner.name,receiver.owner.name)
        return self.request_entanglements(sender,receiver)



    def alice_keys(self,alice):
        qm_alice = alice.timeline.quantum_manager
        for mem_info in alice.resource_manager.memory_manager:
            key=mem_info.memory.qstate_key
            state= qm_alice.get(key)
            print("alice entangled state",state.state)
            return qm_alice,key,state

    def bob_keys(self,bob):
        qm_bob = bob.timeline.quantum_manager
        for mem_info in bob.resource_manager.memory_manager:
            key=mem_info.memory.qstate_key
            state= qm_bob.get(key)
            #print("bob keys",key,state)
            return qm_bob,key,state
        

    def alice_measurement(self,A_0,A_1,alice):

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

        circ=QutipCircuit(2)
        circ.cx(0,1)
        circ.h(0)
        circ.measure(0)
        circ.measure(1)
        output=qm_alice.run_circuit(circ,[key_0,key])
        crz=output.get(key_0)
        crx=output.get(key)
        # circ.measure(1)
        #qm_alice,key,alice_state=alice_keys()
        #alice_state.append()
        #print('output',key_0,key,output,crz,crx)
        return crz,crx,case
        

    def bob_gates(self,crz,crx,case,bob):

        qm_bob,key,state=self.bob_keys(bob)
        if case=="psi+":
            circ=QutipCircuit(1)
            if crx==1:
                circ.x(0)
            if crz==1:
                circ.z(0)
                #circ.measure(0)
            
        if case=="-psi+":
            circ=QutipCircuit(1)
            if crz==0 and crx==0:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
                #circ.measure(0)
            elif crz==0 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)   
            elif crz==1 and crx==0:
                circ.x(0)
                circ.z(0)
                circ.x(0)
            elif crz==1 and crx==1:
                circ.z(0)
                circ.x(0)

        if case=="psi-":
            circ=QutipCircuit(1)
            if crz==0 and crx==0:
                circ.z(0)
                #circ.measure(0)
            elif crz==0 and crx==1:  
                circ.z(0)
                circ.x(0)
            elif crz==1 and crx==0:
                pass
            elif crz==1 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)

        if case=="-psi-":
            circ=QutipCircuit(1)
            if crz==0 and crx==0:
                circ.x(0)
                circ.z(0)
                circ.x(0)
                #circ.measure(0)
            elif crz==0 and crx==1:
                circ.x(0)
                circ.z(0)
            elif crz==1 and crx==0:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
            elif crz==1 and crx==1:
                circ.x(0)

        if case=="phi+":
            circ=QutipCircuit(1)
            if crz==0 and crx==0:
                circ.x(0)    
            elif crz==0 and crx==1:
                pass
            elif crz==1 and crx==0:
                circ.x(0)
                circ.z(0)
            elif crz==1 and crx==1:
                circ.z(0)
        
        if case=="-phi+":
            circ=QutipCircuit(1)
            if crz==0 and crx==0:

                circ.z(0)
                circ.x(0)
                circ.z(0)
                
            elif crz==0 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
            elif crz==1 and crx==0:
                circ.z(0)
                circ.x(0)
                
            elif crz==1 and crx==1:
                circ.x(0)
                circ.z(0)
                circ.x(0)
                
        if case=="-phi-":
            circ=QutipCircuit(1)
            if crz==0 and crx==0:
                print('crz 1')
                circ.x(0)
                circ.z(0)
                    
            elif crz==0 and crx==1:
                print('crz 1')
                circ.x(0)
                circ.z(0)
                circ.x(0)
            elif crz==1 and crx==0:
                circ.x(0)
                
            elif crz==1 and crx==1:
                circ.z(0)
                circ.x(0)
                circ.z(0)
                circ.x(0)
        
        if case=="phi-":
            circ=QutipCircuit(1)
            if crz==0 and crx==0:
                print('crz 1') 
                circ.z(0)
                circ.x(0)
                
                #circ.measure(0)
            elif crz==0 and crx==1:
                print('crz 1')
                circ.z(0)
            elif crz==1 and crx==0:
                circ.z(0)
                circ.x(0)
                circ.z(0)
            elif crz==1 and crx==1:
                pass
        #circ.measure(0)
        
        output=qm_bob.run_circuit(circ,[key])
        print("Bob's state before corrective measures",state.state)
        print('bob final state after corrective measures',qm_bob.get(key).state)


    def runtel(self,alice,bob,A_0,A_1):
        crz,crx,case=self.alice_measurement(A_0,A_1,alice)
        print("crz",crz)
        print("crx",crx)
        self.bob_gates(crz,crx,case,bob)