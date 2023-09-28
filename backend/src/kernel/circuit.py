"""Models for simulation of quantum circuit.
This module introduces the BaseCircuit class and it's platform-specific child classes.
The child classes in the module cannot be instantiated separately. They must be instantiated
through the BaseCircuit.__new__ dunder.
The qutip library is used to calculate the unitary matrix of a circuit.
"""

import math
from copy import deepcopy
from numbers import Number
from types import NoneType
from typing import (Callable, Dict, List, Literal, Optional, TypeAlias, Union,
                    overload)

import numpy as np
from qiskit import QuantumCircuit
from qutip import Qobj
from qutip.qip.circuit import QubitCircuit
from qutip.qip.operations import (controlled_gate, gate_sequence_product,
                                  qasmu_gate, rz, snot)


def validator(func:Callable[["BaseCircuit", [...]], NoneType]) -> Callable:
    def wrapper(self:"BaseCircuit", *args, **kwargs) -> NoneType:
        assert all(q < self.size for q in args if isinstance(q, int)), "Qubit index out of bounds"
        return func(self, *args, **kwargs)
    return wrapper

class BaseCircuit:
    __circuit_class: TypeAlias = Union["QiskitCircuit", "QutipCircuit"]

    # def __new__(cls, *args: Union[Literal["Qiskit", "Qutip"], int]) -> Union["BaseCircuit", __circuit_class]:
    #     for arg in args:
    #         match arg:
    #             case str():
    #                 cls.__type = arg
    #                 match cls.__type:
    #                     case "Qiskit":
    #                         child_cls = QiskitCircuit
    #                     case "Qutip":
    #                         child_cls = QutipCircuit
    #             case int():
                    
    
    @overload
    def __new__(cls, __type:Literal["Qiskit", "Qutip"]) -> __circuit_class: ...
    
    @overload
    def __new__(cls, __type:Literal["Qiskit", "Qutip"], size:int) -> "BaseCircuit": ...
    
    def __new__(cls, __type:Literal["Qiskit", "Qutip"], size:Optional[int] = None) -> Union["BaseCircuit", __circuit_class]:
        """The __new__ of the 'BaseCircuit' class works as an object factory method,
        as well as, a class factory method. Refer to the overloaded type hints.

        Args:
            _type (Literal[&quot;Qiskit&quot;, &quot;Qutip&quot;]): The backend type
            TODO: Keep on adding a str name for increasing dependency on other platforms and add a match case
            corresponding to that
            size (int): the number of qubits used in circuit.

        Returns:
            BaseCircuit: The appropriate child class corresponding to type
        """
        cls.__type = __type
        match cls.__type:
            case "Qiskit":
                child_cls = QiskitCircuit
            case "Qutip":
                child_cls = QutipCircuit
        if size:
            self = object.__new__(child_cls)
            self.size = size
            self.gates = []
            self.measured_qubits = []
            self._cache = None
            return self
        return child_cls

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(num_qubits = {self.num_qubits}, gates_applied = {self.gates}, measured_qubits = {self.measured_qubits}, width = {self.num_qubits+self.num_measured_qubits})" # + depth = {self.depth},

    def __copy__(self) -> "BaseCircuit":
        """Creates a new object with the same parameter. This is equivalent to deepcopy.
           Also, executing copy is equivalent to performing deepcopy.

        Returns:
            "BaseCircuit": The duplicated object
        """
        circuit = __class__(self.__type, self.size)
        circuit.gates = [[gate, [arg for arg in args]] for gate, args in self.gates]
        circuit.measured_qubits = [qubit for qubit in self.measured_qubits]
        circuit._cache = deepcopy(self._cache)
        return circuit

    def __add__(self, circuit:"BaseCircuit") -> None:
        """Performs in-place (i.e., modifying current object) addition.
        .. warning::
            The function doesn't return the modified object.
            Thus it should be implemented as circuit1 + circuit2 and it would modify circuit1.
            Performing circuit1 = circuit1 + circuit2 would override circuit1 with None.

        Args:
            circuit ("BaseCircuit"): The circuit to be added into this circuit
        """
        if circuit.num_qubits > self.num_qubits:
            self.size = circuit.size
        self.gates += circuit.gates
        self.measured_qubits += circuit.measured_qubits

    def __iadd__(self, circuit:"BaseCircuit") -> "BaseCircuit":
        """To perform circuit += other_circuit
           It basically performs the in-place addition and returns the object to be re-assigned into the same variable

        Args:
            circuit ("BaseCircuit"): The circuit to be added into this circuit

        Returns:
            "BaseCircuit": Returns this object after modification
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

    def duplicate(self) -> "BaseCircuit":
        """Return a new circuit object which is the copy of the current circuit

        Returns:
            "BaseCircuit": The duplicated object
        """
        return self.__copy__()

    def reverse_circuit(self, inplace:bool, force_reverse:bool = False) -> Optional["BaseCircuit"]:
        """Reverses the circuit, or returns a new reversed circuit if inplace is True.

        Args:
            inplace (bool): Should this_circuit be reversed or return a new circuit with reversed gates
            force_reverse (bool, optional): If the circuit has measure gates, then it can't be reversed.
                                            In such a case, the reversal of the gates need to be forced.
                                            Defaults to False.

        Returns:
            Optional["BaseCircuit"]: A new circuit object with reversed gates
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

    def combine_circuit(self, circuit:"BaseCircuit", qubit_map:Optional[Dict[int, int]] = None, force_combine:bool = False) -> None:
        """Compose circuit with incoming_circuit, optionally permuting wires based on the qubit_map (provided or generated)

        Args:
            circuit ("BaseCircuit"): incoming_circuit to be appended
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

    def append_circuit(self, circuit:"BaseCircuit") -> None:
        """Attach the incoming_circuit with this_circuit, increasing the width (number of qubits) of this circuit

        Args:
            circuit ("BaseCircuit"): the incoming circuit needed to attach
        """
        qubit_map = {i:i for i in range(self.num_qubits)}
        qubit_map.update({circuit.num_qubits+i:circuit.num_qubits+i for i in range(circuit.num_qubits)})
        self.combine_circuit(circuit=circuit, qubit_map=qubit_map)

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
    def i(self, qubit:int) -> None:
        pass

    # Referred as SNOT in QuTIP(4.7)
    @validator
    def h(self, qubit:int) -> None:
        """Method to apply single-qubit Hadamard gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["h", [qubit]])
        
    @validator
    def x(self, qubit:int) -> None:
        """Method to apply single-qubit Pauli-X gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["x", [qubit]])
        
    @validator
    def y(self, qubit:int) -> None:
        """Method to apply single-qubit Pauli-Y gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["y", [qubit]])
        
    @validator
    def z(self, qubit:int) -> None:
        """Method to apply single-qubit Pauli-Z gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["z", [qubit]])
        
    @validator
    def s(self, qubit:int) -> None:
        """Method to apply single S gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["s", [qubit]])

    # Not in QuTIP(4.7)
    @validator
    def sdg(self, qubit:int) -> None:
        self.gates.append(["sdg", [qubit]])
        
    @validator
    def t(self, qubit:int) -> None:
        """Method to apply single T gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["t", [qubit]])
        
    # Not in QuTIP(4.7)
    @validator
    def tdg(self, qubit:int) -> None:
        """Method to apply single TDG gate on a qubit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.gates.append(["tdg", [qubit]])
        
    # Referred as SQRTNOT in QuTIP(4.7)
    @validator
    def sx(self, qubit:int) -> None:
        self.gates.append(["sx", [qubit]])
        
    # Not in QuTIP(4.7)
    @validator
    def ch(self, control:int, target:int) -> None:
        self.gates.append(["ch", [control, target]])
        
    @validator
    def cx(self, control:int, target:int) -> None:
        """Method to apply Control-X gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            target (int): the index of target in the circuit.
        """
        self.gates.append(["cx", [control, target]])
        
    @validator
    def cy(self, control:int, target:int) -> None:
        self.gates.append(["cy", [control, target]])
        
    @validator
    def cz(self, control:int, target:int) -> None:
        self.gates.append(["cz", [control, target]])
        
    @validator
    def cs(self, control:int, target:int) -> None:
        self.gates.append(["cs", [control, target]])
        
    # Not in QuTIP(4.7)
    @validator
    def csx(self, control:int, target:int) -> None:
        self.gates.append(["csx", [control, target]])
        
    @validator
    def swap(self, qubit1:int, qubit2:int) -> None:
        """Method to apply SWAP gate on two qubits.
        Args:
            qubit1 (int): the index of qubit1 in the circuit.
            qubit2 (int): the index of qubit2 in the circuit.
        """
        self.gates.append(["swap", [qubit1, qubit2]])
        
    @validator
    def iswap(self, qubit1:int, qubit2:int) -> None:
        self.gates.append(["iswap", [qubit1, qubit2]])

    # Referred as FREDKIN in QuTIP(4.7)
    @validator
    def cswap(self, control:int, qubit1:int, qubit2:int) -> None:
        self.gates.append(["cswap", [control, qubit1, qubit2]])
        
    # Referred as TOFFOLI in QuTIP(4.7)
    @validator
    def ccx(self, control1:int, control2:int, target:int) -> None:
        """Method to apply Toffoli gate on three qubits.
        Args:
            control1 (int): the index of control1 in the circuit.
            control2 (int): the index of control2 in the circuit.
            target (int): the index of target in the circuit.
        """
        self.gates.append(["ccx", [control1, control2, target]])

    # Referred as PHASEGATE in QuTIP(4.7)
    @validator
    def p(self, qubit:int, theta:float) -> None:
        self.gates.append(["p", [qubit, theta]])

    @validator
    def rx(self, qubit:int, theta:float) -> None:
        self.gates.append(["rx", [qubit, theta]])

    # Not in QISkit(0.44)
    @validator
    def ry(self, qubit:int, theta:float) -> None:
        self.gates.append(["ry", [qubit, theta]])

    @validator
    def rz(self, qubit:int, theta:float) -> None:
        self.gates.append(["rz", [qubit, theta]])

    # Referred as CPHASE in QuTIP(4.7)
    @validator
    def cp(self, control:int, target:int, theta:float) -> None:
        self.gates.append(["cp", [control, target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def crx(self, control:int, target:int, theta:float) -> None:
        self.gates.append(["crx", [control, target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def cry(self, control:int, target:int, theta:float) -> None:
        self.gates.append(["cry", [control, target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def crz(self, control:int, target:int, theta:float) -> None:
        self.gates.append(["crz", [control, target, theta]])

    # Not in QuTIP(4.7)
    @validator
    def rxx(self, qubit1:int, qubit2:int, theta:float) -> None:
        self.gates.append(["rxx", [qubit1, qubit2, theta]])

    # Not in QuTIP(4.7)
    @validator
    def ryy(self, qubit1:int, qubit2:int, theta:float) -> None:
        self.gates.append(["ryy", [qubit1, qubit2, theta]])

    # Not in QuTIP(4.7)
    @validator
    def rzz(self, qubit1:int, qubit2:int, theta:float) -> None:
        self.gates.append(["rzz", [qubit1, qubit2, theta]])

    # Not in QISkit(0.44), QuTIP(4.7)
    @validator
    def rxy(self, qubit1:int, qubit2:int, theta:float) -> None:
        self.gates.append(["rxy", [qubit1, qubit2, theta]])

    # Referred as QASMU in QuTIP(4.7)
    @validator
    def u(self, qubit:int, theta:float, phi:float, lam:float) -> None:
        self.gates.append(["u", [qubit, theta, phi, lam]])

    # Not in QuTIP(4.7)
    @validator
    def cu(self, control:int, target:int, theta:float, phi:float, lam:float, gamma:float=0) -> None:
        self.gates.append(["cu", [control, target, theta, phi, lam, gamma]])

    def apply_gate(self, gate: str, qubits: List[int], angles: List[float]) -> None:
        getattr(self, gate)(*qubits, *[float(angle) for angle in angles])
    
    def measure(self, qubit: int) -> None:
        """Method to measure quantum bit into classical bit.
        Args:
            qubit (int): the index of qubit in the circuit.
        """
        self.measured_qubits.append(qubit)

class QiskitCircuit(BaseCircuit):
    """Class for a quantum circuit.
    Attributes:
        size (int): the number of qubits in the circuit.
        gates (List[str]): a list of commands bound to register.
        measured_qubits (List[int]): a list of indices of measured qubits.
    """

    def __new__(cls, size:int) -> "BaseCircuit":
        return BaseCircuit.__new__(cls, "Qiskit", size)

    def parse_circuit(self, circuit:Optional[QuantumCircuit] = None) -> QuantumCircuit:
        BaseCircuit.parse_circuit(self, circuit)
        circuit = circuit or QuantumCircuit(self.num_qubits, self.num_measured_qubits)
        for gate, args in self.gates:
            qubits = [arg for arg in args if isinstance(arg, int)]
            angles = list(set(args) - set(qubits))
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
        circuit.measure(self.measured_qubits, circuit.cregs)
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

class QutipCircuit(BaseCircuit):
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

    def __new__(cls, size:int) -> "BaseCircuit":
        return BaseCircuit.__new__(cls, "Qutip", size)

    def parse_circuit(self, circuit:Optional[QubitCircuit] = None) -> QubitCircuit:
        BaseCircuit.parse_circuit(self, circuit)
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
            qubits = [arg for arg in args if isinstance(arg, int)]
            angles = list(set(args) - set(qubits))
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