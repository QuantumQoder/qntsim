


templist=['s0','s1','s2','s3','s4','s5','s6','s7','s8','s9']

fc_throughl,pc_throughl,nc_throughl=[],[],[]


def throughput(network_topo,t,templist):

    csuccess , cfullcomplete , cpartialcomplete , NC , ctotal , pc , inc , rc , ap = 0,0,0,0,0,0,0,0,0

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
    
    except ZeroDivisionError:
        fc_throughl.append(0)
        pc_throughl.append(0)
        nc_throughl.append(0)
        print(f'No Requests at {t} secs')          
                


def throughput_cal():
    import matplotlib.pyplot as plt

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

###every request src node appended only once to templist
###need to change that code
#nodelist=network_topo.get_nodes_by_type("QuantumRouter") 
#print('list',nodelist)
##for node in nodelist:
    #print("node",node.name)
#templist=['v0','v1','v2','v3','v4']

nodelist=['s0','s1','s2','s3','s4','s5','s6','s7','s8','s9']

def calctime(network_topo):
        
    time=[]

    for node in nodelist:

        src=node.name
        
        for ReqId,ResObj in network_topo.nodes[src].network_manager.requests.items():
            if ResObj.isvirtual:
                continue
            starttime=ResObj.start_time*1e-12
            
            maxtime=0
            print('Starttime', starttime,ResObj.initiator, ResObj.responder)
            #print('check',network_topo.nodes[src].resource_manager.reservation_id_to_memory_map.keys())
            if ReqId in network_topo.nodes[src].resource_manager.reservation_id_to_memory_map.keys():
                #memId=self.nodes[node].resource_manager.reservation_to_memory_map.get(ReqId)
                memId = network_topo.nodes[src].resource_manager.reservation_id_to_memory_map.get(ReqId)
                print(memId)
                
                for info in network_topo.nodes[src].resource_manager.memory_manager:
                    ###need to check these changes
                    if info.index in memId and info.entangle_time > maxtime and info.entangle_time != 20 and info.state =='ENTANGLED':
                        #print('ddd',info.entangle_time)
                        maxtime=info.entangle_time*1e-12

            latency=maxtime-starttime
            if latency > 0 :
                time.append(latency)
            
    if len(time)>0:
        avgtime=sum(time)/len(time)
        print('Average latency',avgtime)
    else:
        print('Exception error No entanglements')



def calcfidelity(network_topo):


    import math
    fid=[]

    for node in nodelist:

        src=node.name
        
        for ReqId,ResObj in network_topo.nodes[src].network_manager.requests.items():

            if ResObj.isvirtual:
                continue

            minfid =math.inf

            if ReqId in network_topo.nodes[src].resource_manager.reservation_id_to_memory_map.keys():

                memId = network_topo.nodes[src].resource_manager.reservation_id_to_memory_map.get(ReqId)
                print(memId)
                
                for info in network_topo.nodes[src].resource_manager.memory_manager:

                    if info.index in memId and info.state == 'ENTANGLED' and info.fidelity<minfid:
                        minfid= info.fidelity

            if minfid!=math.inf:
                fid.append(minfid)

    if len(fid)>0:

        avgfid=sum(fid)/len(fid)
        print("avgfid",avgfid)
        return avgfid
    else:
        print("exception error no entangled states")



