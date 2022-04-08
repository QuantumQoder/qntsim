import qntsim
from numpy import random
from qntsim.kernel.timeline import Timeline
from qntsim.topology.topology import Topology
from qntsim.network_management.reservation import Reservation
import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from pyvis.network import Network
import webbrowser

#random.seed(0)
network_config = "/home/aman/SeQUeNCe/example/test_topology1.json"

n,k,lamda=10,6,5

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


def print_memory(network_topo, node, string = None):
    flag = False                           
    print("\nnode", node, string)
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes[node].resource_manager.memory_manager:
        if info.fidelity > 0:
            flag = True
            print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12), str(info.state)))
    if not flag:
        print("No entangled memory")



pairs=[]
indexes=0
vstartnode=[]
def uniformRandomVirtGraph(n,k):
    for i in range(n):
        for j in range(i+1,n):
            pairs.append((i,j))

    print(pairs)
    count=len(pairs)
    indexes=np.random.randint(count,size=k)
    print([pairs[i] for i in indexes])
    for i in indexes:
        node1='v' + str(pairs[i][0])
        node2='v' + str(pairs[i][1])
        nm=network_topo.nodes[node1].network_manager
        nm.createvirtualrequest(node2, start_time=2e12, end_time=20e12, memory_size=1, target_fidelity= 0.5)
        vstartnode.append(node1)


# uniformRandomVirtGraph(n,k)


tl.init()
tl.run()

for node in vstartnode:
    print_memory(network_topo,node, "After Virtual Links")

tl.stop_time=20e12

lis=[]
startnode=[]
li=[]
pairs=[]
indexes=0
totalrequests=0
timesteps=[]
def dynamicrequest(n):
    
    global totalrequests
    for t in range(6,20,2):
        timesteps.append(t)
        print(f'**Requests at {t} secs**')
        req=np.random.poisson(lam=lamda, size=None)
        print('Requests number', req)
        totalrequests = totalrequests + req
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
            node1='v' + str(pairs[i][0])
            node2='v' + str(pairs[i][1])
            tm = network_topo.nodes[node1].transport_manager
            # tm.request(node2, start_time=t*1e12 , end_time=20e12, memory_size=eprs[k], target_fidelity=0.5)
            tm.request(node2,t*1e12,eprs[k],20e12,1,2e12)
            k+=1
            li.append((node1,node2,t))
            startnode.append(network_topo.nodes[node1])
            lis.append(node1)
        #throughput1(lis,t)
    return

dynamicrequest(n)



# virt_graph=network_topo.get_virtual_graph()
# #network_topo.plot_graph(virt_graph)
# #network_topo.draw_graph(virt_graph)
# tl.run()
"""
try:
    tl.run()

except AttributeError:
    pass
"""
through=[]
def throughput(t):
    csuccess, ctotal = 0,0
    #print(li)

    for pairs in li:
        src=pairs[0]
        dest=pairs[1]
        time=pairs[2]
        if time == t:
            ctotal +=1
            flag=False
            for ReqId,ResObj in network_topo.nodes[src].network_manager.requests.items():
                #print('iiiiii',ReqId, ResObj.status)
                if ResObj.isvirtual:
                    continue
                if ResObj.start_time*1e-12 != t:
                    continue
                #if ReqId in network_topo.nodes[src].resource_manager.reservation_to_memory_map.keys():
                #print(ResObj.initiator, ResObj.responder,ResObj.start_time)
                memId=network_topo.nodes[src].resource_manager.reservation_to_memory_map.get(ReqId)
                #print('mem id', memId)
                if memId != None:
                    for info in network_topo.nodes[src].resource_manager.memory_manager:
                        #print('iy',info)
                        if info.index in memId and info.state == 'ENTANGLED' and info.remote_node == dest:
                            #print('info index   remote node   state   ',src, info.remote_node, info.state)
                            csuccess +=1
                            flag=True
                            break
                if flag:
                    break

    print(f'At {t} secs : success: {csuccess} fail: {ctotal-csuccess}')
    try:
        thru=(csuccess)/(ctotal)
        print(f'Throughput = {thru*100}%')
        through.append(thru*100)
    except ZeroDivisionError:
        print(f'No Requests at {t} secs')



reqtores={}
def getmaps():
    for i in range(0,n):
        node='v'+str(i)
        print(node)
        for ReqId,ResObj in network_topo.nodes[node].network_manager.requests.items():
            reqtores[ReqId]=ResObj

getmaps()
reqstotal=[]
reqscomp=[]

def statusthroughput(t):
    csuccess, ctotal = 0,0
    for ReqId,ResObj in reqtores.items():
        #print(ReqId,ResObj.status)
        if ResObj.isvirtual:
            continue
        if ResObj.start_time*1e-12 == t:
            ctotal+=1
            
            if ResObj.status == 'APPROVED':
                csuccess+=1
                
    reqstotal.append(ctotal)
    reqscomp.append(csuccess)
    print(f'At {t} secs : success: {csuccess} fail: {ctotal-csuccess}')
    thru=(csuccess)/(ctotal)
    print(f'Throughput = {thru*100}%')
 
    #print('reqs',reqs)
    #print(ureqs)

def calculate():   
    uniquenode=list(set(startnode))  
    for node in uniquenode:
        print_memory(network_topo,node.name, "After Requests")
    for time in timesteps:
        throughput(time)
        statusthroughput(time)
    # fid=Topology.calcfidelity(network_topo)
    print('Average Fidelity', fid)
    print('Total Requests', totalrequests)
    # time=Topology.calctime2(network_topo,uniquenode)
    #time=Topology.calctime(network_topo,li)
    #Topology.throughput(network_topo, li)
    
   

calculate()

plt.plot(timesteps, through)
plt.title(f'Node: {n}  Virtual links: {k}  Lamda: {lamda}')
plt.xlabel('Time(secs)')
plt.ylabel('Throughput(%)')
plt.ylim(-10,110)
plt.savefig('graph.png')



fig,ax1=plt.subplots()
ax1.plot(timesteps,reqstotal, color='red',label='Total Requests')
ax1.set_xlabel('Timesteps(secs)')
ax1.set_ylabel('Requests')
ax1.set_xticks(range(min(timesteps),max(timesteps)+2,1))
#ax1.set_yticks(range(-5,max(reqstotal)+5,5))

ax2=ax1.twinx()
#ax2.set_yticks(range(-1,max(reqstotal)+5,5))
ax2.plot(timesteps,reqscomp, color='blue',label='Request completed')
#ax2.set_ylabel('Requests Completed')
#plt.show()
ax1.set_ylim(-1,max(reqstotal)+5)
ax2.set_ylim(-1,max(reqstotal)+5)
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax1.set_title('Total requests created and completed at every timestep')
fig.savefig('g.png')
