from enum import Enum

from qntsim.library.components import qntsim_network, qiskit_network

class Network(Enum):
    qiskit = qiskit_network.Network
    qntsim = qntsim_network.Network
