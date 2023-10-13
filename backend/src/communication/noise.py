import math
import random
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from qntsim.kernel.circuit import Circuit

if TYPE_CHECKING:
    from ..kernel.circuit import QiskitCircuit, QutipCircuit
    from ..kernel.quantum_kernel import QiskitManager, QutipManager
    from ..resource_management.memory_manager import MemoryInfo

class Noise:
    """
    Noise.implement('pauli', [0.5, 0.5], circuit = qc_obj)
    Noise.implement('readout', [0.5, 0.5], result = result)
    Noise.implement('reset', [0.5, 0.5], mem_infos = infos)
    Noise.implement('amp_damp', 0.5, keys = keys, network = network_obj)
    """

    @staticmethod
    def implement(noise: Dict[Literal["pauli", "readout", "reset", "amp_damp"], Union[float, List[float]]] = {}, **kwds) -> None:
        for noise_type, probabilities in noise.items():
            getattr(__class__, noise_type)(probabilities, **kwds)
        getattr(__class__, "readout")(kwds.pop("readout", [0, 0]), **kwds)

    @staticmethod
    def pauli(err_probs: List[float] = [0, 0, 0, 0],
              circuit: Optional[Union["QiskitCircuit", "QutipCircuit"]] = None, **_) -> None:
        print("pauli")
        if not circuit: return
        if (array_length := len(err_probs)) < 4: err_probs += [0 for _ in range(4 - array_length)]
        else: err_probs = err_probs[:4]
        if random.random() < err_probs[1]: circuit.x(0)
        if random.random() < err_probs[2]: circuit.y(0)
        if random.random() < err_probs[3]: circuit.z(0)

    @staticmethod
    def readout(err_probs: List[float] = [0, 0], result: Optional[Dict[int, int]] = {}, **_) -> None:
        print("readout")
        if not result: return
        if (array_length := len(err_probs)) < 2: err_probs += [0 for _ in range(2 - array_length)]
        else: err_probs = err_probs[:2]
        p01, p10 = err_probs
        matrix: List[List[float]] = [[1-p01, p01],
                                     [p10, 1-p10]]
        for key, val in result.items():
            result[key] = random.choices([0, 1], matrix[val])[0]

    @staticmethod
    def reset(err: float,
              mem_infos: Optional[List["MemoryInfo"]] = [],
              circuit: Optional[Union["QiskitCircuit", "QutipCircuit"]] = None,
              quantum_manager: Optional[Union["QiskitManager", "QutipManager"]] = None, **_) -> None:
        print("reset")
        if not mem_infos or not circuit or not quantum_manager: return
        if isinstance(err, list): err = err[:1]
        if not isinstance(mem_infos, list): mem_infos = [mem_infos]
        qc = circuit.duplicate()
        qc.measured_qubits = set()
        for mem_info in mem_infos:
            if random.random() < err:
                mem_key = mem_info.memory.qstate_key
                quantum_manager.run_circuit(qc, [mem_key])
                mem_info.to_raw()

    @staticmethod
    def amplitude_damping(gamma: float, keys: Optional[List[float]] = [],
                          quantum_manager: Optional[Union["QiskitManager", "QutipManager"]] = None, **_) -> None:
        print("amp_damp")
        if not keys or not quantum_manager: return
        if isinstance(gamma, list): gamma = gamma[:1]
        if isinstance(keys, int): keys = [keys]
        theta = math.asin(math.sqrt(gamma))
        print(f"gamma: {gamma}\n")
        qc = Circuit(quantum_manager.__class__.__name__[:-7], 2)
        qc.ry(1,theta)
        qc.cx(0,1)
        qc.ry(1,theta)
        qc.cx(0,1)
        qc.measure(0)
        for key in keys:
            random_key = quantum_manager.new([1, 0])
            quantum_manager.run_circuit(qc, [random_key, key])