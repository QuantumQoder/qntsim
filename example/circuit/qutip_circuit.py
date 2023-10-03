from qntsim.kernel.circuit import QutipCircuit

def create_ghz_states(num_qubits: int) -> None:
    circuit = QutipCircuit(num_qubits)
    circuit.h(0)
    for i in range(1, num_qubits):
        circuit.cx(0, i)
    print(circuit)

if __name__ == "__main__":
    create_ghz_states(2)
    create_ghz_states(3)
    create_ghz_states(4)