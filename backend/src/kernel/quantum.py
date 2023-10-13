import math
from abc import abstractmethod
from numbers import Complex
from typing import Dict, List, Literal, Optional, Union

import numpy as np
from qiskit import QuantumCircuit
from qutip.qip.circuit import Gate, QubitCircuit
from qutip.qip.operations import gate_sequence_product

from .circuit import Circuit, QiskitCircuit, QutipCircuit
from .quantum_utils import (measure_entangled_state_with_cache_ket,
                            measure_multiple_with_cache_ket,
                            measure_state_with_cache_ket)


class State:
    def __init__(self, amplitudes: Union[List[Complex], List[List[Complex]]]) -> None:
        num_qubits = math.log2(len(amplitudes))
        assert num_qubits.is_integer(), "Length of amplitudes should be 2 ** n."
        self.state: Optional[Union[QuantumCircuit, np.ndarray]] = None
        self.keys: List[int] = []

    def __str__(self) -> str:
        return f"keys: {self.keys}, state: {self.state}"

class QiskitState(State):
    def __init__(self, amplitudes: List[Complex], keys: Union[int, List[int]]) -> None:
        State.__init__(self, amplitudes)
        if isinstance(keys, int): keys = [keys]
        self.state = QuantumCircuit(math.log2(keys))
        self.keys = keys

class QutipState(State):
    def __init__(self, amplitudes: List[Complex], keys: Union[int, List[int]]) -> None:
        State.__init__(self, amplitudes)
        if isinstance(keys, int): keys = [keys]
        self.state = np.array(amplitudes)
        self.keys = keys

class DensityState(State):
    def __init__(self, amplitudes: Union[List[Complex], List[List[Complex]]], keys: Union[int, List[int]]) -> None:
        State.__init__(self, amplitudes)
        if isinstance(keys, int): keys = [keys]
        self.state = np.array(amplitudes)
        if isinstance(amplitudes, complex):
            self.state = np.outer(self.state, self.state)
        self.keys = keys

class QuantumManager:
    def __new__(cls, __type: Literal["qiskit", "qutip", "density"]) -> Union["QiskitManager", "QutipManager", "DensityManager"]:
        match __type:
            case "qiskit": child = QiskitManager
            case "qutip": child = QutipManager
            case "density": child = DensityManager
            case _: raise ValueError
        self = object.__new__(child)
        self.states: Dict[int, State] = {}
        self._least_available: int = 0
        return self

    @abstractmethod
    def new(self, amplitudes: List[Complex]) -> int:
        num_qubits = math.log2(len(amplitudes))
        assert num_qubits.is_integer(), "Length of amplitudes should be 2 ** n."

    def get(self, key: int) -> Optional["State"]:
        return self.states.get(key)

    @abstractmethod
    def run_circuit(self, circuit: "Circuit", keys: Union[int, List[int]]) -> Dict[int, int]:
        if isinstance(keys, int): keys = [keys]
        assert circuit.num_qubits == len(keys), "Keys provided doesn't match with the size of the circuit."

    def _prepare_circuit(self, circuit: "Circuit") -> Union[QuantumCircuit, QubitCircuit]:
        return circuit.parse_circuit()

    @abstractmethod
    def set(self, keys: Union[int, List[int]], amplitudes: List[Complex]) -> None:
        if isinstance(keys, int): keys = [keys]
        num_qubits = math.log2(len(amplitudes))
        assert num_qubits.is_integer(), "Length of amplitudes should be 2 ** n."

    def remove(self, key: int) -> None:
        self.states.pop(key)

class QiskitManager(QuantumManager):
    def __new__(cls) -> "QiskitManager":
        return QuantumManager.__new__(cls, "qiskit")

    def new(self, amplitudes: List[Complex] = [complex(1), complex(0)]) -> int:
        QuantumManager.new(self, amplitudes)
        key: int = self._least_available
        self.states[key] = QiskitState(amplitudes, key)
        self._least_available += 1
        return key

    def run_circuit(self, circuit: "QiskitCircuit", keys: Union[int, List[int]]) -> Dict[int, int]:
        QuantumManager.run_circuit(self, circuit, keys)

    def set(self, keys: List[int], amplitudes: List[Complex]) -> None:
        if isinstance(keys, int): keys = [keys]
        QuantumManager.set(self, keys, amplitudes)
        new_state = QiskitState(amplitudes, keys)
        for key in keys:
            self.states[key] = new_state

