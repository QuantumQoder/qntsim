"""Models for simulation of quantum circuit.

This module introduces the Circuit base class and it's platform-specific child classes.
All the gates in the quantum computing field are provided in the base class. The child
classes are defined to implement the parsing logic specific to the quantum computing
platform, while also extending the gates from the base class.

Tha Circuit base class also provides a class generator, since the main intuition behind
the child classes was to separate the parsing logic to each specific logic. Refer to the
documentation of the specific method.

The qutip library is used to calculate the unitary matrix of a circuit.
"""

from dataclasses import field
import math
from copy import deepcopy
from numbers import Number
from types import NoneType, new_class
from typing import (Callable, Dict, List, Literal, Optional, Set, TypeAlias, Union,
                    overload)

import numpy as np
from qiskit import QuantumCircuit
from qutip import Qobj
from qutip.qip.circuit import QubitCircuit
from qutip.qip.operations import (controlled_gate, gate_sequence_product,
                                  qasmu_gate, rz, snot)


def validator(func: Callable[["Circuit", Union[int, float]], NoneType]) -> Callable[["Circuit", Union[int, float]], NoneType]:
    def wrapper(self: "Circuit", *args, **kwargs) -> NoneType:
        assert all(q < self.size for q in args if isinstance(q, int)), "Qubit index out of bounds"
        return func(self, *args, **kwargs)
    return wrapper

