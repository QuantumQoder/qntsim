import numpy as np
from qiskit.circuit import QuantumCircuit,Parameter, qpy_serialization

import io
import json
import base64

class composer:
    def __init__(self,circuit_name):
        self.circuit_name=circuit_name
    
    def add_controlled_gate(self, name, layer, index, qubits):
        target_gate = layer[qubits[1]]
        target_gate_name = layer[qubits[1]]['value']
        self.ignore.append([index, qubits[1]])
        name = name + target_gate_name
        params = target_gate.pop("params", None)
        if params:
            self.add_parametarized_gate(name, qubits, params, par_name=self.circuit_name)
        else:
            g = getattr(self.qc, name)
            g(qubits[0], qubits[1])
        
        
    def add_parametarized_gate(self, name, qubits, params, par_name=None):
        angles=[]
        for angle_name, angle_params in params.items():
            if angle_params["variable"] == "True":
                self.variational_params+=1
                angle =  Parameter(par_name+str(self.variational_params))
            else:
                angle = float(angle_params["value"])
            angles.append(angle)
        g = getattr(self.qc, name)
        g(*angles,*qubits)

        
    def get_circuit(self,circuit, flag="optimization"):
        self.qc = QuantumCircuit(len(circuit))
        self.variational_params=0
        self.ignore=[]
        for index, layer in enumerate(zip(*circuit.values())):
            for q in range(len(layer)):
                gate = layer[q]
                name = gate.get("value")
                if name == "c":
                    values = [item.get('value') for item in layer]
                    taget_index = next(i for i, value in enumerate(values) if value not in ['i', 'c'])
                    self.add_controlled_gate(name, layer, index, [q, taget_index])
                else:
                    if name != 'i':
                        if [index, q] not in self.ignore:
                            params = gate.pop("params", None)
                            if params:
                                self.add_parametarized_gate(name, [q], params, par_name=self.circuit_name)
                            else:
                                g = getattr(self.qc, name)
                                g(q)

        if flag == "visualization":              
            self.qc.draw(filename="image.png")
            image_file = open("image.png", "rb")
            image_data = image_file.read()
            output = json.dumps({
                'circuits': base64.b64encode(image_data).decode()
            })
            return output