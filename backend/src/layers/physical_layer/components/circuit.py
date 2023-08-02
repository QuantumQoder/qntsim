"""Models for simulation of quantum circuit.
This module introduces the QuantumCircuit class. The qutip library is used to calculate the unitary matrix of a circuit.
"""

from abc import abstractmethod
from math import e, pi
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import numpy as np
from qiskit import QuantumCircuit
from qutip import Qobj
from qutip.qip.circuit import QubitCircuit
from qutip.qip.operations import (controlled_gate, gate_sequence_product,
                                  qasmu_gate, rz, snot)

from ....core.kernel.quantum_kernel import QuantumKernel
from ....core.kernel.quantum_manager import QuantumManager
from ....core.topology.node import Node

#from sympy import Q
#from QNTSim.build.lib.qntsim.components import circuit
#from QNTSim.build.lib.qntsim.kernel.quantum_manager import QuantumManager
#from QNTSim1.QNTSim.src.kernel.quantumkernel import QuantumManagerKetQiskit, QuantumManagerKetQutip



def x_gate():
    mat = np.array([[0, 1],
                    [1, 0]])
    return Qobj(mat, dims=[[2], [2]])


def y_gate():
    mat = np.array([[0, -1.j],
                    [1.j, 0]])
    return Qobj(mat, dims=[[2], [2]])


def z_gate():
    mat = np.array([[1, 0],
                    [0, -1]])
    return Qobj(mat, dims=[[2], [2]])


def s_gate():
    mat = np.array([[1.,   0],
                    [0., 1.j]])
    return Qobj(mat, dims=[[2], [2]])


def t_gate():
    mat = np.array([[1.,   0],
                    [0., e ** (1.j * (pi / 4))]])
    return Qobj(mat, dims=[[2], [2]])

def tdg_gate():
    return rz(-1 * np.pi/4)


def validator(func):
    def wrapper(self, *args, **kwargs):
        rot_gates =['rx','ry','rz']
        for q in args:
            if func.__name__ not in rot_gates:
                assert q < self.size, 'qubit index out of range'
                assert q not in self.measured_qubits, 'qubit has been measured'
        if func.__name__ != 'measure':
            self._cache = None
        return func(self, *args, **kwargs)

    return wrapper


class BaseCircuit():



    @classmethod
    def create(cls,type):
        # #print(" base ckt type",type)
        Circuit_class=None
        if type=='Qiskit':
            Circuit_class=Circuit
        elif type=='Qutip':
            Circuit_class=QutipCircuit

        return Circuit_class

    def __init__(self, size: int):
        """Constructor for quantum circuit.
        Args:
            size (int): the number of qubits used in circuit.
        """
        
        self.size = size
        self.gates = []
        self.measured_qubits = []
        self._cache = None

    
    @abstractmethod
    def measure(self, qubit: int):
        pass

    def reverse_circuit(self, inplace:bool=True) -> Optional["BaseCircuit"]:
        if self.measured_qubits:
            print(f"Measurement has been done on qubits: {self.measured_qubits}\n Hence, a new circuit object will be returned with the reversed gates")
            inplace = False
        if inplace: self.gates.reverse()
        else:
            circuit = __class__(size=self.size)
            circuit.gates = reversed(self.size)
            return circuit

    @property
    def num_gates(self) -> int:
        return len(self.gates)

    @property
    def num_qubits(self) -> int:
        return self.size

    @property
    def num_measured_qubits(self) -> int:
        return len(self.measured_qubits)

    @property
    def depth(self) -> int:
        indices = [index for gate in self.gates for index in gate[1] if isinstance(index, int)]
        return max(set(indices), key=indices.count)

    def append_gates(self, gates:List[str, List[int, float]]) -> None:
        assert self.num_qubits >= max(gate[1] for gate in gates), f"Maximum numbers of qubits should be less than or equal to {self.num_qubits} qubits of the current circuit"
        self.gates += gates

    def combine_circuit(self, circuit:"BaseCircuit", qubit_map:Optional[Dict[int, int]]) -> None:
        assert qubit_map and self.num_qubits == circuit.num_qubits, f"If the connection between the qubits is not provided then the number of qubits should be {self.num_qubits} for both."
        assert self.num_qubits >= circuit.num_qubits, f"Maximum numbers of qubits should be less than or equal to {self.num_qubits} qubits of the current circuit"
        qubit_map = {val:key for key, val in qubit_map.items()} if qubit_map else {i:i for i in range(self.num_qubits)}
        try:
            for [gate, indices] in circuit.gates:
                getattr(self, gate)(*[qubit_map.get(index) for index in indices])
        finally: pass

    def __copy__(self) -> "BaseCircuit":
        circuit = __class__(size=self.size)
        circuit.gates = [[gate[0], [el for el in gate[1]]] for gate in self.gates]
        circuit.measured_qubits = [qubit for qubit in self.measured_qubits]
        circuit._cache = self._cache
        return circuit

    def duplicate(self) -> "BaseCircuit":
        return self.__copy__()

    def get_counts(self, quantum_manager:Union[QuantumKernel, QuantumManager], nodes:Union[Node, List[Node]], node_map:Dict[str, Union[int, List[int]]], shots:int=1024) -> Tuple[Dict[int, Dict[int, int]], Dict[str, int]]:
        """
        outputs = {500:{0:0.5, 1:0.5}, 1000:{0:0.5, 1:0.5}, ...}
        counts = {"00":145, "01":346, ...}
        """
        if isinstance(nodes, int): nodes = [nodes]
        node_map = {key:([val] if isinstance(val, int) else val) for key, val in node_map.items()}
        assert len(nodes) <= self.num_qubits, "Number of nudes should be less than number of qubits."
        memory_managers = [([node for node in nodes if node.name==node_name][0]).resource_manager.memory_manager[i:i+1] for node_name, qubits in node_map.items() for i in range(len(qubits))]
        keys = [info.memory.qstate_key for infos in zip(*memory_managers) for info in infos]
        outputs = {key:{0:0, 1:0} for key in keys}
        counts = {}
        for _ in range(shots):
            for infos in zip(*memory_managers):
                for info in infos:
                    info.to_raw()
            result = quantum_manager.run_circuit(circuit=self, keys=keys)
            base = ""
            for key, val in result.items():
                base += str(val)
                outputs[key][val] += 1
            if base in counts: counts[base] += 1
            else: counts[base] = 1
        for key, res in outputs.items():
            for bit, count in res.items():
                if count == 0: res.pop(bit)
            if not res: outputs.pop(key)
        return outputs, counts

