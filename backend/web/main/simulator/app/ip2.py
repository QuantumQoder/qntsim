import os
import sys, logging
from functools import partial
from numpy.random import randint
from random import sample
from typing import Any, Dict, List, Tuple
from qntsim.library import Network, insert_check_bits, insert_decoy_photons, bell_type_state_analyzer, Protocol, ErrorAnalyzer
from qntsim.library.attack import Attack, ATTACK_TYPE
from qntsim.components.circuit import QutipCircuit

logging.basicConfig(filename='ip2.log', filemode='w', level=logging.INFO, format='%(pathname)s %(threadName)s %(module)s %(funcName)s %(message)s')

class Party:
    input_messages:Dict[Tuple, str] = None
    # input_messages:Dict[int, str] = None
    id:str = None
    received_msgs:Dict[int, str] = None

class Alice(Party):
    chk_bts_insrt_lctns:List[int] = None
    num_check_bits:int = None
    
    @classmethod
    def input_check_bits(cls, network:Network, returns:Any):
        """Alice inserts random check bits into her message for estimating the integrity of the received message
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        """
        modified_message = insert_check_bits(messages=[cls.input_messages.get(key) for key in cls.input_messages], num_check_bits=cls.num_check_bits)
        cls.chk_bts_insrt_lctns = list(modified_message)[0]
        cls.input_messages[1] = list(modified_message.values())[0]
        logging.info(f'in message by {cls.__name__}!')
    
    @classmethod
    def encode(cls, network:Network, returns:Any):
        """Alice encodes her message into the memory nodes associated to her. In addition, she also performs {I, 𝑍} operations on the Id keys of Bob.
            She also applied cover operations on the decoy photons send by Bob.
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        Returns:
            cls.d_a: List of memory keys of decoy photons
        """
        cls.i_a, cls.d_a = returns[1], returns[2]
        cls.s_a = [ele for ele in returns[0] if ele not in cls.i_a]
        cls.m_a = sample(cls.s_a, k=len(cls.s_a)-len(cls.id)//2)
        cls.c_a = [ele for ele in cls.s_a if ele not in cls.m_a]
        ch0, ch1, i0, i1 = iter(cls.input_messages.get(1)[::2]), iter(cls.input_messages.get(1)[1::2]), iter(cls.id[::2]), iter(cls.id[1::2])
        for s in cls.s_a:
            qtc = QutipCircuit(1)
            if int(next(ch1) if s in cls.m_a else next(i1)): qtc.x(0)
            if int(next(ch0) if s in cls.m_a else next(i0)): qtc.z(0)
            network.manager.run_circuit(qtc, [s])
        cls.basis = randint(2, size=len(cls.i_a))
        for i, base in zip(cls.i_a, cls.basis):
            qtc = QutipCircuit(1)
            if base: qtc.z(0)
            network.manager.run_circuit(qtc, [i])
        cls.cov_ops = randint(4, size=len(cls.d_a))
        for d, ops in zip(cls.d_a, cls.cov_ops):
            q, r = divmod(ops, 2)
            qtc = QutipCircuit(1)
            if r:
                qtc.x(0)
                qtc.z(0)
            if q: qtc.h(0)
            network.manager.run_circuit(qtc, [d])
        logging.info(f'message by {cls.__name__}')
        
        return cls.d_a
    
    @classmethod
    def insert_new_decoy_photons(cls, network:Network, returns:Any, num_decoy_photons:int):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            num_decoy_photons (int): Number of decoy photons to be inserted in the sequence of keys
        Returns:
            cls.d_a: List of memory keys of decoy photons
        """
        cls.d_a, cls.photons_a = insert_decoy_photons(network=network, node_index=0, num_decoy_photons=num_decoy_photons)
        cls.q_a = cls.s_a+cls.i_a+cls.d_a
        logging.info(f'in key-sequence by {cls.__name__}')
        
        return cls.d_a

class Bob(Party):
    @classmethod
    def setup(cls, network:Network, returns:Any, num_decoy_photons:int):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        Returns:
            seq_a (List): _description_
            i_a (List):
            cls.d_a: 
        """
        seq_a, seq_b = list(zip(*[sorted(network.manager.get(key=info.memory.qstate_key).keys) for info in network.nodes[1].resource_manager.memory_manager if info.state=='ENTANGLED']))
        cls.i_b = list(seq_b[-len(cls.id)//2:])
        cls.s_b = [ele for ele in seq_b if ele not in cls.i_b]
        for k, i1, i2 in zip(cls.i_b, cls.id[::2], cls.id[1::2]):
            qtc = QutipCircuit(1)
            if int(i2): qtc.x(0)
            if int(i1): qtc.z(0)
            network.manager.run_circuit(qtc, [k])
        cls.d_a, cls.photons_a = insert_decoy_photons(network=network, node_index=1, num_decoy_photons=num_decoy_photons)
        cls.d_b, cls.photons_b = insert_decoy_photons(network=network, node_index=1, num_decoy_photons=num_decoy_photons)
        logging.info(f'keys for epr pairs and decoy photons by {cls.__name__}')
        cls.d_b = sorted(list(set(cls.d_b)-set(cls.d_a)))
        
        return seq_a, list(seq_a[-len(cls.id)//2:]), cls.d_a
    
    def decode(network:Network, returns:Any):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        Returns:
            _type_: _description_
        """
        outputs = ''.join(str(output) for outputs in returns for output in outputs.values())
        
        return outputs
    
    @classmethod
    def check_integrity(cls, network:Network, returns:Any, cls1, threshold:float):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            cls1 (_type_): _description_
            threshold (float): _description_
        """
        cls.received_msgs = ''.join(char for i, char in enumerate(returns) if i not in cls1.chk_bts_insrt_lctns)
        network._strings = cls.received_msgs
        err = [int(returns[pos])^int(cls1.input_messages.get(1)[pos]) for pos in cls1.chk_bts_insrt_lctns]
        if (err_prct:=sum(err)/len(err))>threshold:
            logging.info('failed, err=', 1-err_prct)
            return
        logging.info(f'passed, messages recived: {cls.received_msgs}')
    
class UTP:
    @classmethod
    def check_channel_security(cls, network:Network, returns:Any, cls1, cls2, threshold:float):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            cls1 (_type_): _description_
            cls2 (_type_): _description_
            threshold (float): _description_
        """
        print(f'channel_security between {cls1.__name__} and {cls2.__name__}')
        keys = returns if cls1==Alice or cls2==Alice else cls2.d_b
        basis = cls2.photons_a if cls1!=cls or cls2==Alice else cls2.photons_b
        cov_ops = cls1.cov_ops if cls1!=cls else [0 for _ in range(len(basis))]
        err = []
        for key, base, ops in zip(keys, basis, cov_ops):
            b_q, b_r = divmod(base, 2)
            op_q, op_r = divmod(ops, 2)
            qtc = QutipCircuit(1)
            if b_q^op_q: qtc.h(0)
            qtc.measure(0)
            output = network.manager.run_circuit(qtc, [key])
            err.append(output.get(key)^b_r^op_r)
        mean_ = sum(err)/len(err)
        if mean_>=threshold:
            logging.info(f'failed between {cls1.__name__} and {cls2.__name__}, err={mean_}')
            sys.exit(f'failed between {cls1.__name__} and {cls2.__name__}, err={mean_}')
            # return -1, f'failed between {cls1.__name__} and {cls2.__name__}, err={mean(err)}'
            # os._exit(f'Security of the channel between {cls1.__name__} and {cls2.__name__} is compromised.')
        logging.info(f'passed between {cls1.__name__} and {cls2.__name__}')
        
        return returns
    
    def authenticate(network:Network, returns:Any, cls1, cls2, circuit:QutipCircuit):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            cls1 (_type_): _description_
            cls2 (_type_): _description_
            circuit (QutipCircuit): _description_
        Returns:
            _type_: _description_
        """
        outputs = []
        for ia, ib in zip(cls1.i_a, cls2.i_b):
            state = network.manager.get(ia)
            outputs.extend(list(network.manager.run_circuit(circuit=circuit, keys=state.keys).values()))
        outputs = ''.join(str(output) if i%2 else str(output^cls1.basis[i//2]) for i, output in enumerate(outputs))
        if outputs!=cls2.id:
            sys.exit(f'{cls2.__name__} is not authenticated')
            # return -1, f'{cls2.__name__} is not authenticated'
            # os._exit(f'{cls2.__name__} is not authenticated')
        else: logging.info(f'{cls2.__name__}, passed!')
        outputs = []
        for c in cls1.c_a:
            state = network.manager.get(c)
            outputs.extend(list(network.manager.run_circuit(circuit=circuit, keys=state.keys).values()))
        outputs = ''.join(str(o) for o in outputs)
        if outputs!=cls1.id:
            sys.exit(f'{cls1.__name__} is not authenticated')
            # os._exit(f'{cls1.__name__} is not authenticated')
        else: logging.info(f'{cls1.__name__}, passed!')
        
        return outputs
    
    def measure(network:Network, returns:Any, circuit:QutipCircuit, cls):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            circuit (QutipCircuit): _description_
        Returns:
            _type_: _description_
        """
        outputs = []
        for m in cls.s_a:
            if m in cls.m_a:
                state = network.manager.get(m)
                outputs.append(network.manager.run_circuit(circuit=circuit, keys=state.keys))
        
        return outputs

def pass_(network:Network, returns:Any):
    return returns

def ip2_run(topology, alice_attrs, bob_id, num_decoy_photons, threshold, attack):
    Alice.input_messages = alice_attrs.get('message')
    Alice.id = alice_attrs.get('id')
    Alice.num_check_bits = alice_attrs.get('check_bits')
    Bob.id = bob_id
    threshold = threshold
    attack, chnnl = attack
    chnnl = [1 if i==chnnl else 0 for i in range(3)]
    Network._flow = [partial(Alice.input_check_bits),
                     partial(Bob.setup, num_decoy_photons=num_decoy_photons),
                     partial(Alice.encode),
                     partial(Attack.implement, attack=ATTACK_TYPE[attack].value) if attack and chnnl[0] else partial(pass_),
                     partial(UTP.check_channel_security, cls1=Alice, cls2=Bob, threshold=threshold),
                     partial(Alice.insert_new_decoy_photons, num_decoy_photons=num_decoy_photons),
                    #  partial(Attack.implement, attack=ATTACK_TYPE[attack].value) if attack and chnnl[1] else partial(pass_),
                     partial(UTP.check_channel_security, cls1=UTP, cls2=Alice, threshold=threshold),
                     partial(Attack.implement, attack=ATTACK_TYPE[attack].value) if attack and chnnl[2] else partial(pass_),
                     partial(UTP.check_channel_security, cls1=UTP, cls2=Bob, threshold=threshold),
                     partial(UTP.authenticate, cls1=Alice, cls2=Bob, circuit=bell_type_state_analyzer(2)),
                     partial(UTP.measure, circuit=bell_type_state_analyzer(2), cls=Alice),
                     partial(Bob.decode),
                     partial(Bob.check_integrity, cls1=Alice, threshold=threshold)]
    network = Network(topology=topology, messages=Alice.input_messages, name='ip2', size=lambda x:(x+Alice.num_check_bits+len(Alice.id)+len(Bob.id))//2, label='00')
    network()
    return_tuple = ErrorAnalyzer._analyse(network=network)
    print(f'Average error in network:{return_tuple[2]}')
    print(f'Standard deviation in error in network:{return_tuple[3]}')
    print(f'Information leaked to the attacker:{return_tuple[4]}')
    print(f'Fidelity of the message:{return_tuple[5]}')
    # Network.execute(networks=[network])
    # print('Received messages:', Bob.received_msgs)
    
    return Bob.received_msgs, return_tuple[2:]