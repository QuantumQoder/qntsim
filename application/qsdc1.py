from random import choices
import random
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.topology.topology import Topology
from qntsim.components.circuit import QutipCircuit
import numpy as np


class QSDC1():
   
    """print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in bob.resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    """

    #I need to request Bell entanglemenets \psi_+ , \psi_-
    
    def request_entanglements(self,sender,receiver,n):
        sender.transport_manager.request(receiver.owner.name,5e12,n,20e12,0,.5,5e12)
        return sender,receiver

    def roles(self,alice,bob,n):
        sender=alice
        receiver=bob
        print('sender, receiver',sender.owner.name,receiver.owner.name)
        return self.request_entanglements(sender,receiver,n)


    def check_phi_plus(self,state):
        assert(len(state) == 4)

        if abs(state[0]*np.sqrt(2) - 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) - 1)  < 1e-5:
            return True

        elif abs(state[0]*np.sqrt(2) + 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) + 1)  < 1e-5:
            return True

        else : return False


    def encode_QSDC(message):
        pass

    def create_entanglement(self,alice,bob):
        entangled_keys = []
        qm_alice=alice.timeline.quantum_manager
        qm_bob=bob.timeline.quantum_manager
        alice_bob_keys_dict = {}
        for info in alice.resource_manager.memory_manager:

            key=info.memory.qstate_key
            state=qm_alice.get(key)

            #Filtering out unentangeled qubits
            if(len(state.keys) == 1) : continue

            #Filtering out wrong states created
            if(not self.check_phi_plus(state.state)):continue
            entangled_keys.append(key)
        for info in bob.resource_manager.memory_manager:

            key=info.memory.qstate_key
            state=qm_bob.get(key)

            if(len(state.keys) == 1) : continue

            # I have to do both order because sometimes 
            # keys come in the form of [alice_key, bob_key]
            # and sometimes [bob_key, alice_key]
            # and I don't know why they happen either way
            if state.keys[0] in entangled_keys :
                alice_bob_keys_dict[state.keys[0]] = state.keys[1]

            if state.keys[1] in entangled_keys :
                alice_bob_keys_dict[state.keys[1]] = state.keys[0]


        return entangled_keys, alice_bob_keys_dict


    def single_message_QSDC_entngl(self,qm, message, keys):
        circ=QutipCircuit(2)   
        #change to bell basis
        circ.cx(0,1)
        circ.h(0)   


        #entangling choices!
        if message[0] == '1':circ.x(0)
        if message[1] == '1':circ.x(1)

        #back to computational basis
        circ.h(0) 
        circ.cx(0,1)

        qm.run_circuit(circ, keys)


    def generate_QSDC_entanglement(self,qm, message, entangled_keys, alice_bob_keys_dict):
        sequence_len = 1
        used_keys = []
        message_transmitted = ""
        for n in range(0, int(len(message)/2)) : 
            keys = entangled_keys[n:n+sequence_len]
            key_pair = [[key, alice_bob_keys_dict[key]] for key in keys]
            for pairs in key_pair:
                self.single_message_QSDC_entngl(qm, message[2*n:2*n+2], pairs)

            for key in keys:
                used_keys.append(key)
        return used_keys
            

    def z_measurement(self,qm, key):
        circ=QutipCircuit(1)       #Z Basis measurement
        circ.measure(0)
        output=qm.run_circuit(circ,[key])

        return output

    def eavesdrop_check(self,alice,bob,entangled_keys, message,alice_bob_keys_dict):
        qm_alice = alice.timeline.quantum_manager
        qm_bob = bob.timeline.quantum_manager
        alice_meas, bob_meas = [], []
        choose_pos = random.sample(range(len(entangled_keys)), int(len(entangled_keys)/4))
        choose_keys = []
        print("message thrown out because we measure it for eavesdrop check : ", )
        thrown_message = []
        for pos in choose_pos:
            alice_meas.append(self.z_measurement(qm_alice, entangled_keys[pos]))
            bob_meas.append(self.z_measurement(qm_bob,alice_bob_keys_dict[entangled_keys[pos]]))
            print(message[2*pos:2*pos+2])
            thrown_message.append(message[2*pos:2*pos+2])
            choose_keys.append(entangled_keys[pos])

        for i in range(len(alice_meas)):
            a_val = list(alice_meas[i].values())[0]
            b_val = list(bob_meas[i].values())[0]

            if thrown_message[i] == "00" or thrown_message[i] == "10":
                assert a_val == b_val
            else : assert a_val == 1 - b_val

        print("eavesdrop check passed!")
        print(alice_meas, bob_meas)
        return choose_keys

    def bell_measure(self,qm, keys):
        qc=QutipCircuit(2) 
        qc.cx(0,1)
        qc.h(0)
        qc.measure(0)
        qc.measure(1)
        output=qm.run_circuit(qc,keys)
        #print(output)
        #print(list(output.values()))
        return output

    def run(self,alice,bob,sequence_length,message):
        #message = "110011001001010101010100"
        assert len(message)%2 == 0
        entangled_keys,alice_bob_keys_dict  = self.create_entanglement(alice,bob)
        qm_alice = alice.timeline.quantum_manager

        protocol_keys = self.generate_QSDC_entanglement(qm_alice, message, entangled_keys,alice_bob_keys_dict )
        message_received = ""
        c = 0
        sequence_len = 1
        measured_keys = self.eavesdrop_check(alice,bob,protocol_keys, message,alice_bob_keys_dict )

        for keys in protocol_keys:
            if keys in measured_keys:continue
            #if (c == len(message)):break

            output = self.bell_measure(qm_alice, [keys, alice_bob_keys_dict[keys]])
            message_received += str(output[keys]) + str(output[alice_bob_keys_dict[keys]])
            c+=2

        print(f"key transmitted : {message}")
        print(f"key shared received : {message_received}")

# In the request if the runtime is till the simulation, then memory will be sequentially allotted 
# For quantum router , you can directly change memory size

# Ask if we can divide task for different slots
# Ask if we can increase memory for each node (currently it is 100)
# Ask how to take care of phi plus vs phi minus generation
# generalize to multiple bits


# if (aliceMeasurementChoices[i] == 2 and bobMeasurementChoices[i] == 1) or (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 2):
#         aliceKey.append(aliceResults[i]) # record the i-th result obtained by Alice as the bit of the secret key k



##############################################################################################################

# sender and receiver (input type :string)-nodes in network 
# backend (input type :string) Qutip (Since entanglements are filtered out based on EPR state)
# Todo Support on Qiskit
# message length should be even
# sequence length should be less than 5
"""
def run(path,sender,receiver,sequence_length,message):

    from qntsim.kernel.timeline import Timeline 
    Timeline.DLCZ=False
    Timeline.bk=True
    from qntsim.topology.topology import Topology
    
    tl = Timeline(20e12,"Qutip")
    network_topo = Topology("network_topo", tl)
    network_topo.load_config(path)
    if (len(message)%2==0):
        
        n=int(sequence_length*len(message))
        alice=network_topo.nodes[sender]
        bob = network_topo.nodes[receiver]
        qsdc1=QSDC1()
        alice,bob=qsdc1.roles(alice,bob,n)
        tl.init()
        tl.run()  
        qsdc1.run_first_QSDC(alice,bob,sequence_length,message)
"""