class Circuit(BaseCircuit):
    """Class for a quantum circuit.
    Attributes:
        size (int): the number of qubits in the circuit.
        gates (List[str]): a list of commands bound to register.
        measured_qubits (List[int]): a list of indices of measured qubits.
    """

    def __init__(self, size: int):
        super().__init__(size)

    def compile_circuit(self, qc:QuantumCircuit) -> QuantumCircuit:
        """Method to get unitary matrix of circuit without measurement.
        Args:
            qc (QuantumCircuit): The quantum circuit on which the gates need to be applied
            keys (List[int]): list of keys for quantum states to apply circuit to.
        Returns:
            QuantumCircuit: quantum circuit with the gates
        """

        # Get the gate info from the called gates
        for gate in self.gates:
            name, indices = gate

            # apply the gates based on the datra received
            if name == 'h':
                qc.h(indices[0])
            elif name == 'x':
                qc.x(indices[0])
            elif name == 'y':
                qc.y(indices[0])
            elif name == 'z':
                qc.z(indices[0])
            elif name == 'cx':
                qc.cx(indices[0], indices[1])
            elif name == 'ccx':
                qc.ccx(indices[0], indices[1], indices[2])
            elif name == 'swap':
                qc.swap(indices[0], indices[1])
            elif name == 't':
                qc.t(indices[0])
            elif name == 's':
                qc.s(indices[0])
            elif name == 'tdg':
                qc.tdg(indices[0])
            else:
                raise NotImplementedError
        for i, key_index in enumerate(self.measured_qubits):
            qc.measure(key_index, i)
        return qc

    def h(self, qubit: int):
        """Method to apply single-qubit Hadamard gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['h', [qubit]])

    def x(self, qubit: int):
        """Method to apply single-qubit Pauli-X gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['x', [qubit]])

    def y(self, qubit: int):
        """Method to apply single-qubit Pauli-Y gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['y', [qubit]])

    def z(self, qubit: int):
        """Method to apply single-qubit Pauli-Z gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['z', [qubit]])

    def cx(self, control: int, target: int):
        """Method to apply Control-X gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            target (int): the index of target in the circuit.
        """

        self.gates.append(['cx', [control, target]])

    def ccx(self, control1: int, control2: int, target: int):
        """Method to apply Toffoli gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            control2 (int): the index of control2 in the circuit.
            target (int): the index of target in the circuit.
        """

        self.gates.append(['ccx', [control1, control2, target]])

    def swap(self, qubit1: int, qubit2: int):
        """Method to apply SWAP gate on two qubits.
        Args:
            qubit1 (int): the index of qubit1 in the circuit.
            qubit2 (int): the index of qubit2 in the circuit.
        """

        self.gates.append(['swap', [qubit1, qubit2]])

    def t(self, qubit: int):
        """Method to apply single T gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['t', [qubit]])

    def tdg(self, qubit: int):
        """Method to apply single TDG gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['tdg', [qubit]])


    def s(self, qubit: int):
        """Method to apply single S gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['s', [qubit]])

    def measure(self, qubit: int):
        """Method to measure quantum bit into classical bit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.measured_qubits.append(qubit)


