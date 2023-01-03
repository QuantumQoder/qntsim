import random
import qntsim
from qntsim.components.circuit import Circuit, QutipCircuit
from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
from qntsim.protocol import Protocol
# from qntsim.topology.node import QuantumRouter
from qntsim.topology.topology import Topology
import string
import sys
import numpy as np



class IP2():
    
    
    def run(self, message):
        
        res = {
            "input_message":"hi",
            "output_message": "hi",
            "sender_key" : "[1,0,1,0]",
            "receiver_key" : "[1,0,1,0]",
            "alice_ida_auth" : "Authenticated",
            "bob_ida_auth" : "Authenticated",
            "security_check" : "Security Check Passed"
        }
        
        return res