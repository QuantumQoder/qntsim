from enum import Enum

from qntsim.library.components import qntsim_network

class Network(Enum):

    qntsim = qntsim_network.Network
