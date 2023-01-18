import numpy as np
from numpy import pi
from numpy.random import randint, uniform

from .network import Network
from ..components.circuit import QutipCircuit

class Attack:
    @staticmethod
    def denial_of_service(network:Network, **kwargs):
        manager = network.manager
        for i in kwargs.get('nodes'):
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
    def entangle_and_measure(network:Network, **kwargs):
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.measure(1)
        
        manager = network.manager
        for i in kwargs.get('nodes'):
            node = network.nodes[i]
            for info in node.resource_manager.memory_manager:
                key = info.memory.qstate_key
                new_key = manager.new([1, 0])
                manager.run_circuit(qtc, [key, new_key])
                if info.index>network.size-1: break
    
    @staticmethod
    def intercept_and_resend(network:Network, **kwargs):
        manager = network.manager
        for i in kwargs.get('nodes'):
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