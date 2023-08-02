from numbers import Number
from random import choices
from typing import Dict, List, Optional, Tuple, Union
from warnings import warn

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import CircuitInstruction

from ....core.kernel.quantum_manager import QuantumManager
from ...physical_layer.components.circuit import QutipCircuit
from .Error import NoiseError
from .noise import DampingError, PauliError, ReadoutError, ResetError

_ATOL = 1e-6
_1qubit_gates = ['id', 'x', 'h', 'y', 'z', 's', 't', 'tdg', 'ry', 'rx', 'rz']
_2qubit_gates = ['cx', 'swap']
_3qubit_gates = ['ccx']

class NoiseModel:

    def __init__(self) -> None:
        
        '''
        This is the noise model to simulate different quantum noises like SPAM error, gate error, channel error etc.
        '''
        
        self._noise_instruction = {}
        self._noise_qubits = {}
        self._noise_gates = set()
        self._noise = set()
        pass

    def add_readout_error(self, err:ReadoutError, qubit = None) -> None:
        
        '''
        Method to add readout error in noise model
        
        Inputs:
            err [ReadoutError]: <ReadoutError> instance
            qubit [list]: List containing qubits with readout error
        '''
        
        if err.ideal:
            warn("Readout error found as ideal... Discarding the error.")
        else:
            self._noise_instruction["ReadoutError"] = err
            if qubit:
                self._noise_qubits["ReadoutError"] = set(qubit)
            else:
                self._noise_qubits["ReadoutError"] = None
            self._noise = self._noise|set(["ReadoutError"])
        pass
    
    def add_reset_error(self, err:ResetError, qubit = None) -> None:
        
        '''
        Method to add reset error in noise model
        
        Inputs:
            err [ResetError]: <ResetError> instance
            qubit [list]: List containing qubits with reset error
        '''
        
        if err.ideal:
            warn("Reset error found as ideal... Discarding the error.")
        else:
            self._noise_instruction["ResetError"] = err
            if qubit:
                self._noise_qubits["ResetError"] = set(qubit)
            else:
                self._noise_qubits["ResetError"] = None
            self._noise = self._noise|set(["ResetError"])
        pass
    
    def add_Pauli_error(self, err:Union[List[Union[float, Tuple]], Dict[str, List[Number, float]]], qubit = None) -> None:
        
        '''
        Method to add Pauli error in noise model
        
        Inputs:
            err [list or dictionary]: Probability for Pauli gates to apply. :math:`[p_I, p_X, p_Y, p_Z]` or :math:`\\{'P':p_P\\}` or :math:`[('P',p_P)]` for Pauli operator :math:`P` and corresponding probability :math:`p_P`.
            qubit [list]: List containing qubits with reset error
        '''
        
        err = PauliError(err)
        if err.ideal:
            warn("Pauli error found as ideal... Discarding the error.")
        else:
            self._noise_instruction["PauliError"] = err
            if qubit:
                self._noise_qubits["PauliError"] = set(qubit)
            else:
                self._noise_qubits["PauliError"] = None
            self._noise = self._noise|set(["PauliError"])
        pass
    
    def add_BitFlip_error(self, err:Union[Number, float], qubit = None) -> None:
        
        '''
        Method to add bit-flip error in noise model
        
        Inputs:
            err [float]: Probability for bit-flip.
            qubit [list]: List containing qubits with bit-flip error
        '''
        
        if not (isinstance(err, float) or isinstance(err, int)):
            raise NoiseError('Error probability should be either float or integer')
        if err < -_ATOL or err > 1 + _ATOL:
            raise NoiseError(f"Probability {err} does not lie in the interval [0, 1]")
        err = PauliError([1 - err, err, 0, 0])
        if err.ideal:
            warn("Bit-flip error found as ideal... Discarding the error.")
        else:
            self._noise_instruction["BitFlipError"] = err
            if qubit:
                self._noise_qubits["BitFlipError"] = set(qubit)
            else:
                self._noise_qubits["BitFlipError"] = None
            self._noise = self._noise|set(["BitFlipError"])
        pass
    
    def add_PhaseFlip_error(self, err:Union[Number, float], qubit = None) -> None:
        
        '''
        Method to add phase-flip error in noise model
        
        Inputs:
            err [float]: Probability for phase-flip.
            qubit [list]: List containing qubits with phase-flip error
        '''
        
        if not (isinstance(err, float) or isinstance(err, int)):
            raise NoiseError('Error probability should be either float or integer')
        if err < -_ATOL or err > 1 + _ATOL:
            raise NoiseError(f"Probability {err} does not lie in the interval [0, 1]")
        err = PauliError([1 - err, 0, 0, err])
        if err.ideal:
            warn("Phase-flip error found as ideal... Discarding the error.")
        else:
            self._noise_instruction["PhaseFlipError"] = err
            if qubit:
                self._noise_qubits["PhaseFlipError"] = set(qubit)
            else:
                self._noise_qubits["PhaseFlipError"] = None
            self._noise = self._noise|set(["PhaseFlipError"])
        pass
    
    def add_depolarizing_error(self, err:Union[Number, float], qubit = None) -> None:
        
        '''
        Method to add depolarizing error in noise model
        
        Inputs:
            err [float]: Depolarizing error parameter.
            qubit [list]: List containing qubits with depoalrizing error
        '''
        
        if not (isinstance(err, float) or isinstance(err, int)):
            raise NoiseError('Error probability should be either float or integer')
        if err < -_ATOL or err > 4/3 + _ATOL:
            raise NoiseError(f'Depolarising parameter {err} is not in range [0, 4/3]')
        err /= 4
        err = PauliError([1 - 3 * err, err, err, err])
        if err.ideal:
            warn("Depolarizing error found as ideal... Discarding the error.")
        else:
            self._noise_instruction["DepolError"] = err
            if qubit:
                self._noise_qubits["DepolError"] = set(qubit)
            else:
                self._noise_qubits["DepolError"] = None
            self._noise = self._noise|set(["DepolError"])
        pass
    
    def add_generalized_amplitude_damping_error(self, err:float, p = 0, f = None, T = None, qubit = None) -> None:
        
        '''
        Method to add depolarizing error in noise model
        
        Inputs:
            err [float]: Amplitude damping parameter.
            qubit [list]: List containing qubits with depoalrizing error
        '''
        
        if err < -_ATOL or err > 1 + _ATOL:
            raise NoiseError(f"Error parameter {err} does not lie in the interval [0, 1]")
        err = DampingError(Type = 'AD', gamma_am = err, p = p, f = f, T = T)
        if err.ideal:
            warn("Amplitude damping error found as ideal... Discarding the error.")
        else:
            self._noise_instruction[err.type] = err
            if qubit:
                self._noise_qubits[err.type] = set(qubit)
            else:
                self._noise_qubits[err.type] = None
            self._noise = self._noise|set([err.type])
        pass
    
    def add_amplitude_damping_error(self, err:float, qubit = None) -> None:
        
        '''
        Method to add depolarizing error in noise model
        
        Inputs:
            err [float]: Amplitude damping parameter.
            qubit [list]: List containing qubits with depoalrizing error
        '''
        
        self.add_generalized_amplitude_damping_error(err = err, qubit = qubit)
        pass

    def apply(self, qc:Union[QuantumCircuit, QutipCircuit], QNTSim = True) -> Union[QuantumCircuit, QutipCircuit]:
        
        '''
        Method to apply noise model in a quantum circuit
        
        Inputs:
            qc [QuantumCircuit]: <QuantumCircuit> instance
            QNTSim [bool]: True/ False depending on the platform QNTSim/ Qiskit
        
        Returns:
            crc [QuantumCircuit]: <QuantumCircuit> instance
        '''
        
        if not QNTSim:
            from qiskit import (ClassicalRegister, QuantumCircuit,
                                QuantumRegister)
            q_reg = {}
            size = 0
            c_reg = []
            for qr in qc.qregs:
                q_reg[QuantumRegister(qr.size, qr.name)] = [size, size + qr.size]
                size += qr.size
            for cr in qc.cregs:
                c_reg.append(ClassicalRegister(cr.size, cr.name))
            q_r = list(q_reg.keys())
            crc = QuantumCircuit(q_r[0])
            for reg in q_r[1:] + c_reg:
                crc.add_register(reg)
