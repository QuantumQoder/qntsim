import numpy as np
from numpy import pi
from numpy.random import randint, uniform

from qntsim.components.circuit import QutipCircuit

class Attack:
    @staticmethod
    def entangle_and_measure(network_obj, **kwargs):
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.measure(1)
        manager = network_obj.manager
        for j in kwargs.get('nodes'):
            node = network_obj.nodes[j]
            for info1, info2 in zip(node.resource_manager.memory_manager, node.resource_manager.memory_manager[::-1]):
                keys = info1.memory.qstate_key, info2.memory.qstate_key
                results = manager.run_circuit(qtc, list(keys))
                if -~info1.index>network_obj.size: break
    
    @staticmethod
    def denial_of_service(network_obj, **kwargs):
        qtc = QutipCircuit(1)
        manager = network_obj.manager
        for j in kwargs.get('nodes'):
            node = network_obj.nodes[j]
            for info in node.resource_manager.memory_manager:
                if randint(2):
                    key = info.memory.qstate_key
#                     print(key)
                    qtc.rz(0, 2*uniform()*pi)
                    qtc.rx(0, 2*uniform()*pi)
                    manager.run_circuit(qtc, [key])
                if -~info.index>network_obj.size: break
    
    @staticmethod
    def intercept_and_resend(network_obj, **kwargs):
        manager = network_obj.manager
        for j in kwargs.get('nodes'):
            node = network_obj.nodes[j]
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
                if -~info.index>network_obj.size: break