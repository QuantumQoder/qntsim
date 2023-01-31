from random import sample
from statistics import mean
import numpy as np
from numpy.random import randint
from typing import Any, Dict, List

from qntsim.components.circuit import QutipCircuit
from qntsim.topology.node import Node
from qntsim.library.network import Network



def insert_seq(lst:List, seq:List):
    insert_locations = sample(range(len(lst)+len(seq)), len(seq))
    inserts = dict(zip(insert_locations, seq))
    input = iter(lst)
    return [inserts[i] if i in inserts else next(input) for i in range(len(lst)+len(seq))]

def insert_check_bits(messages:Dict, num_check_bits:int):
    msg_list = list(messages.get(2))
    messages[2] = ''.join(str(ele) for ele in insert_seq(lst=msg_list, seq=randint(2, size=num_check_bits))) 
    return messages

def bob_abc(network:Network, num_decoy:int ,ids:Dict[int,str]):
    def insert_decoy_photons(node:Node, keys:List[int]):
        keys = insert_seq(lst=keys, seq=[max(keys)+i for i in range(1, num_decoy+1)])
        basis = randint(4, size=num_decoy)
        inputs = iter(basis)
        for info in node.resource_manager.memory_manager:
            key = info.memory.qstate_key
            if key in keys and info.state=='RAW':
                qtc = QutipCircuit(1)
                q, r = divmod(next(inputs), 2)
                if r: qtc.x(0)
                if q: qtc.h(0)
                network.manager.run_circuit(qtc, [key])
                info.state = 'OCCUPIED'
            # state = network.manager.get(key)
            # print(info.state, state.keys, state.state)
        
        return keys, basis
    
    node = network.nodes[0]
    keys_sb_ib = [info.memory.qstate_key for info in node.resource_manager.memory_manager if info.state=='ENTANGLED']
    id_locations = sample(keys_sb_ib, len(ids[1])//2)
    for key, char0, char1 in zip(id_locations, ids[1][::2], ids[1][1::2]):
        qtc = QutipCircuit(1)
        if int(char1): qtc.x(0)
        if int(char0): qtc.z(0)
        network.manager.run_circuit(qtc, [key])
    # keys = insert_decoy_photons(keys=keys)
    # print(keys)
    # node = network.nodes[1]
    # keys = []
    # keys = insert_decoy_photons(keys=keys)
    # print(keys)
    
    return insert_decoy_photons(node=node, keys=keys_sb_ib), id_locations, insert_decoy_photons(node=network.nodes[1], keys=[info.memory.qstate_key for info in network.nodes[1].resource_manager.memory_manager if info.state=='ENTANGLED'])

def alice_abcd(network:Network, ib_pos:List[int], sequence_q:List[int],ids:Dict[int,str]):
    node = network.nodes[1]
    ia_keys = [k for idb in ib_pos for k in network.manager.get(idb).keys if k!=idb]
    id_a = ids[2]
    sa_keys = [sa_key for info in node.resource_manager.memory_manager if info.state=='ENTANGLED' and ((sa_key:=info.memory.qstate_key) not in ia_keys)]
    m_keys = sample(sa_keys, len(network.bin_msgs[0])//2)
    # print(e_keys, m_keys)
    c_keys = list(set(sa_keys)-set(m_keys))
    # print(len(sa_keys), len(s))
    id_a = iter(id_a)
    for sa_key, bit0, bit1 in zip(sa_keys, network.bin_msgs[0][::2], network.bin_msgs[0][1::2]):
        qtc = QutipCircuit(1)
        if sa_key in m_keys:
            if int(bit1): qtc.x(0)
            if int(bit0): qtc.z(0)
        elif sa_key in c_keys:
            i_a = next(id_a)
            # print(i_a)
            if int(i_a): qtc.z(0)
            i_a = next(id_a)
            # print(i_a)
            if int(i_a): qtc.x(0)
        network.manager.run_circuit(qtc, [sa_key])
    # print(ia_keys)
    
    z_basis = randint(2, size=len(ia_keys))
    for key, z_base in zip(ia_keys, z_basis):
        qtc = QutipCircuit(1)
        if z_base: qtc.z(0)
        network.manager.run_circuit(qtc, [key])
    sa_keys = insert_seq(lst=sa_keys, seq=ia_keys)
    # print(sa_keys)
    decoy_keys = list(set(sequence_q)-set(sa_keys))
    ops = randint(4, size=len(decoy_keys))
    # print(ops)
    for key, op in zip(decoy_keys, ops):
        # state = network.manager.get(key)
        # print(state.keys, state.state)
        qtc = QutipCircuit(1)
        q, r = divmod(op, 2)
        if q: qtc.h(0)
        if r:
            qtc.x(0)
            qtc.z(0)
        network.manager.run_circuit(qtc, [key])
        # state = network.manager.get(key)
        # print(state.keys, state.state)
    
    return decoy_keys, ops, z_basis, c_keys, m_keys

def utp_5_7(network:Network, decoy_keys:List, basis:List, ops:List, threshold:float=0.5):
    err = []
    for decoy_key, base, op in zip(decoy_keys, basis, ops):
        qtc = QutipCircuit(1)
        if (base//2)^(op//2): qtc.h(0)
        if (base%2)^(op%2): qtc.x(0)
        qtc.measure(0)
        err.append(network.manager.run_circuit(qtc, [decoy_key]).get(decoy_key))
    #     state = network.manager.get(decoy_key)
    #     print(state.keys, state.state)
    # print(decoy_keys, basis, ops, err)
    
    return mean(err)<threshold

def alice_6(network:Network, decoy_keys:List):
    basis = randint(4, size=len(decoy_keys))
    for decoy_key, base in zip(decoy_keys, basis):
        state = network.manager.get(decoy_key)
        state.state = np.array([complex(1), 0.0])
        qtc = QutipCircuit(1)
        q, r = divmod(base, 2)
        if r: qtc.x(0)
        if q: qtc.h(0)
        network.manager.run_circuit(qtc, [decoy_key])
    
    return decoy_keys, basis

def authenticate(network:Network, ib_pos:List, circuit:QutipCircuit, z_basis:Any):
    outputs = []
    for ib in ib_pos:
        state = network.manager.get(ib)
        outputs.extend(list(network.manager.run_circuit(circuit=circuit, keys=state.keys).values()))
    outputs = ''.join(str(output) if i%2 else str(output^z_basis[i//2]) for i, output in enumerate(outputs))
    # print(outputs, z_basis)  
     
def bsm_circuit():
    qtc = QutipCircuit(2)
    qtc.cx(0, 1)
    qtc.h(0)
    qtc.measure(0)
    qtc.measure(1)
    
    return qtc
# print(c_keys)

def auth_9b(network:Network, c_keys:List, circuit:QutipCircuit):
    outputs = []
    for c_key in c_keys:
        state = network.manager.get(c_key)
        outputs.extend(list(network.manager.run_circuit(circuit=circuit, keys=state.keys).values()))
    outputs = ''.join(str(output) for output in outputs)
    # print(outputs)

def decode(network:Network, m_keys:List, circuit:QutipCircuit ,input_messages:Dict[int,str]):
    outputs = []
    for m_key in m_keys:
        state = network.manager.get(m_key)
        outputs.extend(list(network.manager.run_circuit(circuit, state.keys).values()))
    # print(outputs)
    
    return list(input_messages.values())[0]

def ip2_run(topology,input_messages ,ids,num_check_bits,num_decoy):
   
    messages = insert_check_bits(input_messages.copy(), num_check_bits)
    network = Network(topology=topology, messages=messages, size=lambda x: x//2+len(ids[1]), label='00')
    (sequence_qb, base_b), ib_pos, (sequence_qa, base_a) = bob_abc(network=network, num_decoy=num_decoy,ids=ids)
    
    decoy_keys, ops, z_basis, c_keys, m_keys = alice_abcd(network=network, ib_pos=ib_pos, sequence_q=sequence_qa,ids=ids)

    if utp_5_7(network=network, decoy_keys=decoy_keys, basis=base_a, ops=ops):
        decoy_keys, base_a = alice_6(network=network, decoy_keys=decoy_keys)
        if utp_5_7(network=network, decoy_keys=decoy_keys, basis=base_a, ops=[0]*len(base_a)) and utp_5_7(network=network, decoy_keys=[info.memory.qstate_key for info in network.nodes[0].resource_manager.memory_manager if info.state=='OCCUPIED'], basis=base_b, ops=[0]*len(base_b)):
            authenticate(network=network, ib_pos=ib_pos, circuit=bsm_circuit(), z_basis=z_basis)
            auth_9b(network=network, c_keys=c_keys, circuit=bsm_circuit())

    results=decode(network=network, m_keys=m_keys, circuit=bsm_circuit(),input_messages=input_messages)
    return {"recv_msg" :results}

def test():
    input_messages = {2:'011010'}
    ids = {2:'1011', 1:'0111'}
    num_check_bits = 4
    num_decoy = 4
    topology ="\\web\2n_linear.json"
    print(ip2_run(topology,input_messages,ids,num_check_bits,num_decoy))

##test()