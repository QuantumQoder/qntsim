from qntsim.kernel.timeline import Timeline
from qntsim.topology.topology import Topology
import networkx as nx
import matplotlib.pyplot as plt
import json
#network_config = "/home/aman/SeQUeNCe/example/network_topology.json"

# g = nx.Graph(((1,2), (2,3),  (3,4), (5,6)))
# nx.draw(g)
# plt.show()

n = 10
m = 4

G = nx.barabasi_albert_graph(n, m)
nx.draw(G)


nodes = [{
        "name":str(i), 
        "type":"QuantumRouter", 
        "memo_size":25
        } for i in G.nodes()]

qconnections = [{
        "node1": str(i),
        "node2": str(j),
        "attenuation": 1e-5,
        "distance": 500
        } for i,j in G.edges()]

cchannels_table = { "type": "RT",
                    "labels": [str(i) for i in range(n)],
                    "table": [[1e9 if not i==j else 0 for j in range(n)] for i in range(n)]}


network_topoplogy = {"nodes":nodes, "qconnections":qconnections, "cchannels_table": cchannels_table}


with open('network_topology.json', 'w') as fp:
    json.dump(network_topoplogy, fp, indent = 4)
    
network_config = "/home/aman/SeQUeNCe/example/network_topology.json"

tl = Timeline(2e12)
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)

def set_parameters(topology: Topology):
    # set memory parameters
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 0.95
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

    # set detector parameters
    DETECTOR_EFFICIENCY = 1
    DETECTOR_COUNT_RATE = 5e7
    DETECTOR_RESOLUTION = 100
    for node in topology.get_nodes_by_type("BSMNode"):
        node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
        
    # set entanglement swapping parameters
    SWAP_SUCC_PROB = 0.95
    SWAP_DEGRADATION = 0.9
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
    # set quantum channel parameters
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ


set_parameters(network_topo)


node1 = "0"
node2 = str(n-1)
nm = network_topo.nodes[node1].network_manager
nm.request(node2, start_time=1e12, end_time=10e12, memory_size=10, target_fidelity=0.9)

tl.init()
tl.run()

# print(node1, "memories")
# print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
for info in network_topo.nodes[node1].resource_manager.memory_manager:
    # print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                                         str(info.fidelity), str(info.entangle_time * 1e-12)))

plt.savefig("img.png")