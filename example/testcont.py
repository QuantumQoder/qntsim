import qntsim
from numpy import random
from qntsim.kernel.timeline import Timeline
from qntsim.topology.topology import Topology
from qntsim.topology.node import *
import math, sys
import networkx as nx
import matplotlib.pyplot as plt


def cont():
    #random.seed(0)
    network_config = "/home/aman/SeQUeNCe/example/test_topology1.json"

    n,k=5,3

    tl = Timeline(4e12)
    network_topo = Topology("network_topo", tl)
    #network_topo.load_config(network_config)
    network_topo.create_random_topology(n)



    def set_parameters(topology: Topology):
    
        MEMO_FREQ = 2e3
        MEMO_EXPIRE = 0
        MEMO_EFFICIENCY = 1
        MEMO_FIDELITY = 0.9349367588934053
        for node in topology.get_nodes_by_type("QuantumRouter"):
            node.memory_array.update_memory_params("frequency", MEMO_FREQ)
            node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
            node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
            node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

    
        DETECTOR_EFFICIENCY = 0.9
        DETECTOR_COUNT_RATE = 5e7
        DETECTOR_RESOLUTION = 100
        for node in topology.get_nodes_by_type("BSMNode"):
            node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
            node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
            node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
            
    
        SWAP_SUCC_PROB = 0.90
        SWAP_DEGRADATION = 0.99
        for node in topology.get_nodes_by_type("QuantumRouter"):
            node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
            node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
            
    
        ATTENUATION = 1e-5
        QC_FREQ = 1e11
        for qc in topology.qchannels:
            qc.attenuation = ATTENUATION
            qc.frequency = QC_FREQ

    set_parameters(network_topo)

    #print(json.loads(json.dumps(network_topo.all_pair_shortest_distance)))

    pairs=[]
    indexes=0

    def uniformRandomVirtGraph(n,k):
        for i in range(n):
            for j in range(i+1,n):
                pairs.append((i,j))

        print(pairs)
        count=len(pairs)
        indexes=np.random.randint(count,size=k)
        print(indexes)
        print([pairs[i] for i in indexes])
        for i in indexes:
            node1='v' + str(pairs[i][0])
            node2='v' + str(pairs[i][1])
            nm=network_topo.nodes[node1].network_manager
            nm.createvirtualrequest(node2, start_time=2e12, end_time=20e12, memory_size=1, target_fidelity= 0.5)


    uniformRandomVirtGraph(n,k)

    tl.init()
    tl.run()

    tl.stop_time=20e12

    print("v1 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v1"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

    print("v2 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v2"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


    print("v3 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v3"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


    print("v4 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v4"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))



    print("v0 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v0"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))



    pairs=[]
    indexes=0
    def dynamicrequest(n):
        
        #reqs=np.random.randint(2,5)
        #print('Request count',reqs)
        for t in range(5,19,2):
            print(f'**Requests at {t} secs**')
            req=np.random.poisson(lam=2, size=None)
            print('Requests number', req)
            eprs=np.random.randint(1,5, size=req)
            print('EPR Pairs', eprs)
            
            for i in range(n):
                for j in range(i+1,n):
                    pairs.append((i,j))
            
            count=len(pairs)
            indexes=np.random.randint(count,size=req)
            print([pairs[i] for i in indexes])
            k=0
            for i in indexes:
                #start_time=reqtime[k] * 1e12
                node1='v' + str(pairs[i][0])
                node2='v' + str(pairs[i][1])
                nm = network_topo.nodes[node1].network_manager
                nm.request(node2, start_time=t*1e12 , end_time=20e12, memory_size=eprs[k], target_fidelity=0.5)
                k+=1


    dynamicrequest(n)


    virt_graph=network_topo.get_virtual_graph()
    network_topo.plot_graph(virt_graph)

    #tl.init()
    tl.run()


    print("v1 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v1"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

    print("v2 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v2"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


    print("v3 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v3"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))


    print("v4 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v4"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))



    print("v0 memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["v0"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
   

runtimes=[]

def timeit_wrapper(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        return_val = func(*args, **kwargs)
        end = time.perf_counter()
        runtimes.append(end - start)
        return return_val
    return wrapper


def run():
    #sys.stdout = open(os.devnull, 'w')
    retval = cont()
    #sys.stdout = sys.__stdout__
    return retval


sim_trial=1
list_avg_physical_ent_time=[]
list_avg_virtual_ent_time=[]
list_avg_physical_fidelity=[]
list_avg_virtual_fidelity=[]

print(f'Running for {sim_trial} trials.')
for i in range(sim_trial):
    
