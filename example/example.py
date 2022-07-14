import qntsim
from qntsim.kernel.timeline import Timeline
from qntsim.topology.topology import Topology
import matplotlib.pyplot as plt
import numpy as np
from pyvis.network import Network
import webbrowser
import matplotlib.pyplot as plt

#random.seed(0)
network_config = "/home/bhanusree/Desktop/QNTv1/QNTSim/example/network_topology copy.json" #give path to yopur netwrok topology



tl = Timeline(22e12)
network_topo = Topology("network_topo", tl)
network_topo.create_random_topology(10)




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
    for node in topology.get_nodes_by_type("QuantumRouter"):
        pass
        # node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        # node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)





#node1='v0'
#node2='v2'
#nm=network_topo.nodes[node1].network_manager
#nm.create_request(node1,node2, start_time=2e12, end_time=10e12, memory_size=3, target_fidelity= 0.9,priority=1,tp_id=0)


"""node1='v0'
node2='v3'
nm=network_topo.nodes[node1].network_manager
nm.create_request(node1,node2, start_time=3e12, end_time=10e12, memory_size=3, target_fidelity= 0.8,priority=1,tp_id=0)"""


"""
node1='v0'
node2='v2'
tm = network_topo.nodes[node1].transport_manager
tm.request(node2, start_time=1e12 ,size=6, end_time=20e12,priority=0,target_fidelity=0.5,timeout=4e12)
#self, responder, start_time, size,end_time, priority, target_fidelity,timeout

"""
#node1='v0'
#node2='v2'
##tm = network_topo.nodes[node1].transport_manager
#tm.request(node2, start_time=1e12 ,size=6, end_time=20e12,priority=0,target_fidelity=0.5,timeout=4e12)


"""node1='v3'
node2='v4'

tm = network_topo.nodes[node1].transport_manager
tm.request(node2, start_time=2e12 ,size=3, end_time=20e12,priority=1, target_fidelity=0.5,timeout=3e12)"""




n,k,lamda=10,6,5
lis=[]
startnode=[]
li=[]
pairs=[]
indexes=0
totalrequests=0
timesteps=[]
def dynamicrequest(n):
    
    global totalrequests
    for t in range(2,16,1):
        timesteps.append(t)
        print(f'**Requests at {t} secs**')
        req=np.random.poisson(lam=lamda, size=None)
        req=5
        print('Requests number', req)
        totalrequests = totalrequests + req
        eprs=np.random.randint(5,6, size=req)
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
            # tm.request(node2, start_time=t*1e12 , end_time=20e12, memory_size=eprs[k],priority,target_fidelity=0.5,timeout)
            #tm.request(node2,t*1e12,eprs[k],(t+10)*1e12,1,0.6 ,2e12)
            tm.request(node2,t*1e12,eprs[k],22e12,1,0.7,4e12)
            k+=1
            li.append((node1,node2,t))
            startnode.append(network_topo.nodes[node1])
            lis.append(node1)
        #throughput1(lis,t)
    return

dynamicrequest(n)





tl.init()
tl.run()


#nm.create_request(node1,'v3', start_time=12e12, end_time=23e12, memory_size=3, target_fidelity= 0.8,priority=1,tp_id=0)

# tp_id  <----> protocolobj          Transport protocol map 

# req_id <-----> reqobj              Request map 

# tp_id  <----> req_id               Network map   /// for Reject or Approved requests


print(" pairs" ,li)

def throughputtemp(t):

    csuccess , cfullcomplete , cpartialcomplete , NC , ctotal , pc , inc , rc , ap = 0,0,0,0,0,0,0,0,0
    #print(li)

    for pairs in li:

        src=pairs[0]
        dest=pairs[1]
        time=pairs[2]

        #if time == t:
            #ctotal +=1
            #flag=False
           
            
        for ReqId,ResObj in network_topo.nodes[src].network_manager.requests.items():
            #print('iiiiii',ReqId, ResObj.status)
            temp=False
            tsize=0

            if ResObj.start_time>=t*1e12 and ResObj.start_time< (t+1)*1e12 and ResObj.responder==dest and time:
                ctotal+=1
                print("\n") 
                print("requests ,src ,resobj id ,dst",src,dest, ResObj.initiator,ResObj.responder, ResObj.start_time,ReqId,network_topo.nodes[src].network_manager.requests.items())
                print("network map example ,src ,resobj id ",src,dest,ReqId,network_topo.nodes[src].network_manager.networkmap)
                print("example check",ReqId in network_topo.nodes[src].network_manager.networkmap.keys())
                if ReqId in network_topo.nodes[src].network_manager.networkmap.keys():
                    
                    #ctotal+=1
                    
                    if ResObj.isvirtual:
                        continue

                    #if ResObj.start_time*1e-12 != t:
                        #continue
                
                    if ResObj.status=='PARTIALCOMPLETE':
                        pc +=1

                #elif ResObj.status=='INCOMPLETE':
                    #inc +=1
                
                    elif ResObj.status=='REJECT':
                        rc +=1
                    
                    elif ResObj.status=='APPROVED':
                        ap +=1
                        
            

                
                print("through put map , src ",src,network_topo.nodes[src].resource_manager.reservation_id_to_memory_map)
                
                #reserved memory id list of request

                """
                memId=network_topo.nodes[src].resource_manager.reservation_id_to_memory_map.get(ReqId)

                #print('mem id', memId)
                
                if memId != None:
                    for info in network_topo.nodes[src].resource_manager.memory_manager:
                    #print('iy',info)
                        if info.index in memId and info.state == 'ENTANGLED' and info.remote_node == dest:

                            print('info index   remote node   state ',src, info.remote_node, info.state)
                            
                            tsize+=1
                            flag=True
                            temp =True

                tp_id  = ResObj.tp_id

                #tp_id = network_topo.nodes[src].network_manager.networkmap[ReqId][0]
                 
                parent_request = network_topo.nodes[src].transport_manager.transportprotocolmap.get(tp_id)

                print("cal throughput sizes", tp_id , ResObj.id , parent_request.size , tsize )
 
                if temp:
                    csuccess +=1
                    #break
                    if tsize==parent_request.size:
                        cfullcomplete +=1
                    else :
                        cpartialcomplete +=1

                else:
                    NC +=1
                    print("\n")
                """
                
    print("\n")
    print(f'At {t} secs : success: {csuccess},total :{ctotal}, FC:{cfullcomplete},PC:{cpartialcomplete}, NC:{NC},fail: {ctotal-csuccess} ,pc:{pc},fc:{ap},nc:{rc}')
    
    try:
        #thru=(csuccess)/(ctotal)
        #print(f'Throughput = {thru*100}%')
        pc_through=(pc)/(ctotal)
        nc_through=(rc)/(ctotal)
        fc_through=(ap)/(ctotal)
        print(f' pc_through:{pc_through*100}%,nc_through:{nc_through*100}%,fc_through:{fc_through*100}%')

        #through.append(thru*100)
    except ZeroDivisionError:
        print(f'No Requests at {t} secs')          
                



