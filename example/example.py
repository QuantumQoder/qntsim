from turtle import color
import qntsim
from qntsim.kernel.timeline import Timeline 
Timeline.DLCZ=True
Timeline.bk=False
from qntsim.topology.topology import Topology
import matplotlib.pyplot as plt
import numpy as np
from pyvis.network import Network
import webbrowser
import matplotlib.pyplot as plt

#random.seed(0)
network_config = "/home/bhanusree/Desktop/QNTv1/QNTSim-Demo/QNTSim/example/4node.json" #give path to yopur netwrok topology

#DLCZ=True

tl = Timeline(22e12,"Qiskit")
network_topo = Topology("network_topo", tl)
network_topo.create_random_topology(10,network_config)




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
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)





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
        req=2
        print('Requests number', req)
        totalrequests = totalrequests + req
        eprs=np.random.randint(2,3, size=req)
        print('EPR Pairs', eprs)
        
        for i in range(n):
            for j in range(i+1,n):
                pairs.append((i,j))
        
        count=len(pairs)
        indexes=np.random.randint(count,size=req)
        print([pairs[i] for i in indexes])
        k=0
        for i in indexes:
            node1='s' + str(pairs[i][0])
            node2='s' + str(pairs[i][1])
            tm = network_topo.nodes[node1].transport_manager
            # tm.request(node2, start_time=t*1e12 , end_time=20e12, memory_size=eprs[k],priority,target_fidelity=0.5,timeout)
            #tm.request(node2,t*1e12,eprs[k],(t+10)*1e12,1,0.6 ,2e12)
            tm.request(node2,t*1e12,eprs[k],22e12,1,0.5,4e12)
            k+=1
            li.append((node1,node2,t))
            startnode.append(network_topo.nodes[node1])
            lis.append(node1)
        #throughput1(lis,t)
    return

dynamicrequest(n)



print("requests pairs" ,li)

tl.init()
tl.run()


#nm.create_request(node1,'v3', start_time=12e12, end_time=23e12, memory_size=3, target_fidelity= 0.8,priority=1,tp_id=0)

# tp_id  <----> protocolobj          Transport protocol map 

# req_id <-----> reqobj              Request map 

# tp_id  <----> req_id               Network map   /// for Reject or Approved requests

     
templist=['s0','s1','s2','s3','s4','s5','s6','s7','s8','s9']

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
                #print("requests ,src ,resobj id ,dst",src, ResObj.initiator,ResObj.responder, ResObj.start_time,ReqId,network_topo.nodes[src].network_manager.requests.items())
                #print("network map example ,src ,resobj id ",src,ReqId,network_topo.nodes[src].network_manager.networkmap)
                #print("example check",ReqId in network_topo.nodes[src].network_manager.networkmap.keys())
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

    ctotal1=pc+ap+rc           
    print("\n")
    print(f'At {t} secs ctotal:{ctotal} pc:{pc},fc:{ap},nc:{rc}')
    
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
    plt.plot(y,fc_throughl,color='g', label = 'full')
    plt.plot(y,pc_throughl,color='b', label = 'partial')
    plt.plot(y,nc_throughl,color='r', label = 'incomplete')   
    plt.legend()
    plt.show()
    
       
###GRAPH PLOTTING

# For printing memories
print("s0 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s0"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s1 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s1"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s2 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s2"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s3 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s3"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s4 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s4"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s5 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s5"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s6 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s6"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s7 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s7"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s8 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s8"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

print("s9 memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
for info in network_topo.nodes["s9"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                        str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))



throughput_cal()

