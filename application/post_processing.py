import qntsim
from qntsim.kernel.timeline import Timeline
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
# from qntsim.topology.node import QuantumRouter
from qntsim.network_management.reservation import Reservation
from qntsim.resource_management.memory_manager import MemoryInfo
import numpy as np

network_config = "network_topology.json"

def request_entanglements(sender, receiver, n=50):
    sender.transport_manager.request(receiver.owner.name,5e12,n,10e12,0,.7,5e12)
    print()

def roles(sender, receiver, n):
    request_entanglements(sender, receiver, n)

def print_memories(node):
    print(f"{node} memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in node.resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


def check_phi_plus(state):
    assert(len(state) == 4)

    if abs(state[0]*np.sqrt(2) - 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) - 1)  < 1e-5:
        return True

    elif abs(state[0]*np.sqrt(2) + 1)  < 1e-5 and state[1] == 0 and state[2] == 0 and abs(state[3]*np.sqrt(2) + 1)  < 1e-5:
        return True

    else : return False


### -------------XXXXXXX-------------
### This method filters out all the wrongly entangled states
### and return a list of keys which are correctly entangled
### to phi_+ = |00> + |11>
### -------------XXXXXXX-------------
def create_phi_plus_entanglement(node):
    entangled_keys = []
    qm_node=node.timeline.quantum_manager

    for info in node.resource_manager.memory_manager:

        key=info.memory.qstate_key
        state=qm_node.get(key)

        #Filtering out unentangeled qubits
        if(len(state.keys) == 1) : continue

        #Filtering out phi_minus, created randomly, from phi_plus
        if(not check_phi_plus(state.state)):continue

        #Check that state is indeed phi_+
        print(state)

        entangled_keys.append(key)

    return entangled_keys