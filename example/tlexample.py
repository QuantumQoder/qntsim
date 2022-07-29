
from qntsim.kernel.timeline import Timeline
from qntsim.topology.topology import Topology
from tabulate import tabulate
#random.seed(0)
network_config = "4node.json"

n,k,lamda=10,6,40

tl = Timeline(4e12,"Qiskit")
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)
# network_topo.create_random_topology(n,network_config)



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
        
   
    SWAP_SUCC_PROB = 0.9
    SWAP_DEGRADATION = 0.99
    # for node in topology.get_nodes_by_type("QuantumRouter"):
    #     node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
    #     node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)

# Create scenarios for resource reservation failure.
# Scenarios for overlapping requests with different start times and end times. 




# tl.time=3e12
# node1='v0'
# node2='v2'
# nm=network_topo.nodes[node1].network_manager
# nm.createvirtualrequest(node2, start_time=2e12, end_time=10e12, memory_size=3, target_fidelity= 0.5)


node1='a'
node2='s4'
nm=network_topo.nodes[node1].network_manager
nm.createvirtualrequest(node1, node2, start_time=2e12, end_time=10e12, memory_size=5, target_fidelity=0.5)



tl.init()
tl.run()

table=[]
print('a memories')
for info in network_topo.nodes["a"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'a',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# print('Tbale', table)
print(tabulate(table, headers=['Index','Source node', 'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('b memories')
for info in network_topo.nodes["b"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'b',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s1 memories')
for info in network_topo.nodes["s1"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s1',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s2 memories')
for info in network_topo.nodes["s2"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s2',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# # print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s3 memories')
for info in network_topo.nodes["s3"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s3',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# # print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s4 memories')
for info in network_topo.nodes["s4"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s4',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# # print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
tl.stop_time=10e12




node1='a'
node2='b'
tm=network_topo.nodes[node1].transport_manager
tm.request(node2, start_time=5e12,size=5, end_time=10e12, priority=0 , target_fidelity= 0.5, timeout=2e12) 

# node1='a'
# node2='b'
# tm=network_topo.nodes[node1].transport_manager
# tm.request(node2, start_time=5e12,size=5, end_time=10e12, priority=0 , target_fidelity= 0.6, timeout=2e12) 

# node1='v2'
# node2='v3'
# tm=network_topo.nodes[node1].transport_manager
# tm.request(node2, start_time=6e12,size=5, end_time=10e12, priority=0 , target_fidelity= 0.7, timeout=2e12) 



# node1='v0'
# node2='v2'
# tm=network_topo.nodes[node1].transport_manager
# tm.request(node2, start_time=5e12,size=5, end_time=10e12, priority=0 , target_fidelity= 0.7, timeout=2e12)






# tm.request(node2,3e12,5,10e12,1,.7,2e12) 
# tm.request(node2,5e12,5,10e12,0,.7,5e9)


# virt_graph=network_topo.get_virtual_graph()
# network_topo.plot_graph(virt_graph)




# tl.init()
tl.run()


table=[]
print('a memories')
for info in network_topo.nodes["a"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'a',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# print('Tbale', table)
print(tabulate(table, headers=['Index','Source node', 'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('b memories')
for info in network_topo.nodes["b"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'b',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s1 memories')
for info in network_topo.nodes["s1"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s1',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s2 memories')
for info in network_topo.nodes["s2"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s2',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# # print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s3 memories')
for info in network_topo.nodes["s3"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s3',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# # print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s4 memories')
for info in network_topo.nodes["s4"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s4',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# # print('Tbale', table)
print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))

# table=[]
# print('s3 memories')
# for info in network_topo.nodes["s3"].resource_manager.memory_manager:
#     if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
#         table.append([info.index,'s3',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
# print('Tbale', table)
# print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))

'''
tranmap={}
netmap={}
reqmap={}
table2=[]
def getmaps():
    for i in range(0,5):
        node='v'+str(i)
        for tpid,TpObj in network_topo.nodes[node].transport_manager.transportprotocolmap.items():
            print('tpid',tpid)
            tranmap[tpid]=TpObj
        for netid,[tpd,status] in network_topo.nodes[node].network_manager.networkmap.items():
            netmap[netid]=[tpd,status]
        for reqid,resobj in network_topo.nodes[node].network_manager.requests.items():
            reqmap[reqid]=resobj
        table2.append([tpid, reqid, TpObj.owner.name, TpObj.other, TpObj.retry, TpObj.priority, status])
getmaps()
print(tranmap)
print(netmap)
print(reqmap)
table3=sorted(table2, key=itemgetter(0))
print(table3)
table4=(list(map(list,set(map(tuple,table3)))))
print(table4)
# table3=list(set(table3))
print(tabulate(table4, headers=['Transport ID', 'Network ID' , 'Source Node', 'Entanglement With' ,'Retry count','Priority','Status'], tablefmt='grid'))
table2=[]
def outputmaps():
    for i in range(0,5):
        node='v'+str(i)
        for reqid,resobj in network_topo.nodes[node].network_manager.requests.items():
            
            tp_id=network_topo.nodes[node].network_manager.networkmap.get(reqid)[0]
            Status=network_topo.nodes[node].network_manager.networkmap.get(reqid)[1]
            TpObj=network_topo.nodes[node].transport_manager.transportprotocolmap.get(tp_id)
            table2.append([tp_id, reqid, TpObj.owner.name, TpObj.other, TpObj.retry, TpObj.priority, Status])
            file = open("requestlog.txt","w")
            file.write(" reqid: " + str(reqid) + "," + "-- transport protocol request-- "  + " Status: " +str(Status)+ "," + " tpid: " + str(tp_id) + "," + " source: " + str(TpObj.owner.name) + "," + " starttime: " + str(TpObj.starttime) + "," + " dest: "+str(TpObj.other)+","+" endtime: " + str(TpObj.endtime)+ "," + " priority: "+str(TpObj.priority)+ ","+" retry: "+str(TpObj.retry)+","+" reqcount: "+str(TpObj.reqcount)+"\n")
            file.write(" reqid: " + str(reqid) + "," + "-- reservation  request-- " + " reservation-request initiator: "+ str(resobj.initiator) + "," +" node with which entanglement is requested :"+str(resobj.responder)+"," + " simulation time at which entanglement should be attempted: "+str(resobj.start_time)+","+" simulation time at which resources may be released: "+ str(resobj.end_time)+","+"fidelity:"+str(resobj.fidelity)+"," + " status: "+str(resobj.status)+"," +" isvirtual: "+str(resobj.isvirtual)+"," +" memory_size: "+str(resobj.memory_size)+"," +" priority: "+str(resobj.priority))
            # table2.append([tp_id, reqid, TpObj.owner.name, TpObj.other, TpObj.starttime ,TpObj.endtime, TpObj.retry, TpObj.priority, Status])
            #file.write("reqid:"+reqid+"Status:",Status,"tpid:",tp_id, "source:",TpObj.owner.name, "starttime:",TpObj.starttime,"dest:",TpObj.other,"endtime:",TpObj.endtime,"priority:",TpObj.priority,"retry:",TpObj.retry,"reqcount:",TpObj.reqcount)
            #file.write("reqid:",reqid," reservation request initiator node:",resobj.initiator,"node with which entanglement is requested :",resobj.responder,"time at which entanglement should be attempted:",resobj.start_time,"simulation time at which resources may be released:", resobj.end_time,"fidelity:",resobj.fidelity,"status:",resobj.status,"isvirtual:",resobj.isvirtual,"memory_size:",resobj.memory_size,"priority:",resobj.priority)
            file.close
            # print("reqid:",reqid,"Status:",Status,"tpid:",tp_id, "source:",TpObj.owner.name, "starttime:",TpObj.starttime,"dest:",TpObj.other,"endtime:",TpObj.endtime,"priority:",TpObj.priority,"retry:",TpObj.retry,"reqcount:",TpObj.reqcount)
            # print("reqid:",reqid," reservation request initiator node:",resobj.initiator,"node with which entanglement is requested :",resobj.responder,"time at which entanglement should be attempted:",resobj.start_time,"simulation time at which resources may be released:", resobj.end_time,"fidelity:",resobj.fidelity,"status:",resobj.status,"isvirtual:",resobj.isvirtual,"memory_size:",resobj.memory_size,"priority:",resobj.priority)
outputmaps()
table3=sorted(table2, key=itemgetter(0))
print(tabulate(table3, headers=['Transport ID', 'Network ID' , 'Source Node', 'Entanglement With' ,'Retry count','Priority','Status'], tablefmt='grid'))
'''