#            if "ResetError" in self._noise:  # THIS IS ONLY FOR TESTING PURPOSE AND SHOULD BE REMOVED BEFORE APPLYING THE NOISE IN THE PROTOCOLS
#                crc = self._apply_reset_error(crc, crc.num_qubits)
            for d in qc._data:
                crc._data.append(d)
                if d.operation.name == 'measure' and "ReadoutError" in self._noise and self._is_noisy(q_reg, d.qubits[0], "ReadoutError"):
                    crc = self._apply_readout_error_qiskit(crc, d)
                else: # GATE NOISE WILL BE ADDED HERE
                    for error in self._noise:
#                                    if d.operation.name in _1qubit_gates and self._is_noisy(q_reg, d.qubits[0], "PauliError"):
#                                        crc = self._apply_Pauli_error_qiskit(crc, d)
                        if d.operation.name in _1qubit_gates + _2qubit_gates + _3qubit_gates:
                            _qubits = []
                            for q in d.qubits:
                                if self._is_noisy(q_reg, q, error):
                                    _qubits.append(q_reg[q._register][0] + q._index)
                            if _qubits:
                                match error:
                                    case "PauliError":
                                        crc = self._apply_Pauli_error(crc, _qubits, error)
                                    case "BitFlipError":
                                        crc = self._apply_Pauli_error(crc, _qubits, error)
                                    case "PhaseFlipError":
                                        crc = self._apply_Pauli_error(crc, _qubits, error)
                                    case "DepolError":
                                        crc = self._apply_Pauli_error(crc, _qubits, error)
                                    case "ADError":
                                        crc = self._apply_AD_error_qiskit(crc, _qubits, error)
            return crc
        from qntsim.components.circuit import QutipCircuit
        crc = QutipCircuit(qc.size)
