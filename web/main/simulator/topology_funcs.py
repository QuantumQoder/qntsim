from contextlib import nullcontext
from pyvis.network import Network
from tokenize import String
from main.simulator.helpers import *
from qntsim.topology.topology import Topology
from tabulate import tabulate
from pprint import pprint
import pandas as pd
import numpy as np
from main.simulator.app.e91 import *
from main.simulator.app.e2e import *
from main.simulator.app.ghz import *
from main.simulator.app.ip1 import *
from main.simulator.app.ping_pong import *
from main.simulator.app.qsdc1 import *
from main.simulator.app.teleportation import *

def graph_topology(network_config_json):
    
    tl,network_topo = load_topology(network_config_json)
    print(f'Making graph')
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



def fetchE91Config(network_config):
    json_data = open(network_config)   
    data1 = json.load(json_data) # deserialises it

    responseData = {
        "sender": data1["service_node"] +["a", "b"],
        "receiver": data1["service_node"] +["a", "b"],
    }
    
    return responseData

def e91(network_config, sender, receiver, keyLength):
    tl,network_topo = load_topology(network_config)
    if keyLength<50 and keyLength>0:
        n=int((9*keyLength)/2)
        alice=network_topo.nodes[sender]
        bob = network_topo.nodes[receiver]
        e91=E91()
        alice,bob=e91.roles(alice,bob,n)
        tl.init()
        tl.run()  
        results = e91.run(alice,bob,n)
        return results
    else:
        print("key length should be between 0 and 50")
        return None

def e2e(network_config, sender, receiver, startTime, size, priority, targetFidelity, timeout):
    req_pairs=[]
    
    tl,network_topo = load_topology(network_config)
    tm=network_topo.nodes[sender].transport_manager
    tm.request(receiver, float(startTime),int(size), 20e12 , int(priority) ,float(targetFidelity), float(timeout) )
    req_pairs.append((sender,receiver))
    # tl.stop_time=30e12
    tl.init()
    tl.run()
    
    results = get_res(network_topo,req_pairs)
    return results