from random import choices
from numpy import random

from qntsim.components.circuit import  QutipCircuit
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.topology.topology import Topology
import numpy as np
import time

class PingPong():
   
    """print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in bob.resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    """

    #I need to request Bell entanglemenets \psi_+ , \psi_-
    alice_key_list, bob_key_list = [], []
    state_key_list=[]
    alice_bob_keys_dict={}
    alice=None
    bob=None
    
    def request_entanglements(self,sender,receiver,n):
        sender.transport_manager.request(receiver.owner.name,5e12,n,20e12,0,.5,5e12)
        return sender,receiver

    def roles(self,alice,bob,n):
        sender=alice
        receiver=bob
        print('sender, receiver',sender.owner.name,receiver.owner.name)
        return self.request_entanglements(sender,receiver,200)
    
    def create_key_lists(self,alice,bob):
        self.alice=alice
        self.bob=bob
        for info in alice.resource_manager.memory_manager:
            alice_key=info.memory.qstate_key
            self.alice_key_list.append(alice_key)
        #print('Alice keys',self.alice_key_list)
        
        for info in bob.resource_manager.memory_manager:
            bob_key=info.memory.qstate_key
            self.bob_key_list.append(bob_key)
        #print('Bob keys',self.bob_key_list)

    def z_measurement(self,qm, key):
        circ=QutipCircuit(1)       #Z Basis measurement
        circ.measure(0)
        output=qm.run_circuit(circ,[key])
        return output

    def check_phi_plus(self,state):
        assert(len(state) == 4)
        if abs(state[0]*np.sqrt(2) - 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) - 1)  < 1e-5:
            return True
        elif abs(state[0]*np.sqrt(2) + 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) + 1)  < 1e-5:
            return True
        else : return False

    def create_psi_plus_entanglement(self):
        entangled_keys = []
        qm_alice=self.alice.timeline.quantum_manager

        for info in self.bob.resource_manager.memory_manager:

            key=info.memory.qstate_key
            state=qm_alice.get(key)

            #Filtering out unentangeled qubits
            if(len(state.keys) == 1) : continue

            #Filtering out phi_minus, created randomly, from phi_plus
            if(not self.check_phi_plus(state.state)):continue

            #print(state)
            self.state_key_list.append(state.keys)
            #print('state key list', self.state_key_list)
            self.alice_bob_keys_dict[state.keys[0]] = state.keys[1]
            self.alice_bob_keys_dict[state.keys[1]] = state.keys[0]
            self.to_psi_plus(qm_alice, state.keys)
            entangled_keys.append(key)

        return entangled_keys

    def to_psi_plus(self,qm, keys):

        circ=QutipCircuit(2)   
        #change to bell basis
        circ.cx(0,1)
        circ.h(0)   

        #Changing to psi_+
        circ.x(1)

        #back to computational basiss
        circ.h(0) 
        circ.cx(0,1)
        qm.run_circuit(circ, keys)
        #print('to psi plus',keys)
        #return is_psi_plus

    def protocol_c(self,entangled_keys):
        meas_results_alice, meas_results_bob = [] , [] 

        qm_alice=self.alice.timeline.quantum_manager
        for info in self.alice.resource_manager.memory_manager:

            alice_key=info.memory.qstate_key
            state=qm_alice.get(alice_key)
            
            if alice_key not in entangled_keys: continue
            meas_results_alice.append(self.z_measurement(qm_alice, alice_key))
            
        qm_bob=self.bob.timeline.quantum_manager
        for info in self.bob.resource_manager.memory_manager:

            bob_key=info.memory.qstate_key
            state=qm_bob.get(bob_key)
            
            if bob_key not in entangled_keys : continue
            meas_results_bob.append(self.z_measurement(qm_bob, bob_key))

        return meas_results_alice, meas_results_bob

    def encode_and_bell_measure(self,x_n, qm, keys):
        qc=QutipCircuit(2) 
        if(x_n == '1'):
            qc.z(1)
        qc.cx(0,1)
        qc.h(0)
        qc.measure(0)
        qc.measure(1)
        output=qm.run_circuit(qc,keys)
        print("message -> ", x_n)
        print(output)
        return output

    def protocol_m(self,x_n, current_keys):

        meas_results_bob = []
        qm_bob=self.bob.timeline.quantum_manager
        #print('protocl m',x_n, current_keys)
        for i,info in enumerate(self.bob.resource_manager.memory_manager):
            bob_key=info.memory.qstate_key
            if bob_key in current_keys:
                if bob_key in self.alice_bob_keys_dict.keys() or bob_key in self.alice_bob_keys_dict.values():
                    #print('new keylist',bob_key,self.alice_bob_keys_dict[bob_key])
                    meas_results_bob.append(self.encode_and_bell_measure(x_n, qm_bob, [bob_key,self.alice_bob_keys_dict[bob_key]]))
        return meas_results_bob


    def get_percentage_accurate(self,bell_results, x_n):
        count = 0
        assert x_n in ['0', '1']

        if x_n == '0':
            for result in bell_results:
                if list(result.values()) == [0, 1]:
                    count+=1

            return count/len(bell_results)


        elif x_n == '1':
            for result in bell_results:
                if list(result.values()) == [1, 1]:
                    count+=1

            return count/len(bell_results)


    def decode_bell(self,bell_results):
        list_vals = list(bell_results.values())
        if list_vals == [1,1]:
            return '1'
        elif list_vals == [0,1]:
            return '0'
        else : return '#'

    def one_bit_ping_pong(self,x_n, c, sequence_length, entangled_keys, round_num):
        #print("round_num ", round_num)
        memory_size = 10

        current_keys = entangled_keys[round_num*sequence_length : (round_num + 1)*sequence_length]

        draw = random.uniform(0, 1)
        while (draw < c):
            #print("Switching to protocol c ")
            meas_results_alice, meas_results_bob = self.protocol_c(current_keys)

            for i in range(len(meas_results_alice)):
                if not (list(meas_results_alice[i].values())[0] == 1 - list(meas_results_bob[i].values())[0]):
                    #print("Alice and Bob get same states -> Stop Protocol!")
                    return -1

            print("Protocol c passes through without trouble! No Eve detected yet")
            draw = random.uniform(0, 1)
            #print("meas_results_alice : ", meas_results_alice)
            #print("meas_results_bob : ", meas_results_bob)
            round_num = round_num + 1
            current_keys = entangled_keys[round_num*sequence_length : (round_num + 1)*sequence_length]

        if (draw > c) : 
            bell_results = self.protocol_m(x_n, current_keys)
            round_num = round_num + 1
            #print("HERE", bell_results)
            accuracy = self.get_percentage_accurate(bell_results, x_n)
            print(accuracy)
            if accuracy == 1 :
                return self.decode_bell(bell_results[0]), round_num

            else : 
                print("protocol m has some impurities; accuracy of transmission is ", accuracy)
                return -1


    def run_ping_pong(self,sequence_length,message):
        n = 0
        c = 0.2
        #sequence_length = 4
        
        bob_message = ""
        entangled_keys = self.create_psi_plus_entanglement()
        print("entangled_keys",entangled_keys)
        round_num = 0
        
        

        while(n < len(message)):
            n = n+1
            print(" whil n",n,len(message))

            result, round_num = self.one_bit_ping_pong(message[n-1], c, sequence_length, entangled_keys, round_num)

            if(result == -1): 
                print("Protocol doesn't run because of the aforesaid mistakes!")

            bob_message = bob_message + result

        print(f"Message transmitted : {message}")
        print(f"Message recieved : {bob_message}")

    #start = time.time()
    #run_ping_pong(alice,bob,sequence_length,message = "010110100")
    #end = time.time()
    #print("time took : ",  end - start)

    # In the request if the runtime is till the simulation, then memory will be sequentially allotted 
    # For quantum router , you can directly change memory size

    # Ask if we can divide task for different slots
    # Ask if we can increase memory for each node (currently it is 100)
    # Ask how to take care of phi plus vs phi minus generation
    # generalize to multiple bits


    # if (aliceMeasurementChoices[i] == 2 and bobMeasurementChoices[i] == 1) or (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 2):
    #         aliceKey.append(aliceResults[i]) # record the i-th result obtained by Alice as the bit of the secret key k

    ## Initilize new state as required, and you get key corresponding to these states
    # key = qm_alice.new([amp1, amp2])