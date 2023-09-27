from qiskit.circuit import QuantumCircuit, Parameter
from copy import deepcopy
import numpy as np
from qiskit.opflow.state_fns import CircuitStateFn
from qiskit.opflow.primitive_ops import CircuitOp
from scipy.optimize import minimize
from qiskit.algorithms import optimizers
# from qiskit_machine_learning.algorithms import VQC
from qiskit.utils.quantum_instance import QuantumInstance


class VQA:
    def __init__(self,ansatz, num_layers, initialization=None, expectation=None):
        self.initialization=initialization
        self.ansatz = ansatz
        self.variational_params=self.ansatz.parameters.data
        
        self.num_layers=num_layers
        self.num_qubits=self.ansatz.num_qubits
        self.expectation=expectation
    def reshape_params(self,params):
        return np.array(params).reshape(self.num_layers,len(self.variational_params))
    def create_circuit(self, params):
        if self.initialization:
            self.initial_variational_params=self.initialization.parameters.data
            self.vqa_circuit = self.initialization
            for p in range(len(self.initial_variational_params)):
                    self.vqa_circuit=self.vqa_circuit.bind_parameters({self.initial_variational_params[p]:params.pop(p)})
            self.vqa_circuit.barrier()
        else:
            self.vqa_circuit = QuantumCircuit(self.num_qubits)
        params = self.reshape_params(params)
        for l in range(self.num_layers):
            layer=deepcopy(self.ansatz)
            for p in range(len(self.variational_params)):
                layer=layer.bind_parameters({self.variational_params[p]:params[l][p]})
            self.vqa_circuit = self.vqa_circuit&(layer)
            self.vqa_circuit.barrier()
        return self.vqa_circuit
    def get_exp_value(self):
        op = CircuitOp(self.expectation)
        psi = CircuitStateFn(self.vqa_circuit)
        return psi.adjoint().compose(op).compose(psi).eval().real
    
    def cost_fun(self, params):
        global current_cost
        circuit = self.create_circuit(params)
        current_cost = self.get_exp_value()
        return current_cost

    def optimization(self, args,initial_params):
        #args=(), method=None, jac=None, hess=None, hessp=None, bounds=None, constraints=(), tol=None, callback=None,
        iteration_results = []

    # Define a custom callback function to collect results
        def callback_function(xk):
            iteration_results.append(current_cost)
        result = minimize(self.cost_fun, x0=initial_params,  method=args.pop("optimizer", "COBYLA"), callback=callback_function, options={"maxiter":args.pop("maxiter", 1000), "disp":args.pop("disp", True)}, **args)
        return result, iteration_results
    
    
    
class QAOA(VQA):
    def __init__(self, initialization, cost,mixer, num_layers, expectation=None):
        self.cp=len(cost.parameters.data)
        self.mp=len(mixer.parameters.data)
        anstaz=cost&mixer
        super().__init__(anstaz, num_layers, initialization,expectation)
    def reshape_params(self,params):
        new_params=[]
        for n in range(0, len(params), 2):
            if n + 1 < len(params):
                new_params = new_params + [params[n]]*self.cp + [params[n+1]]*self.mp
        return np.array(new_params).reshape(self.num_layers,len(self.variational_params))
    
    
    

