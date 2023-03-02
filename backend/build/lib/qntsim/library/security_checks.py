from collections.abc import Iterable
from typing import List, Dict
from random import sample
from numpy.random import randint

from ..topology.node import Node
from ..components.circuit import QutipCircuit
from .network import Network

# class SecurityCheck:
#     @staticmethod
#     def insert_check_bits(network:Network)

def __insert_seq__(lst:List, seq:List):
    is_same_type = all(type(lst[0])==type(ele) for ele in lst[1:])
    insert_locations = sample(range(len(lst)+len(seq)), len(seq))
    iter1, iter2 = iter(lst), iter(seq)
    
    return [next(iter1) if i not in insert_locations else type(lst[0])(next(iter2)) if is_same_type else next(iter2) for i in range(len(lst)+len(seq))], insert_locations

def insert_check_bits(messages:List[str], num_check_bits:int):
    return {tuple((seq:=__insert_seq__(lst=message, seq=randint(2, size=num_check_bits)))[1]):''.join(seq[0]) for message in messages}

def insert_decoy_photons(network:Network, node_index:int, num_decoy_photons:int):
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