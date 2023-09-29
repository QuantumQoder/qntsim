import logging
import random
from copy import deepcopy
from random import choices
from typing import Dict, List

import numpy as np
from qntsim.communication.noise import Noise
from qntsim.kernel.circuit import QutipCircuit
from qntsim.utils import log

# logger = logging.getLogger("main_logger.application_layer." + "qsdc1")

class QSDC1():
   
    """print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in bob.resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    """

    #I need to request Bell entanglemenets \psi_+ , \psi_-
    
    def request_entanglements(self,sender,receiver,n):
        print("sender,receiver,n",sender.name,receiver.name,n)
        log.logger.info("requesting entanglement between: "+ sender.name+ " "+receiver.name)
        sender.transport_manager.request(receiver.owner.name,5e12,n,20e12,0,.5,5e12)
        source_node_list=[sender.name]
        print("sender,receiver,source_node_list",sender,receiver,source_node_list)
        return sender,receiver,source_node_list

    def roles(self,alice,bob,n):
        sender=alice
        receiver=bob
        print('sender, receiver',sender.owner.name,receiver.owner.name)
        log.logger.info('sender, receiver are '+sender.owner.name+" "+receiver.owner.name)     
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
            # print('llll')
            key=info.memory.qstate_key
            state=qm_alice.get(key)

            #Filtering out unentangeled qubits
            if(len(state.keys) == 1) : continue

            #Filtering out wrong states created
            if(not self.check_phi_plus(state.state)):continue
            entangled_keys.append(key)
        print('entangled keys', entangled_keys)
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

        print("entangled_keys, alice_bob_keys_dict",entangled_keys, alice_bob_keys_dict)
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
        # Convert message here
        for n in range(0, int(len(message)/2)) : 
            keys = entangled_keys[n:n+sequence_len]
            key_pair = [[key, alice_bob_keys_dict[key]] for key in keys]
            for pairs in key_pair:
                self.single_message_QSDC_entngl(qm, message[2*n:2*n+2], pairs)

            for key in keys:
                used_keys.append(key)
        return used_keys
            
    def string_to_binary(self,messages):
        print("Converting to binary...")
        binary = [''.join('0'*(8-len(bin(ord(char))[2:]))+bin(ord(char))[2:] for char in message) for message in messages]
        print("Conversion completed")
    
        return binary

    def binary_to_string(self,message):

        string = ''.join(chr(int(message[i*8:-~i*8], 2)) for i in range(len(message)//8))

        return string

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
        removed_bits=[]
        print("message thrown out because we measure it for eavesdrop check : ", )
        #logger.info("message thrown out because we measure it for eavesdrop check : " )
        thrown_message = []
        for pos in choose_pos:
            alice_meas.append(self.z_measurement(qm_alice, entangled_keys[pos]))
            bob_meas.append(self.z_measurement(qm_bob,alice_bob_keys_dict[entangled_keys[pos]]))
            print(message[2*pos:2*pos+2])
            removed_bits.append(message[2*pos:2*pos+2])
            thrown_message.append(message[2*pos:2*pos+2])
            choose_keys.append(entangled_keys[pos])
        print(entangled_keys, "fuck")
        self.eavesdrop = None

        for i in range(len(alice_meas)):
            a_val = list(alice_meas[i].values())[0]
            b_val = list(bob_meas[i].values())[0]

            if thrown_message[i] == "00" or thrown_message[i] == "10":
                if a_val ==b_val:
                    self.eavesdrop=False
                else:
                    self.eavesdrop=True
                #assert a_val == b_val
            else : 
                if a_val == 1-b_val:
                    self.eavesdrop=False
                else:
                    self.eavesdrop=True
                #assert a_val == 1 - b_val

        print("eavesdrop check passed!", self.eavesdrop)
        log.logger.info("eavesdrop check passed!")
        print(alice_meas, bob_meas)
        return choose_keys,removed_bits

    def bell_measure(self,qm, keys, noise: Dict[str, List[float]] = {}):
        qc=QutipCircuit(2)
        qc.cx(0,1)
        qc.h(0)
        readout = noise.pop("readout", [0, 0])
        Noise.implement(noise, circuit = qc, keys = keys, quantum_manager = qm)
        qc.measure(0)
        qc.measure(1)
        output=qm.run_circuit(qc,keys)
        Noise.readout(readout, reasult = output)
        #print(output)
        #print(list(output.values()))
        return output

    def run(self,alice,bob,sequence_length,message, noise: Dict[str, List[float]] = {}):
        #message = "110011001001010101010100"
        #  convert message before run is called
        # message = string_to_binary(message)
        assert len(message)%2 == 0
        entangled_keys,alice_bob_keys_dict  = self.create_entanglement(alice,bob)
        print('entangled_keys,alice_bob_keys_dict',alice, bob,entangled_keys,alice_bob_keys_dict)
        qm_alice = alice.timeline.quantum_manager

        protocol_keys = self.generate_QSDC_entanglement(qm_alice, message, entangled_keys,alice_bob_keys_dict )
        message_received = ""
        c = 0
        sequence_len = 8
        measured_keys,removed_bits = self.eavesdrop_check(alice,bob,protocol_keys, message,alice_bob_keys_dict )

        for keys in protocol_keys:
            if keys in measured_keys:
                message_received += "__"
                continue
            #if (c == len(message)):break

            output = self.bell_measure(qm_alice, [keys, alice_bob_keys_dict[keys]], deepcopy(noise))
            message_received += str(output[keys]) + str(output[alice_bob_keys_dict[keys]])
            c+=2
        final_key = message_received.replace("__", "")
        log.logger.info("obtained final key")
        print("message thrown out because we measure it for eavesdrop check : ",removed_bits)
        print(f"key transmitted : {message}")
        print(f"key shared received : {message_received}")
        print(f"Final key : {final_key}")
        

        ###"message thrown out because we measure it for eavesdrop check : ",removed_bits
        ###display_msg : "message thrown out because we measure it for eavesdrop check : "
        #  covert key abck to string
        res = {
            "eavesdrop":self.eavesdrop,
            "display_msg":removed_bits,
            "key_transmitted": message,
            "key_shared_received": message_received,
            "final_key" : final_key
        }
        print(res)
        return res

if __name__ == "__main__":
    import json

    from qntsim.layers.application_layer.communication.network import Network

    topology = json.load(open("topology.json", 'r'))
    network = Network(topology=topology,messages={('node1','node2'):'hello'})
    nodes = network.nodes
    alice,bob = nodes[0],nodes[1]
    aa = QSDC1()
    aa.run(alice,bob, None,"11001000",noise={"amp_dmp":[0.9]})