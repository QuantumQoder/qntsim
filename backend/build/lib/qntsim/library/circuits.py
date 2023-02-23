from ..components.circuit import QutipCircuit

def bell_type_state_analyzer(num_qubits:int):
    qtc = QutipCircuit(num_qubits)
    for i in range(num_qubits-1, 0, -1): qtc.cx(0, i)
    qtc.h(0)
    for i in range(num_qubits): qtc.measure(i)
    
    return qtc