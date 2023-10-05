from enum import Enum
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, TypeAlias, Union

import numpy as np

from ..kernel.circuit import Circuit

if TYPE_CHECKING:
    from ..topology.node import EndNode, ServiceNode
    from ..kernel.quantum_kernel import QiskitManager, QutipManager

class OnMemoryAttack:
    __node_type: TypeAlias = Union[EndNode, ServiceNode]
    __manager_type: TypeAlias = Union[QiskitManager, QutipManager]
    
    @staticmethod
    def implement(node: __node_type,
                  quantum_manager: __manager_type,
                  attack: Callable[[__node_type, __manager_type], None],
                  *args, **kwargs) -> Optional[List[int]]:
        """
        implement Implements the attack on to the node

        :param node: Node to be attacked
        :type node: Union[EndNode, ServiceNode]
        :param quantum_manager: QuantumManager to execute on-memory circuits
        :type quantum_manager: Union[QiskitManager, QutipManager]
        :param attack: attack to be implemented
        :type attack: Callable[[__node_type, __manager_type], None]
        :return: any leakages to be returned
        :rtype: Optional[List[int]]
        """
        return attack(node, quantum_manager, *args, **kwargs)

    @staticmethod
    def denial_of_service(node: __node_type, quantum_manager: __manager_type, *args, **kwargs) -> None:
        """
        denial_of_service

        :param node: Node to be attacked
        :type node: __node_type
        :param quantum_manager: QuantumManager to execute on-memory circuits
        :type quantum_manager: __manager_type
        """
        circuit_type: str = quantum_manager.__class__.__name__[:-7].lower()
        for mem_info in node.resource_manager.memory_manager:
            if np.random.randint(2):
                key = mem_info.memory.qstate_key
                circuit = Circuit(circuit_type, 1)
                circuit.rx(0, 2*np.random.uniform() * np.pi)
                circuit.rz(0, 2*np.random.uniform() * np.pi)
                quantum_manager.run_circuit(circuit, [key])

    @staticmethod
    def entangle_and_measure(node: __node_type, quantum_manager: __manager_type, *args, **kwargs) -> List[int]:
        """
        entangle_and_measure

        :param node: Node to be attacked
        :type node: __node_type
        :param quantum_manager: QuantumManager to execute on-memory circuits
        :type quantum_manager: __manager_type
        :return: leakages due to attack
        :rtype: List[int]
        """
        circuit_type: str = quantum_manager.__class__.__name__[:-7].lower()
        circuit = Circuit(circuit_type, 2)
        circuit.cx(0, 1)
        circuit.measure(1)
        leaked_bins: List[int] = []
        for mem_info in node.resource_manager.memory_manager:
            key = mem_info.memory.qstate_key
            new_key = quantum_manager.new([1, 0])
            leaked_bins.append(quantum_manager.run_circuit(circuit, [key, new_key]).get(new_key))
        return leaked_bins

    @staticmethod
    def intercept_and_resend(node: __node_type, quantum_manager: __manager_type, *args, **kwargs) -> List[int]:
        """
        intercept_and_resend

        :param node: Node to be attacked
        :type node: __node_type
        :param quantum_manager: QuantumManager to execute on-memory circuits
        :type quantum_manager: __manager_type
        :return: leakages due to attack
        :rtype: List[int]
        """
        circuit_type: str = quantum_manager.__class__.__name__[:-7].lower()
        circuit_class = Circuit(circuit_type)
        leaked_bins: List[int] = []
        for mem_info in node.resource_manager.memory_manager:
            key = mem_info.memory.qstate_key
            base = np.random.randint(2)
            circuit = circuit_class(1)
            if base: circuit.h(0)
            circuit.measure(0)
            output: Dict[int, int] = quantum_manager.run_circuit(circuit, [key])
            leaked_bins.append(output.get(key))
            new_key = quantum_manager.new([1 - output.get(key), output.get(key)])
            if base:
                circuit = circuit_class(1)
                circuit.h(0)
                quantum_manager.run_circuit(circuit, [new_key])
                quantum_manager.get(key).state = quantum_manager.get(new_key).state
                quantum_manager.get(new_key).state = np.ndarray([1, 0])
        return leaked_bins
    
class ATTACK_TYPE(Enum):
    DS = OnMemoryAttack.denial_of_service
    EM = OnMemoryAttack.entangle_and_measure
    IR = OnMemoryAttack.intercept_and_resend