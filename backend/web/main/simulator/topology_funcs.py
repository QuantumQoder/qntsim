
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
from main.simulator.app.qsdc_teleportation import *
from main.simulator.app.single_photon_qd import *
from main.simulator.app.mdi_qsdc import * 
from main.simulator.app.ip2 import ip2_run
from main.simulator.app.utils import *
from random import shuffle
#from qntsim.library.protocol_handler.protocol_handler import Protocol
from qntsim.library.protocol import Protocol
from statistics import mean

def graph_topology(network_config_json):
    
    network_config_json,tl,network_topo = load_topology(network_config_json, "Qiskit")
    print(f'Making graph')
    graph = network_topo.get_virtual_graph()
    print(network_topo)
    return graph

def network_graph(network_topo,source_node_list,report):
    
    performance={}
    t=0
    timel ,fidelityl,latencyl,fc_throughl,pc_throughl,nc_throughl=[],[],[],[],[],[]

    while t < 20: ###Pass endtime of simulation instead of 20  

        fidelityl=calcfidelity(network_topo,source_node_list,t,fidelityl) 
        latencyl= calclatency(network_topo,source_node_list,t,latencyl)
        fc_throughl,pc_throughl,nc_throughl= throughput(network_topo,source_node_list,t,fc_throughl,pc_throughl,nc_throughl)
        t=t+1
        timel.append(t)
    for i in latencyl:
        if i>0:
            latency = i
    for i in fidelityl:
         if i>0:
            fidelity = i
    for i in fc_throughl:
        if i>0:
            through = i
    execution_time = 3
    performance["latency"]    = latency
    performance["fidelity"]   = fidelity
    performance["throughput"] = through
    performance["execution_time"] = execution_time
    # graph["throughput"]["fully_complete"]= fc_throughl  
    # graph["throughput"]["partially_complete"]= pc_throughl
    # graph["throughput"]["rejected"]= nc_throughl        #{fc_throughl,pc_throughl,nc_throughl}
    # graph["time"] = timel
    report["performance"] = performance
    print(report)
    return report

def eve_e91(network_config, sender, receiver, keyLength):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    trials=4
    while (trials>0):
        if keyLength<=0 or keyLength>30:
            return {"Error_Msg":"keyLength Should be Greater than 0 and less than 30 .Retry Again"}
        if keyLength<=30 and keyLength>0:
            #n=int((9*key_length)/2)
            n=int(8*keyLength)
            alice=network_topo.nodes[sender]
            bob = network_topo.nodes[receiver]
            e91=E91()
            alice,bob,source_node_list=e91.roles(alice,bob,n)
            tl.init()
            tl.run() 
            results=e91.eve_run(alice,bob,n)
            if keyLength<len(results["sender_keys"]):
                results["sender_keys"]=results["sender_keys"][:keyLength]
                results["receiver_keys"]=results["receiver_keys"][:keyLength] 
                results["sifted_keylength"]=keyLength 
            report={}
            report["application"]=results
            report=network_graph(network_topo,source_node_list,report)
            print(report)
            return report
        trials=trials-1    
    return {"Error_Msg":"Couldn't generate required length.Retry Again"}

def e91(network_config, sender, receiver, keyLength):
    print('network config', network_config)
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    print('network topo', network_topo)
    trials=4
    while (trials>0):
        if keyLength<=0 or keyLength>30:
            return {"Error_Msg":"keyLength Should be Greater than 0 and less than 30 .Retry Again"}

        if keyLength<=30 and keyLength>0:
            #n=int((9*key_length)/2)
            n=int(8*keyLength)
            alice=network_topo.nodes[sender]
            bob = network_topo.nodes[receiver]
            e91=E91()
            alice,bob,source_node_list=e91.roles(alice,bob,n)
            tl.init()
            tl.run()  
            results = e91.run(alice,bob,n)
            if keyLength<len(results["sender_keys"]):
                results["sender_keys"]=results["sender_keys"][:keyLength]
                results["receiver_keys"]=results["receiver_keys"][:keyLength] 
                results["sifted_keylength"]=keyLength 
            report={}
            report["application"]=results
            report=network_graph(network_topo,source_node_list,report)
            print(report)
            return report
        trials=trials-1
        
    return {"Error_Msg":"Couldn't generate required length.Retry Again"}

    
