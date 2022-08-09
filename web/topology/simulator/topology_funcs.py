from topology.simulator.helpers import *
from qntsim.topology.topology import Topology
from tabulate import tabulate
from pprint import pprint

def graph_topology(network_config):


    network_topo = load_topology(network_config)
    graph = network_topo.get_virtual_graph()
    
    return graph

def tlexample(network_config):
    network_topo = load_topology(network_config)
    set_parameters(network_topo)
    
    return network_topo