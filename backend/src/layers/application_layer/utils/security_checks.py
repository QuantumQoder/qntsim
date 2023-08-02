from random import sample
from typing import Dict, List, Sequence

from numpy.random import randint

from ...physical_layer.components.circuit import QutipCircuit
from ..communication.network import Network

# class SecurityCheck:
#     @staticmethod
#     def insert_check_bits(network:Network)

def __insert_seq__(lst:List, seq:List):
    # is_same_type = all(type(lst[0])==type(ele) for ele in lst[1:])
    insert_locations = sorted(sample(range(len(lst)+len(seq)), len(seq)))
    iter1, iter2 = iter(lst), iter(seq)
    
    return  insert_locations, [next(iter1) if i not in insert_locations else next(iter2) for i in range(len(lst)+len(seq))]

def __separate_seq__(indices:Sequence, lst:Sequence):
    seq_items = [lst[index] for index in indices]
    list_items = list(set(lst)-set(seq_items))
    # seq_items = [lst.pop() for index in indices]
    # list_items = list(set(lst) - set(seq_items))
    # print(f"indices: {indices},\nlst: {lst},\nlsit_items: {list_items},\nseq_items: {seq_items}")

    return type(lst)(list_items), type(lst)(seq_items)

def insert_check_bits(messages:List[str], num_check_bits:int):
    """Insert check bits into a list of strings

    Args:
        messages (List[str]): Message, to insert check bits
        num_check_bits (int): Number of check bits to be inserted

    Returns:
        modified message (Dict[Tuple[int], str]): The message 
    """
    return {tuple((seq:=__insert_seq__(lst=message, seq=randint(2, size=num_check_bits)))[0]):''.join([str(ele) for ele in seq[1]]) for message in messages}

def insert_decoy_photons(network:Network, node_index:int, num_decoy_photons:int):
    """Insert decoy photons at memory nodes of the network

    Args:
        network (Network): <Network> object
        node_index (int): The node, to insert the decoy photons
        num_decoy_photons (int): Number of decoy photons to be inserted

    Returns:
        keys, photons (List[int], numpy.array): The keys of the decoy photons, The photon states
    """
    photons = randint(4, size=num_decoy_photons)
    photon_iterator = iter(photons)
    for info in network.nodes[node_index].resource_manager.memory_manager:
        if info.state=='RAW':
            key = info.memory.qstate_key
            # if info.state=='OCCUPIED': network.manager.get(key).state = [1, 0]
            try: q, r = divmod(next(photon_iterator), 2)
            except: break
            qtc = QutipCircuit(1)
            if r: qtc.x(0)
            if q: qtc.h(0)
            network.manager.run_circuit(qtc, [key])
            info.state = 'OCCUPIED'
    
    return [info.memory.qstate_key for info in network.nodes[node_index].resource_manager.memory_manager if info.state=='OCCUPIED'], photons