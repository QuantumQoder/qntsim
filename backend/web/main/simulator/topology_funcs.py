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
    
    network_config_json,tl,network_topo = load_topology(network_config_json, "Qiskit")
    print(f'Making graph')
    graph = network_topo.get_virtual_graph()
    print(network_topo)
    return graph

def e91(network_config, sender, receiver, keyLength):
    network_config_json,tl,network_topo = load_topology(network_config, "Qiskit")
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
    
    network_config_json,tl,network_topo = load_topology(network_config, "Qiskit")
    tm=network_topo.nodes[sender].transport_manager
    tm.request(receiver, float(startTime),int(size), 20e12 , int(priority) ,float(targetFidelity), float(timeout) )
    req_pairs.append((sender,receiver))
    # tl.stop_time=30e12
    tl.init()
    tl.run()
    
    results = get_res(network_topo,req_pairs)
    #graph = network_topo.get_virtual_graph()
    
    """results={
        "parameter":network_config_json,
        "graph":graph,
        "results":results
    }"""
    return results

def ghz(network_config, endnode1, endnode2, endnode3, middlenode):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    alice=network_topo.nodes[endnode1]
    bob = network_topo.nodes[endnode2]
    charlie=network_topo.nodes[endnode3]
    middlenode=network_topo.nodes[middlenode]
    ghz= GHZ()
    alice,bob,charlie,middlenode=ghz.roles(alice,bob,charlie,middlenode)
    tl.init()
    tl.run()  
    results = ghz.run(alice,bob,charlie,middlenode)
    return results

def ip1(network_config, sender, receiver, message):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    alice=network_topo.nodes[sender]
    bob = network_topo.nodes[receiver]
    ip1=IP1()
    alice,bob=ip1.roles(alice,bob,n=50)
    tl.init()
    tl.run()  
    results = ip1.run(alice,bob,message)
    return results
    
def ping_pong(network_config, sender, receiver, sequenceLength, message):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    if len(message)<=9:
        n=int(sequenceLength*len(message))
        alice=network_topo.nodes[sender]
        bob = network_topo.nodes[receiver]
        pp=PingPong()
        alice,bob=pp.roles(alice,bob,n)
        tl.init()
        tl.run() 
        pp.create_key_lists(alice,bob)
        results = pp.run(sequenceLength,message)
        return results
    else:
        print("message should be less than or equal to 9")
        return None
    
def qsdc1(network_config, sender, receiver, sequenceLength, key):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    if (len(key)%2==0):
        
        n=int(sequenceLength*len(key))
        alice=network_topo.nodes[sender]
        bob = network_topo.nodes[receiver]
        qsdc1=QSDC1()
        alice,bob=qsdc1.roles(alice,bob,n)
        tl.init()
        tl.run()  
        results = qsdc1.run(alice,bob,sequenceLength,key)
        return results
    else:
        print("key should have even no of digits")
        return None
    
def teleportation(network_config, sender, receiver, amplitude1, amplitude2):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    
    alice=network_topo.nodes[sender]
    bob = network_topo.nodes[receiver]
    tel= Teleportation()
    alice,bob=tel.roles(alice,bob)
    tl.init()
    tl.run()
    results = tel.run(alice,bob,amplitude1,amplitude2)
    return results