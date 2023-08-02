import itertools
import json
import math
import random
import sys
from random import choice, random

import matplotlib.pyplot as plt
import numpy as np
import qntsim
# from Noise import noise, NoiseModel2, Error
from qntsim.communication import Error, noise
from qntsim.communication import noise_model as NoiseModel2
from qntsim.components.circuit import QutipCircuit
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
from qntsim.kernel.timeline import Timeline
from qntsim.network_management.reservation import Reservation
from qntsim.protocol import Protocol
from qntsim.resource_management.memory_manager import MemoryInfo
# from qntsim.topology.node import QuantumRouter
from qntsim.topology.topology import Topology
from qutip import *
from qutip.qip.circuit import *
from qutip.qip.gates import *
from qutip.qip.operations import *
from qutip.qobj import Qobj

Timeline.bk = True
Timeline.DLCZ = False

topology = {
    "nodes": [
        {
            "Name": "a",
            "Type": "service",
            "noOfMemory": 500,
        },
        {"Name": "b", "Type": "end", "noOfMemory": 500},
    ],
    "quantum_connections": [{"Nodes": ["a", "b"], "Attenuation": 1e-5, "Distance": 70}],
    "classical_connections": [
        {"Nodes": ["a", "a"], "Delay": 0, "Distance": 1000},
        {"Nodes": ["a", "b"], "Delay": 1000000000, "Distance": 1000},
        {"Nodes": ["b", "a"], "Delay": 1000000000, "Distance": 1000},
        {"Nodes": ["b", "b"], "Delay": 1000000000, "Distance": 1000},
    ],
}
_parameters = "parameters.json"

tl = Timeline(10e12, "Qutip")
net_topo = Topology("qsdc", tl)
net_topo.load_config_json(topology)

# with open(_parameters, 'r') as file:
#     data = json.load(file)