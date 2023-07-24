"""Models for simulation of quantum circuit.
This module introduces the QuantumCircuit class. The qutip library is used to calculate the unitary matrix of a circuit.
"""

from math import e, pi
from typing import List

import numpy as np
from qutip.qip.circuit import QubitCircuit
from qutip.qip.operations import gate_qntsim_product
from qutip import Qobj

class Circuit():
    """Class for a quantum circuit.
    Attributes:
        size (int): the number of qubits in the circuit.
        gates (List[str]): a list of commands bound to register.
        measured_qubits (List[int]): a list of indices of measured qubits.
    """

    def __init__(self, size: int):
        """Constructor for quantum circuit.
        Args:
            size (int): the number of qubits used in circuit.
        """
        
        self.size = size
        self.gates = []
        self.measured_qubits = []
        self._cache = None

    def compile_circuit(self, qc):
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