def e2e(network_config, sender, receiver, startTime, size, priority, targetFidelity, timeout):

    ##TODO: Integrate Network Graphs 
    req_pairs=[]
    
    network_config_json,tl,network_topo = load_topology(network_config, "Qiskit")
    tm=network_topo.nodes[sender].transport_manager
    tm.request(receiver, float(startTime),int(size), 20e12 , int(priority) ,float(targetFidelity), float(timeout) )
    req_pairs.append((sender,receiver))
    # tl.stop_time=30e12
    tl.init()
    tl.run()
    
    results ,source_node_list = get_res(network_topo,req_pairs)
    report={}
    report["application"]=results
    report=network_graph(network_topo,source_node_list,report)
    print(report)
    return report
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
    alice,bob,charlie,middlenode,source_node_list=ghz.roles(alice,bob,charlie,middlenode)
    tl.init()
    tl.run()  
    results = ghz.run(alice,bob,charlie,middlenode)
    report={}
    report["application"]=results
    report=network_graph(network_topo,source_node_list,report)
    print(report)
    return report

def ip1(network_config, sender, receiver, message):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    alice=network_topo.nodes[sender]
    bob = network_topo.nodes[receiver]
    ip1=IP1()
    alice,bob,source_node_list=ip1.roles(alice,bob,n=50)
    tl.init()
    tl.run()  
    results = ip1.run(alice,bob,message)
    report={}
    report["application"]=results
    report=network_graph(network_topo,source_node_list,report)
    print(report)
    return results
    
def ping_pong(network_config, sender, receiver, sequenceLength, message):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    if len(message)<=9:
        n=int(sequenceLength*len(message))
        alice=network_topo.nodes[sender]
        bob = network_topo.nodes[receiver]
        pp=PingPong()
        alice,bob,source_node_list=pp.roles(alice,bob,n)
        tl.init()
        tl.run() 
        pp.create_key_lists(alice,bob)
        results = pp.run(sequenceLength,message)
        report={}
        report["application"]=results
        report=network_graph(network_topo,source_node_list,report)
        print(report)
        return report
    else:
        print("message should be less than or equal to 9")
        return None
    
def qsdc1(network_config, sender, receiver, sequenceLength, key):
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    if (len(key)%2==0):
        
        n=int(sequenceLength*len(key))
        alice=network_topo.nodes[sender]
        bob = network_topo.nodes[receiver]
        print('alice bob', alice,bob,n)
        qsdc1=QSDC1()
        alice,bob,source_node_list=qsdc1.roles(alice,bob,n)
        print("alice,bob,source_node_list",alice,bob,source_node_list)
        tl.init()
        tl.run()  
        print('init and run', network_config_json)
        results = qsdc1.run(alice,bob,sequenceLength,key)
        report={}
        report["application"]=results
        report=network_graph(network_topo,source_node_list,report)
        print(report)
        return results
    else:
        print("key should have even no of digits")
        return None
    
def teleportation(network_config, sender, receiver, amplitude1, amplitude2):

    ##TODO: Integrate Network Graphs 
    print("teleportation running")
    network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    
    alice=network_topo.nodes[sender]
    bob = network_topo.nodes[receiver]
    tel= Teleportation()
    alice,bob,source_node_list=tel.roles(alice,bob)
    tl.init()
    tl.run()
    results = tel.run(alice,bob,amplitude1,amplitude2)
    report={}
    report["application"]=results
    report=network_graph(network_topo,source_node_list,report)
    print(report)
    return report

