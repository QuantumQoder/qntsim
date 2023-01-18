import numpy as np
from qutip import Qobj

from qntsim.components.circuit import x_gate, y_gate, z_gate

from ..components.network import Network
from ..attacks.attacks import Attack

class Channel:
    def __init__(self, parameter, network:Network, attack:Attack):
        self.parameter = parameter
        self.network = network
    
    def depolarizing_channel(self, receiver:int):
        parameter = self.parameter
        value0 = np.sqrt(1-3*parameter/4)
        value1 = np.sqrt(parameter/4)
        identity = np.identity(2)
        operators = [value0*Qobj(identity), value1*x_gate(), value1*y_gate(), value1*z_gate()]
        network = self.network
        nodes = network.get_nodes_by_type('EndNode')
        op_list = [identity]*len(nodes)
        manager = network.manager
        for info in nodes[receiver].resource_manager.memory_manager:
            if info.state=='ENTANGLED':
                key = info.memory.qstate_key
                state = manager.get(key)
                rho = Qobj(np.kron(state.state, state.state))
                for operator in operators:
                    op = op_list.copy()
                    op[receiver] = operator
                    operator = op[0]
                    rho_prime = operator*rho*operator.dag()
                    for i in range(1, len(nodes)): operator = np.kron(operator, op[i])
                    rho_prime+=operator*rho*operator.dag()
                state.state = np.array(rho_prime)
    
    def amplitude_damping(self, receiver:int):
        parameter = self.parameter
        operators = [Qobj([[1, 0], [0, np.sqrt(1-parameter)]]), Qobj([[0, np.sqrt(parameter)], [0, 0]])]
        network = self.network
        nodes = network.get_nodes_by_type('EndNode')
        op_list = [np.identity(2)]*len(nodes)
        manager = network.manager
        for info in nodes[receiver].resource_manager.memory_manager:
            if info.state=='ENTANGLED':
                key = info.memory.qstate_key
                state = manager.get(key)
                rho = Qobj(np.kron(state.state, state.state))
                for operator in operators:
                    op = op_list.copy()
                    op[receiver] = operator
                    operator = op[0]
                    rho_prime = operator*rho*operator.dag()
                    for i in range(1, len(nodes)): operator = np.kron(operator, op[i])
                    rho_prime+=operator*rho*operator.dag()
                state.state = np.array(rho_prime)