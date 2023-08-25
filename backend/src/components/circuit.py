"""Models for simulation of quantum circuit.
This module introduces the QuantumCircuit class. The qutip library is used to calculate the unitary matrix of a circuit.
"""

from abc import abstractmethod
from copy import deepcopy
from math import e, pi
from numbers import Number
from typing import Dict, List, Literal, Optional, Self, Union

import numpy as np
from qiskit import QuantumCircuit
from qutip import Qobj
from qutip.qip.circuit import QubitCircuit
from qutip.qip.operations import (controlled_gate, gate_sequence_product,
                                  qasmu_gate, rz, snot)

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
    @staticmethod
    def create(type:Literal["Qiskit", "Qutip"]) -> "BaseCircuit":
        """Returns the appropriate class corresponding to type

        Args:
            type (Literal[&quot;Qiskit&quot;, &quot;Qutip&quot;]): The backend type
            TODO: Keep on adding a str name for increasing dependency and add a match case
            corresponding to that

        Returns:
            BaseCircuit: The appropriate child class corresponding to type
        """
        match type:
            case "Qiskit":
                return Circuit
            case "Qutip":
                return QutipCircuit

    def __init__(self, size: int) -> None:
        """Constructor for quantum circuit.
        .. warning::
            The object is unable to perform inplace measurement and/or apply classically controlled gates
        TODO: Resolve the precaution.
        
        Args:
            size (int): the number of qubits used in circuit.
        """
        
        self.size = size
        self.gates = []
        self.measured_qubits = []
        self._cache = None

    def __copy__(self) -> Self:
        """Creates a new object with the same parameter. This is equivalent to deepcopy.
           Also, executing copy is equivalent to performing deepcopy.

        Returns:
            Self: The duplicated object
        """
        circuit = __class__(self.size)
        circuit.gates = [[gate, [arg for arg in args]] for gate, args in self.gates]
        circuit.measured_qubits = [qubit for qubit in self.measured_qubits]
        circuit._cache = deepcopy(self._cache)
        return circuit

    def __add__(self, circuit:Self) -> None:
        """Performs in-place (i.e., modifying current object) addition.
        .. warning::
            The function doesn't return the modified object.
            Thus it should be implemented as circuit1 + circuit2 and it would modify circuit1.
            Performing circuit1 = circuit1 + circuit2 would override circuit1 with None.

        Args:
            circuit (Self): The circuit to be added into this circuit
        """
        if circuit.num_qubits > self.num_qubits:
            self.size = circuit.size
        self.gates += circuit.gates
        self.measured_qubits += circuit.measured_qubits

    def __iadd__(self, circuit:Self) -> Self:
        """To perform circuit += other_circuit
           It basically performs the in-place addition and returns the object to be re-assigned into the same variable

        Args:
            circuit (Self): The circuit to be added into this circuit

        Returns:
            Self: Returns this object after modification
        """
        self + circuit
        return self

    @property
    def num_qubits(self) -> int:
        """Number of qubits in the circuit

        Returns:
            int: number of qubits in the circuit
        """
        return self.size

    @property
    def num_gates(self) -> int:
        """Total number of individual gates applied in the circuit

        Returns:
            int: total number of individual gates
        """
        return len(self.gates)

    @property
    def num_measured_qubits(self) -> int:
        """Number of qubits measured in the circuit

        Returns:
            int: number of measured qubits
        """
        return len(self.measured_qubits)

    @property
    def num_layers(self) -> int:
        """The number of layers in the circuit

        Returns:
            int: total number of layers in the circuit
        """
        if not self.gates:
            return 0
        op_stack = [0 for _ in range(self.num_qubits)]
        for _, qubits in self.gates:
            levels = []
            for qubit in qubits:
                if not isinstance(qubit, int):
                    continue
                levels.append(op_stack[qubit])
            max_level = max(levels)
            for qubit in qubits:
                op_stack[qubit] = max_level
        return max(op_stack)
    
    @property
    def depth(self) -> int:
        """The number of layers in the circuit

        Returns:
            int: circuit depth
        """
        return self.num_layers

    @property
    def width(self) -> int:
        """The width is the sum of total qubits and total clbits present in the circuit.
           In the absence of actual clbits in the circuit, it is the sum of the number
           of qubits and number of clbits.

        Returns:
            int: circuit width
        """
        return self.num_qubits + self.num_measured_qubits
    
    @abstractmethod
    def measure(self, qubit: int):
        pass

    def duplicate(self) -> Self:
        """Return a new circuit object which is the copy of the current circuit

        Returns:
            Self: The duplicated object
        """
        return self.__copy__()

    def reverse_circuit(self, inplace:bool, force_reverse:bool = False) -> Optional[Self]:
        """Reverses the circuit, or returns a new reversed circuit if inplace is True.

        Args:
            inplace (bool): Should this_circuit be reversed or return a new circuit with reversed gates
            force_reverse (bool, optional): If the circuit has measure gates, then it can't be reversed.
                                            In such a case, the reversal of the gates need to be forced.
                                            Defaults to False.

        Returns:
            Optional[Self]: A new circuit object with reversed gates
        """
        if self.measured_qubits:
            assert force_reverse, f"In the presence of measured qubits, set force_reverse = {True}"
        if inplace:
            self.gates.reverse()
        else:
            circuit = self.duplicate()
            circuit.gates.reverse()
            return circuit

    def append_gates(self, gates:List[List[Union[str, List[Number]]]]) -> None:
        """Adds new gates into the circuit

        Args:
            gates (List[List[Union[str, List[Number]]]]): List of gates needed to be added in the circuit
        """
        assert self.num_qubits > max(arg for _, args in gates for arg in args if isinstance(arg, int)), f"Maximum numbers of qubits should be less than or equal to {self.num_qubits}."
        self.gates += gates

    def combine_circuit(self, circuit:Self, qubit_map:Optional[Dict[int, int]] = None, force_combine:bool = False) -> None:
        """Compose circuit with incoming_circuit, optionally permuting wires based on the qubit_map (provided or generated)

        Args:
            circuit (Self): incoming_circuit to be appended
            qubit_map (Optional[Dict[int, int]], optional): A map of connection between the qubits of incoming_circuit to new_circuit.
                                                            Defaults to None. {incoming_qubit:new_qubit}
            force_combine (bool, optional): It's not possible to combine circuits if the number of qubits in the incoming_circuit is more
                                            than the number of qubits in this_circuit. To do so, one needs to force the combination. In
                                            such scenario, this_circuit is adjusted so that the combination can take place. Defaults to False.
        """
        # If number of qubits of this_circuit (self) is less than the number of qubits in the incoming_circuit (circuit),
        # then one has to force the combination
        if self.num_qubits < max(arg for _, args in circuit.gates for arg in args if isinstance(arg, int)):
            assert force_combine, f"If number of qubits of the incoming circuit is greater than {self.num_qubits}, then set force_combine = {True}"
        
        # If the qubit_map is not provided, then it's generated from the total number of qubits present in this_circuit (self) or the incoming_circuit (circuit).
        # If the combination is forced, then it is assumed that the incoming_circuit has more qubits than this_circuit (This is referred as the force_combine assumpiton in the context of this function)
        qubit_map = qubit_map or {i:i for i in range(circuit.num_qubits if force_combine else self.num_qubits)}

        # As per the force_combine assumption, an inplace addition is done which then modifies this_circuit (self)
        if force_combine:
            self + circuit
            return

        # If combination is not forced, then assuming that the number of qubits of the incoming_circuit is within the bounds of this_circuit,
        # gates from the incoming_circuit are applied appropriately based on the qubit_map (provided or generated)
        for gate, args in circuit.gates:
            getattr(self, gate)(*[qubit_map.get(arg, 0) if isinstance(arg, int) else arg for arg in args])
        self.measured_qubits = list(set(self.measured_qubits).union(circuit.measured_qubits))

    def append_circuit(self, circuit:Self) -> None:
        """Attach the incoming_circuit with this_circuit, increasing the width (number of qubits) of this circuit

        Args:
            circuit (Self): the incoming circuit needed to attach
        """
        self.combine_circuit(circuit=circuit, qubit_map={i:i for i in range(self.num_qubits)}.update({circuit.num_qubits+i:circuit.num_qubits+i for i in range(circuit.num_qubits)}))
            

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
        # ## print('get unitary')
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

