

import string
from main.simulator.constants import *


def load_topology(network_config_json, backend):
    from qntsim.kernel.timeline import Timeline
    Timeline.DLCZ=False
    Timeline.bk=True
    from qntsim.topology.topology import Topology
    #from qntsim.topology.node import force_import
    #force_import("bk")
    print(f'Loading Topology: {network_config_json}')
    
    tl = Timeline(20e12,backend)
    # print('Timeline', tl)

    network_topo = Topology("network_topo", tl)
    network_topo.load_config_json(network_config_json)
    all_pair_dist, G = network_topo.all_pair_shortest_dist()
    # print('all pair distance', all_pair_dist, G)

    # print(f'Topology Graph: {network_topo}')

    
    return network_config_json,tl,network_topo
    
def get_nodes(nodes):
    
    
    service_node,end_node =[],{}
    for node in nodes:
        if node.get("Type") == "service":
            service_node.append(node.get("Name"))
        else:
            pass
    return service_node,end_node


def get_qconnections(quantum_connections):
    
    conn, qconnections = {},[]
    for connections in quantum_connections:
        for nodes in connections.get("Nodes"):
            conn["nodes1"] = nodes[0]
            conn["nodes2"] = nodes[1]
            conn["attenuation"] = conn.get("Attenuation")
            conn["distance"] = conn.get("Distance")
        qconnections.append(conn)
    
    return qconnections
            
def to_matrix(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]
                     
def get_cconnections(classical_connections):
    
    cchannels_table ={}
    cchannels_table["type"] ="RT"
    nodes = []
    for conn in classical_connections:
        for node in conn.get("Nodes"):
            nodes.append(*node)
            
    nodes = list(set(nodes))
    cchannels_table["labels"] = nodes
    table = []
    for node1 in nodes:
        for node2 in nodes:
            if node1 == node2:
                table.append(0)
            else:
                table.append(1000000000)
    
    cchannels_table["table"] = to_matrix(table, len(nodes))
    
    return cchannels_table
 
            
def refactor_topo(topology):
    
    nodes = topology.get("nodes")
    quantum_connections = topology.get("quantum_connections")
    classical_connections = topology.get("classical_connections")
    
    network_json = {}
    service_node,end_node = get_nodes(nodes)
    
    network_json["service_node"] = service_node
    network_json["end_node"] = end_node
    network_json["qconnections"] = qconnections
    network_json["cchannels_table"] = service_node