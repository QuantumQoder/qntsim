from tokenize import String
from topology.simulator.helpers import *
from qntsim.topology.topology import Topology
from tabulate import tabulate
from pprint import pprint
import pandas as pd

def graph_topology(network_config):
    tl,network_topo = load_topology(network_config)
    graph = network_topo.get_virtual_graph()
    
    return graph

def tlexample(network_config: String, node1: String, node2: String):
    tl,network_topo = load_topology(network_config)
    set_parameters(network_topo)
    tm=network_topo.nodes[node1].transport_manager
    tm.request(node2, start_time=5e12,size=5, end_time=10e12, priority=0 , target_fidelity= 0.5, timeout=2e12) 
    tl.stop_time=10e12
    tl.init()
    tl.run()
    memoryDict = {}

    table=[]
    print('\na memories')
    for info in network_topo.nodes["a"].resource_manager.memory_manager:
        if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
            table.append([info.index,'a',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
    # print(tabulate(table, headers=['Index','Source node', 'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
    memoryDict["a"] = pd.DataFrame(table, columns=MEMORY_COLS)
    
    print(memoryDict["a"])
    table=[]
    print('\nb memories')
    for info in network_topo.nodes["b"].resource_manager.memory_manager:
        if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
            table.append([info.index,'b',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
    # print('\nTbale', table)
    # print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
    memoryDict["b"] = pd.DataFrame(table, columns=MEMORY_COLS)
    print(memoryDict["b"])
    table=[]

    print('\ns1 memories')
    for info in network_topo.nodes["s1"].resource_manager.memory_manager:
        if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
            table.append([info.index,'s1',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
    # print('\nTbale', table)
    # print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
    memoryDict["s1"] = pd.DataFrame(table, columns=MEMORY_COLS)
    print(memoryDict["s1"])
    table=[]
    print('\ns2 memories')
    for info in network_topo.nodes["s2"].resource_manager.memory_manager:
        if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
            table.append([info.index,'s2',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
    # # print('\nTbale', table)
    # print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
    memoryDict["s2"] = pd.DataFrame(table, columns=MEMORY_COLS)
    print(memoryDict["s2"])
    table=[]
    print('\ns3 memories')
    for info in network_topo.nodes["s3"].resource_manager.memory_manager:
        if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
            table.append([info.index,'s3',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
    # # print('\nTbale', table)
    # print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
    memoryDict["s3"] = pd.DataFrame(table, columns=MEMORY_COLS)
    print(memoryDict["s3"])
    
    table=[]
    print('\ns4 memories')
    for info in network_topo.nodes["s4"].resource_manager.memory_manager:
        if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
            table.append([info.index,'s4',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
    # # print('\nTbale', table)
    # print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))

    memoryDict["s4"] = pd.DataFrame(table, columns=MEMORY_COLS)
    print(memoryDict["s4"])

    # print(memoryDict)
    # memoryDictHTML = ""
    # for key, value in memoryDict.items():
    #     memoryDictHTML += "<h2>" + key + " memories</h2>"
    #     memoryDictHTML += value

    return memoryDict