templist=['v0','v1','v2','v3','v4','v5','v6','v7','v8','v9']

fc_throughl,pc_throughl,nc_throughl=[],[],[]


def throughput(t):

    csuccess , cfullcomplete , cpartialcomplete , NC , ctotal , pc , inc , rc , ap = 0,0,0,0,0,0,0,0,0
    #print(li)

    for src in templist:

        src=src
        #if time == t:
            #ctotal +=1
            #flag=False
           
            
        for ReqId,ResObj in network_topo.nodes[src].network_manager.requests.items():
            #print('iiiiii',ReqId, ResObj.status)
            temp=False
            tsize=0

            if ResObj.start_time>=t*1e12 and ResObj.start_time< (t+1)*1e12 :
                ctotal+=1
                print("\n") 
                print("requests ,src ,resobj id ,dst",src, ResObj.initiator,ResObj.responder, ResObj.start_time,ReqId,network_topo.nodes[src].network_manager.requests.items())
                print("network map example ,src ,resobj id ",src,ReqId,network_topo.nodes[src].network_manager.networkmap)
                print("example check",ReqId in network_topo.nodes[src].network_manager.networkmap.keys())
                if ReqId in network_topo.nodes[src].network_manager.networkmap.keys():
                    
                    #ctotal+=1
                    
                    if ResObj.isvirtual:
                        continue

                    #if ResObj.start_time*1e-12 != t:
                        #continue
                
                    if ResObj.status=='PARTIALCOMPLETE':
                        pc +=1

                #elif ResObj.status=='INCOMPLETE':
                    #inc +=1
                
                    elif ResObj.status=='REJECT':
                        rc +=1
                    
                    elif ResObj.status=='APPROVED':
                        ap +=1
                                        
                print("through put map , src ",src,network_topo.nodes[src].resource_manager.reservation_id_to_memory_map)
                
                #reserved memory id list of request

                
    print("\n")
    print(f'At {t} secs : success: {csuccess},total :{ctotal}, FC:{cfullcomplete},PC:{cpartialcomplete}, NC:{NC},fail: {ctotal-csuccess} ,pc:{pc},fc:{ap},nc:{rc}')
    
    try:
        #thru=(csuccess)/(ctotal)
        #print(f'Throughput = {thru*100}%')
        pc_through=(pc)/(ctotal)
        pc_throughl.append(pc_through*100)
        nc_through=(rc)/(ctotal)
        nc_throughl.append(nc_through*100)
        fc_through=(ap)/(ctotal)
        fc_throughl.append(fc_through*100)
        print(f' pc_through:{pc_through*100}%,nc_through:{nc_through*100}%,fc_through:{fc_through*100}%')
    
        #through.append(thru*100)
    except ZeroDivisionError:
        fc_throughl.append(0)
        pc_throughl.append(0)
        nc_throughl.append(0)
        print(f'No Requests at {t} secs')          
                


def throughput_cal():
  
    y=[]
    
    plt.xlabel('Time in seconds')
    plt.ylabel('Throughput')

    plt.title('Throughput')
    for t in range(21):
        fc_through,pc_through,nc_through=0.0,0.0,0.0
        print("\n")
        throughput(t)
        print("fc,pc,nc",fc_through,pc_through,nc_through)
        y.append(t)
    print("values",fc_throughl,pc_throughl,nc_throughl,y)
    plt.plot(y,fc_throughl, label = "full")
    plt.plot(y,pc_throughl, label = "partial")
    plt.plot(y,nc_throughl, label = "incomplete")   
    #plt.legend()
    #ax1.set_ylim(-1,max(reqstotal)+5)
    #cdax2.set_ylim(-1,max(reqstotal)+5)
    plt.show()
    
       
###GRAPH PLOTTING

# For printing memories
print("v0 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v0"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

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

print("v5 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v5"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("v6 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v6"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("v7 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v7"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("v8 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v8"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("v9 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["v9"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))



throughput_cal()

