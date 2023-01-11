from numpy import pi
from numpy.random import randint, uniform
from qiskit import QuantumRegister, ClassicalRegister

class Attack:
    @staticmethod
    def entangle_and_measure(network_obj, **kwargs):
        qubits = kwargs.get('nodes')
        circuits = network_obj.circuits
        for circuit in circuits:
            qr = QuantumRegister(len(qubits), 'ancilla')
            cr = ClassicalRegister(len(qubits)-circuit.num_clbits, 'c')
            circuit.add_register(qr, cr)
            circuit.cx(qubits, qr)
            circuit.measure(qr, circuit.clbits)
            circuit.barrier()
    
    @staticmethod
    def denial_of_service(network_obj, **kwargs):
        qubits = kwargs.get('nodes')
        circuits = network_obj.circuits
        for circuit in circuits:
            for qubit in qubits:
                if randint(2):
                    circuit.u(2*uniform()*pi,
                              2*uniform()*pi,
                              2*uniform()*pi,
                              qubit)
            circuit.barrier()
    
    @staticmethod
    def intercept_and_resend(network_obj, **kwargs):
        qubits = kwargs.get('nodes')
        circuits = network_obj.circuits
        for circuit in circuits:
            circuit.add_register(ClassicalRegister(len(qubits)-circuit.num_clbits-1, 'c'))
            for qubit in qubits:
                base = randint(2)
                if base: circuit.h(qubit)
                circuit.measure(qubit, ~-qubit)
                if base: circuit.h(qubit)
            circuit.barrier()