def qsdc_teleportation(network_config, sender, receiver, message, attack):
    
    
    # messages = {(1, 2):'hello world'}
    # print("sender, receiver, message, attack",sender, receiver, message, attack)
    messages = {(sender,receiver):message}
    attack=None
    topology = '/code/web/configs/2n_linear.json'
    protocol = Protocol(name='qsdc_tel', messages_list=[messages], label='00', attack=attack)
    protocol(topology=topology)
    print(protocol)
    # return protocol.recv_msgs_list[0], mean(protocol.mean_list)
    res={}
    res["input_message"] = message
    # res["input_message2"] = message2
    res["output_message"] = protocol.recv_msgs_list[0][1]
    # res["output_message2"] = protocol.recv_msgs_list[0][2]
    res["attack"] = attack
    res["error"] = mean(protocol.mean_list)
    report = {}
    report["application"] = res
    
    return report
    # network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    # alice=network_topo.nodes[sender]
    # bob = network_topo.nodes[receiver]
    # qsdc_tel = QSDCTeleportation()
    # alice,bob,source_node_list=qsdc_tel.roles(alice,bob,len(message))
    # tl.init()
    # tl.run()
    # results = qsdc_tel.run(alice,bob,message, attack)
    # report={}
    # report["application"]=results
    # report=network_graph(network_topo,source_node_list,report)
    # print(report)
    # return report
    # topology = json_topo(network_config)
    # # print('pwd', os.getcwd())
    # with open('network_topo.json','w') as fp:
    #     json.dump(topology,fp, indent=4)
    # # f = open('/code/web/network_topo.json')
    # topo = '/code/web/3node.json'
    # # print('message', [message], type(message),type([message]),attack)
    # # message = ['hello']
    # message = [message]
    # # print('message', message, type(message),type([message]),attack)
    # protocol = Protocol(platform='qntsim',
    #                     messages_list=[message],
    #                     topology=topo,
    #                     backend='Qutip',
    #                     label='00',
    #                     attack = attack
    #                     )

    # # This should be on results page
    # print('Received messages:', protocol.recv_msgs)
    # print('Error:', mean(protocol.mean_list))
    # error = mean(protocol.mean_list)
    # res ={}
    # res["input_message"] = message
    # res["output_message"] = protocol.recv_msgs[0][1]
    # res["attack"] = attack
    # res["error"] = error
    # report = {}
    # report["application"] = res
    
    # return report

def single_photon_qd(network_config, sender, receiver, message1, message2, attack):
    
    
    print('sender, receiver, message1, message2',sender, receiver, message1, message2,attack)
    messages = {(sender,receiver):message1,(receiver,sender):message2}
    # messages = {(1, 2):'hello', (2, 1):'world'}
    # attack=None
    topology = '/code/web/configs/singlenode.json'
    protocol = Protocol(name='qd_sp', messages_list=[messages], attack=attack)
    protocol(topology=topology)
    print("protocol.recv_msgs_list",protocol.recv_msgs_list)
    print("mean(protocol.mean_list)",mean(protocol.mean_list))
    res={}
    res["input_message1"] = message1
    res["input_message2"] = message2
    res["output_message1"] = protocol.recv_msgs_list[-1][1]
    res["output_message2"] = protocol.recv_msgs_list[-1][2]
    res["attack"] = attack
    res["error"] = protocol.mean_list[-1]
    report = {}
    report["application"] = res
    
    return report
    # return protocol.recv_msgs_list, mean(protocol.mean_list)
    
    
    # topology = json_topo(network_config)
    # with open('network_topo.json','w') as fp:
    #     json.dump(topology,fp, indent=4)
    # topo = '/code/web/singlenode.json'
    # message = [message1,message2]
    # print('message', message)
    # protocol = Protocol(platform='qntsim',
    #                 messages_list=[message],
    #                 topology=topo,
    #                 backend='Qutip',
    #                 attack=attack)

    # # This should be on results page
    # print('Received messages:', protocol.recv_msgs[0][1],protocol.recv_msgs[0].keys())
    # print('Error:', mean(protocol.mean_list))
    # error = mean(protocol.mean_list)
    # res ={}
    # res["input_message1"] = message1
    # res["input_message2"] = message2
    # res["output_message1"] = protocol.recv_msgs[0][1]
    # res["output_message2"] = protocol.recv_msgs[0][2]
    # res["attack"] = attack
    # res["error"] = error
    # report = {}
    # report["application"] = res
    
    # return report


def random_encode_photons(network:Network):
    print('inside random encode')
    node = network.network.nodes['n1']
    manager = network.manager
    basis = {}
    for info in node.resource_manager.memory_manager:
        if info.state=='RAW':
            key = info.memory.qstate_key
            base = randint(4)
            basis.update({key:base})
            q, r = divmod(base, 2)
            qtc = QutipCircuit(1)
            if r: qtc.x(0)
            if q: qtc.h(0)
            manager.run_circuit(qtc, [key])
        if info.index==2*(network.size+75): break
    
    print('output', network,basis)
    return network, basis