#        if "ResetError" in self._noise:  # THIS IS ONLY FOR TESTING PURPOSE AND SHOULD BE REMOVED BEFORE APPLYING THE NOISE IN THE PROTOCOLS
#            crc = self._apply_reset_error(crc, crc.size)
        for gate in qc.gates:
            crc.gates.append(gate)
            for error in self._noise:
                match error:
                    case "PauliError":
                        crc = self._apply_Pauli_error(crc, gate[1], error)
                    case "BitFlipError":
                        crc = self._apply_Pauli_error(crc, gate[1], error)
                    case "PhaseFlipError":
                        crc = self._apply_Pauli_error(crc, gate[1], error)
                    case "DepolError":
                        crc = self._apply_Pauli_error(crc, gate[1], error)
        crc.measured_qubits = qc.measured_qubits
        return crc
    
    def execute(self, qc:QutipCircuit, manager:QuantumManager, keys:List[Number]) -> Optional[Dict[Number, Number]]:
        
        '''
        Method to execute circuit with noise in QNTSim
        
        Inputs:
            qc [QuantumCircuit]: <QuantumCircuit> instance
            manager [quantum_manager]: <quantum_manager> for QNTSim
            keys [list]: List of keys to run the QuantumCircuit [i-th qubit in qc will run with keys[i]]
        
        Returns:
            Result: Measurement result
        '''
        
        from qntsim.components.circuit import QutipCircuit
#        if "ResetError" in self._noise:  # THIS IS ONLY FOR TESTING PURPOSE AND SHOULD BE REMOVED BEFORE APPLYING THE NOISE IN THE PROTOCOLS
#            crc = self._apply_reset_error(crc, crc.size)
        for gate in qc.gates:
            crc = QutipCircuit(len(gate[1]))
            crc.gates.append([gate[0], range(len(gate[1]))])
            for error in self._noise:
                if error != "ReadoutError":
                    match error:
                        case "ADError":
                            self._apply_AD_error_QNTSim(crc, manager, [keys[i] for i in gate[1]] + [keys[-1]], error)
                            crc = QutipCircuit(len(gate[1]))
        crc = QutipCircuit(qc.size)
        crc.measured_qubits = qc.measured_qubits
        return self._apply_readout_error_qntsim(crc, manager, keys[:-1])
    
    def _is_noisy(self, reg:Dict[QuantumRegister, List[Number]], qubit_data:type(CircuitInstruction.qubits), err:str) -> bool:
        
        '''
        Method to check whether the qubit for the provided data is noisy or not
        '''
        
        qubit = reg[qubit_data._register][0] + qubit_data._index
        if self._noise_qubits[err] and qubit not in self._noise_qubits[err]:
            return False
        return True
    
    def _apply_reset_error(self, crc:Union[QuantumCircuit, QutipCircuit], size:Number) -> Union[QuantumCircuit, QutipCircuit]:
        
        '''
        Method to apply reset error
        '''
        
        for qubit in range(size):
            if choices(range(3), self._noise_instruction["ResetError"].probabilities)[0] == 2:
                crc.x(qubit)
        return crc

    def _apply_readout_error_qiskit(self, crc:QuantumCircuit, data:CircuitInstruction) -> QuantumCircuit:
        
        '''
        Method to apply readout error on qiskit
        '''
        
        flag = False
        for i in range(2):
            if choices(range(2), self._noise_instruction["ReadoutError"].probabilities[i])[0] - i:
                flag = True
                crc.x(data.qubits).c_if(data.clbits[0], i)
        if flag:
            crc._data.append(data)
        return crc
    
    def _apply_readout_error_qntsim(self, crc:QutipCircuit, manager:QuantumManager, keys:List[Number]) -> Optional[Dict[Number, Number]]:
        
        '''
        Method to apply readout error on QNTSim
        '''
        
        from qntsim.components.circuit import QutipCircuit
