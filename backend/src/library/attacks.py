import numpy as np
from functools import partial
from enum import Enum
from numpy import pi
from numpy.random import randint, uniform
from concurrent.futures import ProcessPoolExecutor

from .network import Network
from ..components.circuit import QutipCircuit
from ..kernel.quantum_manager import QuantumManagerDensity

class Attack(Enum):
    @classmethod
    def implement(cls, network:Network, *args, attack:str):
        manager = network.manager
        nodes = range(1, len(network.nodes)) if len(network.nodes)>1 else [0]
        ProcessPoolExecutor().map(partial(cls[attack].value, network=network, manager=manager), nodes)

    @staticmethod
    def _denial_of_service_(i:int, network:Network, manager:QuantumManagerDensity):
        node = network.nodes[i]
        for info in node.resource_manager.memory_manager:
            if randint(2):
                qtc = QutipCircuit(1)
                qtc.rx(0, 2*uniform()*pi)
                qtc.rz(0, 2*uniform()*pi)
                key = info.memory.qstate_key
                manager.run_circuit(qtc, [key])
            if info.index>network.size-1: break
    
    @staticmethod
    def _entangle_and_measure_(i:int, network:Network, manager:QuantumManagerDensity):
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.measure(1)
        
        node = network.nodes[i]
        for info in node.resource_manager.memory_manager:
            key = info.memory.qstate_key
            new_key = manager.new([1, 0])
            manager.run_circuit(qtc, [key, new_key])
            if info.index>network.size-1: break
    
    @staticmethod
    def _intercept_and_resend_(i:int, network:Network, manager:QuantumManagerDensity):
        node = network.nodes[i]
        for info in node.resource_manager.memory_manager:
            key = info.memory.qstate_key
            basis = randint(2)
            qtc = QutipCircuit(1)
            if basis: qtc.h(0)
            qtc.measure(0)
            result = manager.run_circuit(qtc, [key])
            new_key = manager.new([1-result.get(key), result.get(key)])
            if basis:
                qtc = QutipCircuit(1)
                qtc.h(0)
                manager.run_circuit(qtc, [new_key])
                manager.get(key).state = manager.get(new_key).state
                manager.get(new_key).state = np.ndarray([1, 0])
            if info.index>network.size-1: break
    
    DoS = _denial_of_service_
    EM = _entangle_and_measure_
    IR = _intercept_and_resend_