def authenticate_party(network:Network):
    manager = network.manager
    node = network.network.nodes['n1']
    keys = [info.memory.qstate_key for info in node.resource_manager.memory_manager[:2*network.size+150]]
    keys1 = keys[network.size-25:network.size]
    keys1.extend(keys[2*network.size:2*network.size+75])
    shuffle(keys1)
    keys2 = keys[2*network.size-25:2*network.size]
    keys2.extend(keys[2*network.size+75:])
    shuffle(keys2)
    # print(keys1)
    # print(keys2)
    all_keys = []
    outputs = []
    for keys in zip(keys1, keys2):
        all_keys.append(keys)
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.h(0)
        qtc.measure(0)
        qtc.measure(1)
        outputs.append(manager.run_circuit(qtc, list(keys)))
    err, counter = 0, 0
    for output in outputs:
        (key1, key2) = tuple(output.keys())
        base1 = basis.get(key1)
        base2 = basis.get(key2)
        out1 = output.get(key1)
        out2 = output.get(key2)
        if base1!=None!=base2 and base1//2==base2//2:
            counter+=1
            if (out1 if base1//2 else out2)!=(base1%2)^(base2%2): err+=1
    print(err/counter*100)
    
    return network, err/counter*100

def swap_entanglement(network:Network):
    node = network.network.nodes['n1']
    manager = network.manager
    e_keys = []
    for info0, info1 in zip(node.resource_manager.memory_manager[:network.size-25],
                            node.resource_manager.memory_manager[network.size:2*network.size-25]):
        qtc = QutipCircuit(2)
        qtc.cx(0, 1)
        qtc.h(0)
        qtc.measure(0)
        qtc.measure(1)
        keys = [info0.memory.qstate_key, info1.memory.qstate_key]
        print(keys)
        e_key = [k for key in keys for k in manager.get(key).keys if k!=key]
        output = manager.run_circuit(qtc, keys)
        c1, c2 = True, False
        for e_k, value in zip(e_key, output.values()):
            qtc = QutipCircuit(1)
            if c1 and value:
                qtc.x(0)
                c1, c2 = False, True
            elif c2 and value:
                qtc.z(0)
                c1, c2 = True, False
            manager.run_circuit(qtc, [e_k])
        e_keys.append(e_key)
    
    return e_keys

def mdi_qsdc(network_config, sender, receiver, message, attack):
    
    # network_config_json,tl,network_topo = load_topology(network_config, "Qutip")
    # # print('network config json', network_config_json)
    # mdi_qsdc = MdiQSDC()
    # mdi_qsdc.random_encode_photons()
    # # print("network Config", network_config)
    # topo = json_topo(network_config)
    # print("topo",topo)
    # results = mdi_qsdc.run(topo,message,attack)
    # print('results',results)
    topology = json_topo(network_config)
    print('pwd', os.getcwd())
    with open('network_topo.json','w') as fp:
        json.dump(topology,fp, indent=4)
    # f = open('/code/web/network_topo.json')
    topo = '/code/web/network_topo.json'
    # topo = code/backend/web/network_topo.json
    print("topo", topo)
    network = Network(topology=topo,
                messages=[message],
                label='00',
                size=lambda x:len(x[0])+100)
    
    print('network', network)
    network, basis = random_encode_photons(network=network)
    # network, err_prct = authenticate_party(network=network)
    network.dump('n1')
    print('network',network,basis)


def ip2(input_messages,ids,num_check_bits,num_decoy):
    report ={}
    print("input_messages,ids,num_check_bits,num_decoy",input_messages,ids,num_check_bits,num_decoy)
    topology = '/code/web/configs/2n_linear.json'
    results=ip2_run(topology,input_messages,ids,num_check_bits,num_decoy)
    # report["application"]=results
    # return report

    res={}
    res["input_message"] = list(input_messages.values())
    res["ids"] = ids
    res["check_bits"] = num_check_bits
    res["num_decoys"] = num_decoy
    res["output_msg"] = results[0]
    res["error"] = results[1]
    # report = {}
    report["application"] = res
    print('report',report)
    return report