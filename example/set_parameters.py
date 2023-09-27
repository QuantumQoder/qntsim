from qntsim.kernel.timeline import Timeline
from qntsim.kernel.quantum_manager import QuantumManager, QuantumManagerKet
from qntsim.protocol import Protocol
# from qntsim.topology.node import QuantumRouter
from qntsim.topology.topology import Topology
from qntsim.network_management.reservation import Reservation
from qntsim.resource_management.memory_manager import MemoryInfo
import json

def set_parameters(topology: Topology):
   
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 1
    #MEMO_FIDELITY = 0.9349367588934053
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

  
    DETECTOR_EFFICIENCY = 1
    #DETECTOR_EFFICIENCY = 0.2
    DETECTOR_COUNT_RATE = 5e7
    #DETECTOR_RESOLUTION = 70
    DETECTOR_RESOLUTION = 100
    for node in topology.get_nodes_by_type("BSMNode"):
        node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

def create_architecture(tl : Timeline, network_config : str):  
    network_topo = Topology("network_topo", tl)
    network_topo.load_config(network_config)
    set_parameters(network_topo)
    return network_topo