class QutipCircuit(BaseCircuit):
    """Class for a quantum circuit.
    Attributes:
        size (int): the number of qubits in the circuit.
        gates (List[str]): a list of commands bound to register.
        measured_qubits (List[int]): a list of indices of measured qubits.
    """
    def __init__(self, size: int):
        super().__init__(size)
    
    def get_unitary_matrix(self) -> "np.ndarray":
        """Method to get unitary matrix of circuit without measurement.
        Returns:
            np.ndarray: the matrix for the circuit operations.
        """
        # #print('get unitary')
        if self._cache is None:
            if len(self.gates) == 0:
                self._cache = np.identity(2 ** self.size)
                return self._cache

            qc = QubitCircuit(self.size)
            qc.user_gates = {"X": x_gate,
                             "Y": y_gate,
                             "Z": z_gate,
                             "S": s_gate,
                             "T": t_gate,
                             "tdg":tdg_gate}
            for gate in self.gates:
                name, indices = gate
                if name == 'h':
                    qc.add_gate('SNOT', indices[0])
                elif name == 'x':
                    qc.add_gate('X', indices[0])
                elif name == 'y':
                    qc.add_gate('Y', indices[0])
                elif name == 'z':
                    qc.add_gate('Z', indices[0])
                elif name == 'cx':
                    qc.add_gate('CNOT', controls=indices[0], targets=indices[1])
                elif name == 'ccx':
                    qc.add_gate('TOFFOLI', controls=indices[:2], targets=indices[2])
                elif name == 'swap':
                    qc.add_gate('SWAP', indices)
                elif name == 't':
                    qc.add_gate('T', indices[0])
                elif name == 's':
                    qc.add_gate('S', indices[0])
                elif name == 'tdg':
                    qc.add_gate('tdg', indices[0])
                elif name == 'ry':
                    qc.add_gate('RY', indices[0],arg_value=indices[1])
                elif name == 'rx':
                    qc.add_gate('RX', indices[0],arg_value=indices[1])
                elif name == 'rz':
                    qc.add_gate('RZ', indices[0],arg_value=indices[1])
                else:
                    raise NotImplementedError
            self._cache = gate_sequence_product(qc.propagators()).full()
            return self._cache
        return self._cache

    @validator
    def ry(self, qubit, arg_value):
        self.gates.append(['ry',[qubit,arg_value]])

    @validator
    def rx(self,qubit, arg_value):
        self.gates.append(['rx',[qubit,arg_value]])

    @validator
    def rz(self,qubit, arg_value):
        self.gates.append(['rz',[qubit,arg_value]])

    @validator
    def h(self, qubit: int):
        """Method to apply single-qubit Hadamard gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['h', [qubit]])

    @validator
    def x(self, qubit: int):
        """Method to apply single-qubit Pauli-X gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['x', [qubit]])

    @validator
    def y(self, qubit: int):
        """Method to apply single-qubit Pauli-Y gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['y', [qubit]])

    @validator
    def z(self, qubit: int):
        """Method to apply single-qubit Pauli-Z gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['z', [qubit]])

    @validator
    def cx(self, control: int, target: int):
        """Method to apply Control-X gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            target (int): the index of target in the circuit.
        """

        self.gates.append(['cx', [control, target]])

    @validator
    def ccx(self, control1: int, control2: int, target: int):
        """Method to apply Toffoli gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            control2 (int): the index of control2 in the circuit.
            target (int): the index of target in the circuit.
        """

        self.gates.append(['ccx', [control1, control2, target]])

    @validator
    def swap(self, qubit1: int, qubit2: int):
        """Method to apply SWAP gate on two qubits.
        Args:
            qubit1 (int): the index of qubit1 in the circuit.
            qubit2 (int): the index of qubit2 in the circuit.
        """

        self.gates.append(['swap', [qubit1, qubit2]])

    @validator
    def t(self, qubit: int):
        """Method to apply single T gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['t', [qubit]])

    @validator
    def s(self, qubit: int):
        """Method to apply single S gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['s', [qubit]])
    
    @validator
    def tdg(self, qubit: int):
        """Method to apply single TDG gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.gates.append(['tdg', [qubit]])

    @validator
    def measure(self, qubit: int):
        """Method to measure quantum bit into classical bit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """

        self.measured_qubits.append(qubit)

