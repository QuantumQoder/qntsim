from enum import Enum

from ..components import qntsim_network, qiskit_network

class Network(Enum):
    qiskit = qiskit_network.Network
    qntsim = qntsim_network.Network