#        for key in keys:  # THIS FOR LOOP IS ONLY FOR TESTING PURPOSE AND SHOULD BE REMOVED BEFORE APPLYING THE NOISE IN THE PROTOCOLS
#            states = manager.get(key).state
#            if states[1]:
#                qc = QutipCircuit(1)
#                qc.x(0)
#                qc.measure(0)
#                manager.run_circuit(qc, [key])
        result = manager.run_circuit(crc, keys)
        if not crc.measured_qubits:
            return
        if "ReadoutError" not in self._noise:
            return result
        for key in list(result.keys()):
            if self._noise_qubits["ReadoutError"] and key not in self._noise_qubits["ReadoutError"]:
                continue
            flag = False
            for i in range(2):
                if choices(range(2), self._noise_instruction["ReadoutError"].probabilities[i])[0] - i and result[key] == i:
                    flag = True
            if flag:
                result[key] = 1 - result[key]
                qc = QutipCircuit(1)
                qc.x(0)
                qc.measure(0)
                manager.run_circuit(qc, [key])
        return result
    
    def _apply_Pauli_error(self, crc:Union[QuantumCircuit, QutipCircuit], qubit_data:Union[List[Number], type(CircuitInstruction.qubits)], error:str) -> Union[QuantumCircuit, QutipCircuit]:
        
        '''
        Method to apply Pauli error
        '''
        
        for q in qubit_data:
            ch = choices(range(4), self._noise_instruction[error].probabilities)[0]
            if not ch:
                continue
            if not ~-ch:
                crc.x(q)
                continue
            if not ch & 1:
                crc.y(q)
                continue
            else:
                crc.z(q)
        return crc
    
    def _apply_AD_error_qiskit(self, crc:QuantumCircuit, qubit_data:type(CircuitInstruction.qubits), error:str) -> QuantumCircuit:
        
        '''
        Method to apply Amplitude Damping error in qiskit
        '''
        
        from qiskit import QuantumCircuit, QuantumRegister
        if not crc.num_clbits:
            from qiskit import ClassicalRegister
            cr = ClassicalRegister(1, 'envm')
            crc.add_register(cr)
        qr = QuantumRegister(1, 'env')
        qc = QuantumCircuit(qr)
        crc += qc
        for q in qubit_data:
            ch = choices(range(2), self._noise_instruction[error].probabilities)[0]
            if not ch:
                crc.x(q)
            crc.cry(self._noise_instruction[error].theta_am*2, q, qr)
            crc.cx(qr, q)
            if not ch:
                crc.x(q)
            crc.measure(qr, 0)
            crc.reset(qr)
        return crc
    
    def _apply_AD_error_QNTSim(self, crc:QutipCircuit, manager:QuantumManager, keys:List[Number], error:str) -> None:
        
        '''
        Method to apply Amplitude Damping error in QNTSim
        '''
        
        from qntsim.components.circuit import QutipCircuit
        nq = crc.size
        crc.size += 1
        states = manager.get(keys[-1]).state
        if states[1]:
            qc = QutipCircuit(1)
            qc.x(0)
            qc.measure(0)
            manager.run_circuit(qc, [keys[-1]])
        ch = choices(range(2), self._noise_instruction[error].probabilities)[0]
        if not ch:
            crc.x(0)
        crc.ry(nq, self._noise_instruction[error].theta_am)
        crc.cx(0, nq)
        crc.ry(nq, -self._noise_instruction[error].theta_am)
        crc.cx(0, nq)
        crc.cx(nq, 0)
        if not ch:
            crc.x(0)
        crc.measure(nq)
        manager.run_circuit(crc, keys)
        for q in range(1, crc.size - 1):
            states = manager.get(keys[-1]).state
            if states[1]:
                qc = QutipCircuit(1)
                qc.x(0)
                qc.measure(0)
                manager.run_circuit(qc, [keys[-1]])
            crc = QutipCircuit(2)
            ch = choices(range(2), self._noise_instruction[error].probabilities)[0]
            if not ch:
                crc.x(0)
            crc.ry(1, self._noise_instruction[error].theta_am)
            crc.cx(0, 1)
            crc.ry(1, -self._noise_instruction[error].theta_am)
            crc.cx(0, 1)
            crc.cx(1, 0)
            if not ch:
                crc.x(0)
            crc.measure(1)
            manager.run_circuit(crc, [keys[q], keys[-1]])
        pass