class Circuit:
    """This is the base class containing all the gates available in the field of quantum computing.
    The constructor of the class acts as a factory method for the base class and it's child classes,
    while also creating the objects for the corresponding child classes.

    Implementation logic:-
        After the class has been first time imported, Circuit() will return the Circuit class.
        Execuitng Circuit(2) will return the instance of the base class. But, once the type has
        been provided as a string, the class would remember the type and always return the
        corresponding child class, i.e., Circuit("qiskit") would return the QiskitCircuit class
        and then executing Circuit(2) would return the object of the QiskitCircuit. This same
        behaviour can also be achieved by Circuit("qiskit", 2) or Circuit(2, "qiskit"). To override
        the type, the constructor must be called with either a different type or with None, i.e.,
        Circuit("qutip") would override the type and return the QutipCircuit class, Circuit(None)
        will reset the type and return the Circuit class.

    Side effect:-
        Due to the unique implementation logic, the constructor would return the class/object of the
        last value provided in the parameter list, i.e., Circuit("qiskit", 2, 3, "qutip") would return
        an object of QutipCircuit with 3 qubits.

    Returns:
        _type_: _description_
    """
    __type: Optional[str] = None
    __circuit_classes: TypeAlias = Union["QiskitCircuit", "QutipCircuit"]

    @overload
    def __new__(cls, args: Union[Literal["qiskit", "qutip"], int]) -> Union["Circuit", __circuit_classes]: ...

    @overload
    def __new__(cls, args: Literal["qiskit", "qutip"]) -> __circuit_classes: ...

    @overload
    def __new__(cls, args: int) -> __circuit_classes: ...

    def __new__(cls, *args: Union[Optional[Literal["qiskit", "qutip"]], Optional[int]]) -> Union["Circuit", __circuit_classes]:
        """The __new__ of the 'Circuit' class works as an object factory method,
        as well as, a class factory method. Refer to the overloaded type hints.

        Args:
            _type (Literal[&quot;Qiskit&quot;, &quot;Qutip&quot;]): The backend type
            TODO: Keep on adding a str name for increasing dependency on other platforms and add a match case
            corresponding to that
            size (int): the number of qubits used in circuit.

        Returns:
            Circuit: The appropriate child class corresponding to type
        """
        size: Optional[int] = 0
        for arg in args:
            match arg:
                case str(): cls.__type = (arg or cls.__type).lower()
                case int(): size = arg
                case _: cls.__type = None
        match cls.__type:
            case "qiskit": child = QiskitCircuit
            case "qutip": child = QutipCircuit
            case _: child = __class__
        if not isinstance(size, int): raise TypeError("The size, also referred to as the number of qubits, cannot be a non-integer.")
        if size < 0: raise ValueError("The size, also referred to as the number of qubits, cannot be a negative.")
        if size > 0:
            self = object.__new__(child)
            self.size: int = size
            self.gates: List[List[Union[str, List[Union[int, float]]]]] = []
            self.measured_qubits: Set = set()
            self._cache: Optional[np.ndarray] = None
            return self
        return child

    @staticmethod
    def generate_child_class(__type: str, parse_cricuit_func: Callable[["Circuit", type], None]) -> type:
        return new_class(__type.capitalize() + "Circuit", (__class__), {"size": field(int)}, parse_cricuit_func)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(num_qubits = {self.num_qubits}, gates_applied = {self.gates}, measured_qubits = {self.measured_qubits}, width = {self.num_qubits+self.num_measured_qubits})" # + depth = {self.depth},

    def __copy__(self) -> "Circuit":
        """Creates a new object with the same parameter. This is equivalent to deepcopy.
           Also, executing copy is equivalent to performing deepcopy.

        Returns:
            "Circuit": The duplicated object
        """
        circuit = __class__(self.__type, self.size)
        circuit.gates: List[List[Union[str, List[Union[int, float]]]]] = [[gate, [arg for arg in args]] for gate, args in self.gates]
        circuit.measured_qubits: Set = set([qubit for qubit in self.measured_qubits])
        circuit._cache: Optional[np.ndarray] = deepcopy(self._cache)
        return circuit

    def __add__(self, circuit:"Circuit") -> None:
        """Performs in-place (i.e., modifying current object) addition.
        .. warning::
            The function doesn't return the modified object.
            Thus it should be implemented as circuit1 + circuit2 and it would modify circuit1.
            Performing circuit1 = circuit1 + circuit2 would override circuit1 with None.

        Side effect:
            If the size of the incoming circuit is greater than the size of this circuit,
            then the size is overridden with the new size.

        Args:
            circuit ("Circuit"): The circuit to be added into this circuit
        """
        if circuit.num_qubits > self.num_qubits: self.num_qubits = circuit.num_qubits
        self.gates += circuit.gates
        self.measured_qubits |= circuit.measured_qubits

    def __iadd__(self, circuit:"Circuit") -> "Circuit":
        """To perform circuit += other_circuit
           It basically performs the in-place addition and returns the object to be re-assigned into the same variable

        Args:
            circuit ("Circuit"): The circuit to be added into this circuit

        Returns:
            "Circuit": Returns this object after modification
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

    @num_qubits.setter
    def num_qubits(self, __value: int) -> None:
        self.size = __value

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

    def duplicate(self) -> "Circuit":
        """Return a new circuit object which is the copy of the current circuit

        Returns:
            "Circuit": The duplicated object
        """
        return self.__copy__()

    def reverse_circuit(self, inplace:bool, force_reverse:bool = False) -> Optional["Circuit"]:
        """Reverses the circuit, or returns a new reversed circuit if inplace is True.

        Args:
            inplace (bool): Should this_circuit be reversed or return a new circuit with reversed gates
            force_reverse (bool, optional): If the circuit has measure gates, then it can't be reversed.
                                            In such a case, the reversal of the gates need to be forced.
                                            Defaults to False.

        Returns:
            Optional["Circuit"]: A new circuit object with reversed gates
        """
        if self.measured_qubits:
            assert force_reverse, f"In the presence of measured qubits, set force_reverse = {True}"
        if inplace:
            self.gates.reverse()
        else:
            circuit = self.duplicate()
            circuit.gates.reverse()
            return circuit

    def append_gates(self, gates: List[List[Union[str, List[Union[int, float]]]]]) -> None:
        """Adds new gates into the circuit

        Args:
            gates (List[List[Union[str, List[Number]]]]): List of gates needed to be added in the circuit
        """
        assert max(arg for _, args in gates for arg in args if isinstance(arg, int)) < self.num_qubits, \
            f"Maximum numbers of qubits should be less than or equal to {self.num_qubits}."
        self.gates += gates
        
    def apply_gate(self, gate: str, qubits: List[int], angles: List[float]) -> None:
        """
        apply_gate Method to apply gates into the circuit. This can also be used to apply user-defined gates.
                   although the class would not have any knowledge on the user-defined gate

        :param gate: name of the gate to be applied
        :type gate: str
        :param qubits: list of qubits on which the gate can be applied
        :type qubits: List[int]
        :param angles: rotation angles to be applied with the gate
        :type angles: List[float]
        """
        if hasattr(self, gate):
            getattr(self, gate.lower())(*qubits, *[float(angle) for angle in angles])
            return
        self.gates.append([gate, qubits + angles])

    def combine_circuit(self, circuit: "Circuit", qubit_map: Optional[Dict[int, int]] = None, force_combine: bool = False) -> None:
        """
        combine_circuit Compose circuit with incoming_circuit, optionally permuting wires based on the qubit_map

        :param circuit: incoming_circuit to be appended
        :type circuit: Circuit
        :param qubit_map: A map of connection between the qubits of incoming_circuit to new_circuit, of the form {incoming_qubit: this_qubit}, defaults to None
        :type qubit_map: Optional[Dict[int, int]], optional
        :param force_combine: It's not possible to combine circuits if the number of qubits in the incoming_circuit is more
                              than the number of qubits in this_circuit. To do so, one needs to force the combination. In
                              such scenario, this_circuit is adjusted so that the combination can take place, defaults to False
        :type force_combine: bool, optional
        """
        # If number of qubits of this incoming_circuit (circuit) is greater than the number of qubits in this_circuit (self),
        # then one has to force the combination
        if not force_combine:
            assert circuit.num_qubits <= self.num_qubits, f"If number of qubits of the incoming circuit is greater than {self.num_qubits}, then set force_combine = {True}"
        # If the qubit_map is not provided then the incoming_circuit is appended into this_circuit
        if not qubit_map:
            self + circuit
            return
        for gate, args in circuit.gates:
            qubits = list(filter(lambda x: isinstance(x, int), args))
            angles = list(filter(lambda x: isinstance(x, float), args))
            self.apply_gate(gate, [qubit_map.get(qubit, 0) for qubit in qubits], angles)
        self.measured_qubits |= circuit.measured_qubits

    def append_circuit(self, circuit: "Circuit") -> None:
        """
        append_circuit Method to append an incoming_circuit into this_circuit. Equivalent to self + circuit

        :param circuit: incoming_circuit to be appended
        :type circuit: Circuit
        """
        assert circuit.num_qubits <= self.num_qubits, f"Number of qubits in the incoming circuit must be less than or equal to {self.num_qubits}"
        self.combine_circuit(circuit)

    def attach_circuit(self, circuit: "Circuit") -> None:
        """Attach the incoming_circuit with this_circuit, increasing the width (number of qubits) of this circuit

        Args:
            circuit ("Circuit"): the incoming circuit needed to attach
        """
        qubit_map = {i: self.num_qubits + i for i in range(circuit.num_qubits)}
        self.num_qubits += circuit.num_qubits
        self.combine_circuit(circuit, qubit_map)

    def parse_circuit(self, circuit:Optional[Union[QuantumCircuit, QubitCircuit]] = None) -> Union[QuantumCircuit, QubitCircuit]:
        if circuit:
            num_qubits = getattr(circuit, ("num_qubit" if isinstance(circuit, QuantumCircuit) else
                                           "N"))
            assert self.num_qubits == num_qubits, f"The number of qubits in circuit must be equal to {self.num_qubits}."
            num_clbits = getattr(circuit, ("num_clbits" if isinstance(circuit, QuantumCircuit) else
                                           "num_cbits"))
            assert num_clbits, "The circuit object must have classical registers."
            assert self.num_measured_qubits == num_clbits, f"The number of classical bits in circuit must be equal to {self.num_measured_qubits}."

    @validator
    def i(self, __qubit:int) -> None:
        pass

    # Referred as SNOT in QuTIP(4.7)
    @validator
    def h(self, __qubit:int) -> None:
        """Method to apply single-qubit Hadamard gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["h", [__qubit]])
        
    @validator
    def x(self, __qubit:int) -> None:
        """Method to apply single-qubit Pauli-X gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["x", [__qubit]])
        
    @validator
    def y(self, __qubit:int) -> None:
        """Method to apply single-qubit Pauli-Y gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["y", [__qubit]])
        
    @validator
    def z(self, __qubit:int) -> None:
        """Method to apply single-qubit Pauli-Z gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["z", [__qubit]])
        
    @validator
    def s(self, __qubit:int) -> None:
        """Method to apply single S gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["s", [__qubit]])

    # Not in QuTIP(4.7)
    @validator
    def sdg(self, __qubit:int) -> None:
        self.gates.append(["sdg", [__qubit]])
        
    @validator
    def t(self, __qubit:int) -> None:
        """Method to apply single T gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["t", [__qubit]])
        
    # Not in QuTIP(4.7)
    @validator
    def tdg(self, __qubit:int) -> None:
        """Method to apply single TDG gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["tdg", [__qubit]])
        
    # Referred as SQRTNOT in QuTIP(4.7)
    @validator
    def sx(self, __qubit:int) -> None:
        self.gates.append(["sx", [__qubit]])
        
    # Not in QuTIP(4.7)
    @validator
    def ch(self, __control:int, __target:int) -> None:
        self.gates.append(["ch", [__control, __target]])
        
    @validator
    def cx(self, __control:int, __target:int) -> None:
        """Method to apply Control-X gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            target (int): the index of target in the circuit.
        """
        self.gates.append(["cx", [__control, __target]])
        
    @validator
    def cy(self, __control:int, __target:int) -> None:
        self.gates.append(["cy", [__control, __target]])
        
    @validator
    def cz(self, __control:int, __target:int) -> None:
        self.gates.append(["cz", [__control, __target]])
        
    @validator
    def cs(self, __control:int, __target:int) -> None:
        self.gates.append(["cs", [__control, __target]])
        
    # Not in QuTIP(4.7)
    @validator
    def csx(self, __control:int, __target:int) -> None:
        self.gates.append(["csx", [__control, __target]])
        
    @validator
    def swap(self, __qubit1:int, __qubit2:int) -> None:
        """Method to apply SWAP gate on two qubits.
        Args:
            qubit1 (int): the index of qubit1 in the circuit.
            qubit2 (int): the index of qubit2 in the circuit.
        """
        self.gates.append(["swap", [__qubit1, __qubit2]])
        
    @validator
    def iswap(self, __qubit1:int, __qubit2:int) -> None:
        self.gates.append(["iswap", [__qubit1, __qubit2]])

    # Referred as FREDKIN in QuTIP(4.7)
    @validator
    def cswap(self, __control:int, __qubit1:int, __qubit2:int) -> None:
        self.gates.append(["cswap", [__control, __qubit1, __qubit2]])
        
    # Referred as TOFFOLI in QuTIP(4.7)
    @validator
    def ccx(self, __control1:int, __control2:int, __target:int) -> None:
        """Method to apply Toffoli gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            control2 (int): the index of control2 in the circuit.
            target (int): the index of target in the circuit.
        """
        self.gates.append(["ccx", [__control1, __control2, __target]])

    # Referred as PHASEGATE in QuTIP(4.7)
    @validator
    def p(self, __qubit:int, theta:float) -> None:
        self.gates.append(["p", [__qubit, theta]])

    @validator
    def rx(self, __qubit:int, theta:float) -> None:
        self.gates.append(["rx", [__qubit, theta]])

    # Not in QISkit(0.44)
    @validator
    def ry(self, __qubit:int, theta:float) -> None:
        self.gates.append(["ry", [__qubit, theta]])

    @validator
    def rz(self, __qubit:int, theta:float) -> None:
        self.gates.append(["rz", [__qubit, theta]])

    # Referred as CPHASE in QuTIP(4.7)
    @validator
    def cp(self, __control:int, __target:int, theta:float) -> None:
        self.gates.append(["cp", [__control, __target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def crx(self, __control:int, __target:int, theta:float) -> None:
        self.gates.append(["crx", [__control, __target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def cry(self, __control:int, __target:int, theta:float) -> None:
        self.gates.append(["cry", [__control, __target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def crz(self, __control:int, __target:int, theta:float) -> None:
        self.gates.append(["crz", [__control, __target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def rxx(self, __qubit1:int, __qubit2:int, theta:float) -> None:
        self.gates.append(["rxx", [__qubit1, __qubit2, theta]])

    # Not in QuTIP(4.7)
    @validator
    def ryy(self, __qubit1:int, __qubit2:int, theta:float) -> None:
        self.gates.append(["ryy", [__qubit1, __qubit2, theta]])

    # Not in QuTIP(4.7)
    @validator
    def rzz(self, __qubit1:int, __qubit2:int, theta:float) -> None:
        self.gates.append(["rzz", [__qubit1, __qubit2, theta]])

    # Not in QISkit(0.44), QuTIP(4.7)
    @validator
    def rxy(self, __qubit1:int, __qubit2:int, theta:float) -> None:
        self.gates.append(["rxy", [__qubit1, __qubit2, theta]])

    # Referred as QASMU in QuTIP(4.7)
    @validator
    def u(self, __qubit:int, theta:float, phi:float, lam:float) -> None:
        self.gates.append(["u", [__qubit, theta, phi, lam]])

    # Not in QuTIP(4.7)
    @validator
    def cu(self, __control:int, __target:int, theta:float, phi:float, lam:float, gamma:float=0) -> None:
        self.gates.append(["cu", [__control, __target, theta, phi, lam, gamma]])

    def measure(self, *qubits: int) -> None:
        """Method to measure quantum bit into classical bit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.measured_qubits.update(qubits)

    def measure_all(self) -> None:
        for qubit in range(self.num_qubits): self.measured_qubits.add(qubit)

    def measure_active(self) -> None:
        self.measure_all()

class QiskitCircuit(Circuit):
    """Class for a quantum circuit.
    Attributes:
        size (int): the number of qubits in the circuit.
        gates (List[str]): a list of commands bound to register.
        measured_qubits (List[int]): a list of indices of measured qubits.
    """

    def __new__(cls, size:int) -> "Circuit":
        return Circuit.__new__(cls, "qiskit", size)

    def parse_circuit(self, circuit:Optional[QuantumCircuit] = None) -> QuantumCircuit:
        Circuit.parse_circuit(self, circuit)
        circuit = circuit or QuantumCircuit(self.num_qubits, self.num_measured_qubits)
        for gate, args in self.gates:
            qubits: List[int] = list(filter(lambda x: isinstance(x, int), args))
            angles: List[float] = list(filter(lambda x: isinstance(x, float), args))
            if hasattr(circuit, gate):
                _gate = getattr(circuit, gate)
                _gate(*angles, *qubits)
            else:
                match gate:
                    case "ry":
                        circuit.u(angles[0], 0, 0, qubits[0])
                    case "rxy":
                        from qiskit.extensions import UnitaryGate
                        circuit.append(UnitaryGate([[1,                         0,                         0, 1],
                                                    [0,     math.cos(angles[0]/2), -1j*math.sin(angles[0]/2), 0],
                                                    [0, -1j*math.sin(angles[0]/2),     math.cos(angles[0]/2), 0],
                                                    [1,                         0,                         0, 1]]),
                                       *qubits)
        circuit.measure(list(self.measured_qubits), circuit.cregs)
        return circuit

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

class QutipCircuit(Circuit):
    """Class for a quantum circuit.
    Attributes:
        size (int): the number of qubits in the circuit.
        gates (List[str]): a list of commands bound to register.
        measured_qubits (List[int]): a list of indices of measured qubits.
    """

    @staticmethod
    def __cu(args:List[float], N:Optional[int] = None, target:int = 0) -> Qobj:
        return controlled_gate(qasmu_gate(args[:3], N, target))

    @staticmethod
    def __rxy(phi:float) -> Qobj:
        return Qobj([[1,               0,                       0, 1],
                     [0,     math.cos(phi/2), -1j*math.sin(phi/2), 0],
                     [0, -1j*math.sin(phi/2),     math.cos(phi/2), 0],
                     [1,                   0,                   0, 1]])

    @staticmethod
    def __rxx(phi:float) -> Qobj:
        return Qobj([[    math.cos(phi/2),                   0,                   0, -1j*math.sin(phi/2)],
                     [                  0,     math.cos(phi/2), -1j*math.sin(phi/2),                   0],
                     [                  0, -1j*math.sin(phi/2),     math.cos(phi/2),                   0],
                     [-1j*math.sin(phi/2),                   0,                   0,     math.cos(phi/2)]])

    @staticmethod
    def __ryy(phi:float) -> Qobj:
        return Qobj([[   math.cos(phi/2),                   0,                   0, 1j*math.sin(phi/2)],
                     [                 0,     math.cos(phi/2), -1j*math.sin(phi/2),                  0],
                     [                 0, -1j*math.sin(phi/2),     math.cos(phi/2),                  0],
                     [1j*math.sin(phi/2),                   0,                   0,    math.cos(phi/2)]])

    @staticmethod
    def __rzz(phi:float) -> Qobj:
        import cmath
        return Qobj([[cmath.exp(-1j*phi/2),                   0,                   0,                    0],
                     [                   0, cmath.exp(1j*phi/2),                   0,                    0],
                     [                   0,                   0, cmath.exp(1j*phi/2),                    0],
                     [                   0,                   0,                   0, cmath.exp(-1j*phi/2)]])

    @staticmethod
    def __ch() -> Qobj:
        return controlled_gate(snot())

    @staticmethod
    def __tdg() -> Qobj:
        return rz(-math.pi/4)

    @staticmethod
    def __sdg() -> Qobj:
        return rz(-math.pi/2)
    
    __gate_map = {"x":"X",
                  "y":"Y",
                  "z":"Z",
                  "s":"S",
                  "t":"T",
                  "h":"SNOT",
                  "u":"QASMU",
                  "p":"PHASEGATE",
                  "rx":"RX",
                  "ry":"RY",
                  "rz":"RZ",
                  "sx":"SQRTNOT",
                  "cx":"CX",
                  "cy":"CY",
                  "cs":"CS",
                  "ct":"CT",
                  "cp":"CPHASE",
                  "cx":"CNOT",
                  "ch":"ch",
                  "cu":"cu",
                  "crx":"CRX",
                  "cry":"CRY",
                  "crz":"CRZ",
                  "ccx":"TOFFOLI",
                  "tdg":"tdg",
                  "sdg":"sdg",
                  "rxx":"rxx",
                  "rxy":"rxy",
                  "ryy":"ryy",
                  "rzz":"rzz",
                  "swap":"SWAP",
                  "iswap":"iSWAP",
                  "cswap":"FREDKIN"}

    def __new__(cls, size:int) -> "Circuit":
        return Circuit.__new__(cls, "qutip", size)

    def parse_circuit(self, circuit:Optional[QubitCircuit] = None) -> QubitCircuit:
        Circuit.parse_circuit(self, circuit)
        circuit = circuit or QubitCircuit(self.num_qubits, num_cbits=self.num_measured_qubits,
                                          user_gates={"ch":self.__ch,
                                                      "cu":self.__cu,
                                                      "tdg":self.__tdg,
                                                      "sdg":self.__sdg,
                                                      "rxx":self.__rxx,
                                                      "rxy":self.__rxy,
                                                      "ryy":self.__ryy,
                                                      "rzz":self.__rzz})
        for gate, args in self.gates:
            qubits: List[int] = list(filter(lambda x: isinstance(x, int), args))
            angles: List[float] = list(filter(lambda x: isinstance(x, float), args))
            circuit.add_gate(self.__gate_map.get(gate), targets=qubits[-1], controls=qubits[:-1], arg_value=angles)
        for i, measured_qubit in enumerate(self.measured_qubits):
            circuit.add_measurement(f"M{i}", targets=measured_qubit, classical_store=i)
        return circuit

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
            qc.user_gates = {"tdg":self.__tdg}
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