from ..components.circuit import QutipCircuit

def bsm_circuit():
    qtc = QutipCircuit(2)
    qtc.cx(0, 1)
    qtc.h(0)
    qtc.measure(0)
    qtc.measure(1)
    
    return qtc