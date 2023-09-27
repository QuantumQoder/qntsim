ch = input("Choose a protocol (0 for Barret Kok, 1 for DLCZ): ")

if ch == '0':
    from src.kernel.timeline import Timeline
    from src.topology.topology import Topology
else:
    from src_DLCZ.kernel.timeline import Timeline
    from src_DLCZ.topology.topology import Topology
import networkx as nx
import matplotlib.pyplot as plt
import json
network_config = ".\\network_topology.json"

# network_config = ".\\starlight.json"

n = 5
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


# with open('network_topoplogy.json', 'w+') as fp:
#     json.dump(network_topoplogy, fp, indent = 4)

tl = Timeline(6e12)
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)

def set_parameters(topology: Topology):
    # set memory parameters
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 0.9
    MEMO_FIDELITY = 0.9
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
    SWAP_SUCC_PROB = 0.9
    SWAP_DEGRADATION = 0.9
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
    # set quantum channel parameters
    ATTENUATION = 1e-5
    QC_FREQ = 2e4
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ


set_parameters(network_topo)


node0 = "v0"
node1 = "v1"
node2 = "v2"
node3 = "v3"
node4 = "v4"
# nm = network_topo.nodes[node1].network_manager
# nm.request(node4, start_time=1e12, end_time=15e12, memory_size=5, target_fidelity=0.7, priority = 1)
# nm = network_topo.nodes[node0].network_manager
# nm.request(node4, start_time=2e12, end_time=5e12, memory_size=1, target_fidelity=0.7, priority = 0, tp_id = 5e9)
# nm = network_topo.nodes[node1].network_manager
# nm.request(node4, start_time=2e12, end_time=5e12, memory_size=5, target_fidelity=0.7, priority = 1)

# tm=network_topo.nodes[node0].transport_manager
# tm.request(node4,2e12,5,6e12,0,5e9)

# tm=network_topo.nodes[node2].transport_manager
# tm.request(node3,5e12,7,6e12,0,5e9)

# node1='v0'
# node2='v4'
# tm=network_topo.nodes[node1].transport_manager
# tm.request(node2,4e12,1,6e12,1,5e9)
 
# node1='v1'
# node2='v3'
tm=network_topo.nodes[node1].transport_manager
tm.request(node4,1e12,5,6e12,0,5e9) 
# tm.request(node2,3e12,1,6e12,0,5e9) 



tl.init()
# import time 
# time.sleep(5)
# # print('\n\n\n\n\nDone with initializing sim')
tl.run()

for node in [node0, node1, node2, node3, node4]:
    # print(node, "memories")
    # print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes[node].resource_manager.memory_manager:
        # print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12)))
    # print("=====================================================================")

# # print(node1, "memories")
# # print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
# for info in network_topo.nodes[node1].resource_manager.memory_manager:
#     # print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
#                                          str(info.fidelity), str(info.entangle_time * 1e-12)))

plt.savefig("img.png")