class QutipManager(QuantumManager):
    def __new__(cls) -> "QutipManager":
        return QuantumManager.__new__(cls, "qutip")

    def new(self, amplitudes: List[Complex] = [complex(1), complex(0)]) -> int:
        QuantumManager.new(self, amplitudes)
        key: int = self._least_available
        self.states[key] = QutipState(amplitudes, key)
        self._least_available += 1
        return key

    def _prepare_circuit(self, circuit: "Circuit", keys: List[int]):
        old_states = []
        all_keys = []

        # go through keys and get all unique qstate objects
        #print('prepare circuit qutip')
        for key in keys:
            qstate = self.states[key]
            if qstate.keys[0] not in all_keys:
                old_states.append(qstate.state)
                all_keys += qstate.keys

        # construct compound state; order qubits
        new_state = [1]
        for state in old_states:
            new_state = np.kron(new_state, state)

        # get circuit matrix; expand if necessary
        circ_mat = circuit.get_unitary_matrix()
        if circuit.size < len(all_keys):
            # pad size of circuit matrix if necessary
            diff = len(all_keys) - circuit.size
            circ_mat = np.kron(circ_mat, np.identity(2 ** diff))

        # apply any necessary swaps
        if not all([all_keys.index(key) == i for i, key in enumerate(keys)]):
            all_keys, swap_mat = self._swap_qubits(all_keys, keys)
            circ_mat = circ_mat @ swap_mat

        return new_state, all_keys, circ_mat

    def _swap_qubits(self, all_keys, keys):
        swap_circuit = QubitCircuit(N=len(all_keys))
        for i, key in enumerate(keys):
            j = all_keys.index(key)
            if j != i:
                gate = Gate("SWAP", targets=[i, j])
                swap_circuit.add_gate(gate)
                all_keys[i], all_keys[j] = all_keys[j], all_keys[i]
        swap_mat = gate_sequence_product(swap_circuit.propagators()).full()
        return all_keys, swap_mat

    def run_circuit(self, circuit: "Circuit", keys: Union[int, List[int]]) -> Dict[int, int]:
        if isinstance(keys, int): keys = [keys]
        super().run_circuit(circuit, keys)
        #print('run circuit')
        new_state, all_keys, circ_mat = self._prepare_circuit(circuit, keys)

        new_state = circ_mat @ new_state

        if len(circuit.measured_qubits) == 0:
            # set state, return no measurement result
            new_ket = QutipState(new_state, all_keys)
            for key in all_keys:
                self.states[key] = new_ket
            return None
        else:
            # measure state (state reassignment done in _measure method)
            keys = [all_keys[i] for i in circuit.measured_qubits]
            return self._measure(new_state, keys, all_keys)

    def _measure(self, state: List[complex], keys: List[int], all_keys: List[int]) -> Dict[int, int]:
        """Method to measure qubits at given keys.
        SHOULD NOT be called individually; only from circuit method (unless for unit testing purposes).
        Modifies quantum state of all qubits given by all_keys.
        Args:
            state (List[complex]): state to measure.
            keys (List[int]): list of keys to measure.
            all_keys (List[int]): list of all keys corresponding to state.
        Returns:
            Dict[int, int]: mapping of measured keys to measurement results.
        """

        if len(keys) == 1:
            if len(all_keys) == 1:
                prob_0 = measure_state_with_cache_ket(tuple(state))
                if np.random() < prob_0:
                    result = 0
                else:
                    result = 1

            else:
                key = keys[0]
                num_states = len(all_keys)
                state_index = all_keys.index(key)
                state_0, state_1, prob_0 = measure_entangled_state_with_cache_ket(tuple(state), state_index, num_states)
                if np.random.random() < prob_0:
                    new_state = np.array(state_0, dtype=complex)
                    result = 0
                else:
                    new_state = np.array(state_1, dtype=complex)
                    result = 1

            all_keys.remove(keys[0])

        else:
            # swap states into correct position
            if not all([all_keys.index(key) == i for i, key in enumerate(keys)]):
                all_keys, swap_mat = self._swap_qubits(all_keys, keys)
                state = swap_mat @ state

            # calculate meas probabilities and projected states
            len_diff = len(all_keys) - len(keys)
            new_states, probabilities = measure_multiple_with_cache_ket(tuple(state), len(keys), len_diff)

            # choose result, set as new state
            possible_results = np.arange(0, 2 ** len(keys), 1)
            result = np.random.choice(possible_results, p=probabilities)
            new_state = new_states[result]

            for key in keys:
                all_keys.remove(key)

        result_states = [np.array([1, 0]), np.array([0, 1])]
        result_digits = [int(x) for x in bin(result)[2:]]
        while len(result_digits) < len(keys):
            result_digits.insert(0, 0)

        for res, key in zip(result_digits, keys):
            # set to state measured
            new_state_obj = QutipState(result_states[res], [key])
            self.states[key] = new_state_obj
        
        if len(all_keys) > 0:
            new_state_obj = QutipState(new_state, all_keys)
            for key in all_keys:
                self.states[key] = new_state_obj
        
        return dict(zip(keys, result_digits))

    def run_circuit(self, circuit: "QutipCircuit", keys: Union[int, List[int]]) -> Dict[int, int]:
        QuantumManager.run_circuit(self, circuit, keys)
        if isinstance(keys, int): keys = [keys]
        circuit: QubitCircuit = self._prepare_circuit(circuit)

    def set(self, keys: List[int], amplitudes: List[Complex]) -> None:
        if isinstance(keys, int): keys = [keys]
        QuantumManager.set(self, keys, amplitudes)
        new_state = QutipState(amplitudes, keys)
        for key in keys:
            self.states[key] = new_state

class DensityManager(QuantumManager):
    def __new__(cls) -> "DensityManager":
        return QuantumManager.__new__(cls, "density")

    def new(self, amplitudes: List[Complex] = [complex(1), complex(0)]) -> int:
        QuantumManager.new(self, amplitudes)
        key: int = self._least_available
        self.states[key] = DensityState(amplitudes, key)
        self._least_available += 1
        return key