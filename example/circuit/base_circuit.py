from qntsim.kernel.circuit import Circuit


def create_ghz_states(num_qubits: int) -> None:
    circuit1 = Circuit("qiskit", num_qubits)
    circuit2 = Circuit("qutip", num_qubits)
    circuit1.h(0)
    circuit2.h(0)
    for i in range(1, num_qubits):
        circuit1.cx(0, i)
        circuit2.cx(0, i)
    circuit1.measure_all()
    print(circuit1)
    print(circuit2)
    circuit1 + circuit2
    print(circuit1)

if __name__ == "__main__":
    create_ghz_states(2)
    create_ghz_states(3)
    create_ghz_states(4)