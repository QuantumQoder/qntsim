from qntsim.kernel.timeline import Timeline 
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.topology.topology import Topology
from tabulate import tabulate
from e91 import E91


def load_topo(path,backend):

   tl = Timeline(20e12,backend)
   network_topo = Topology("network_topo", tl)
   network_topo.load_config(path)
   return tl,network_topo


def get_res(network_topo,req_pairs):

      #table=[]
      for pair in req_pairs:
         print('src ',pair[0])
         table=[]
         src=pair[0]
         for info in network_topo.nodes[src].resource_manager.memory_manager:
            if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
               table.append([info.index,src,info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
         print(tabulate(table, headers=['Requestid','Index','Source node', 'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
         table=[]
         print('dst ',pair[1])
         dst=pair[1]
         for info in network_topo.nodes[dst].resource_manager.memory_manager:
            if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
               table.append([info.index,dst,info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])
         print(tabulate(table, headers=['Requestid','Index','Source node', 'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
      
def set_parameters(topology:Topology):
   
   MEMO_FREQ = 2e4
   MEMO_EXPIRE = 0
   MEMO_EFFICIENCY = 1
   MEMO_FIDELITY = 0.9349367588934053
   for node in topology.get_nodes_by_type("EndNode"):
      node.memory_array.update_memory_params("frequency", MEMO_FREQ)
      node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
      node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
      node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)
   
   for node in topology.get_nodes_by_type("ServiceNode"):
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

   ATTENUATION = 1e-5
   QC_FREQ = 1e11
   for qc in topology.qchannels:
      qc.attenuation = ATTENUATION
      qc.frequency = QC_FREQ


def input_e91(e91_state):



   print("\n ----E91 QKD--- ")   
   print("\nEnter command for help page $:--help")
   print("\nEnter command to Load topology $: load_topology <path_to_json_file>")
   print("\nEnter command to run E91 $:run_e91 <sender> <receiver> <9k/2>")
   print("\nEnter command to exit Simulation $:exit")


   while True:
      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      args=tokens[1:]

      if command=='load_topology'and (e91_state==0 or e91_state==1) :
         if len(args)==1:
            print('\nLoaded topology')
            path=args[0]
            tl,network_topo=load_topo(path,"Qiskit")
            e91_state=1
         else:
            print("Path to config file is not given")
      
      elif command=='run_e91'and e91_state==1:
         if len(args)==3:
            sender=args[0]
            receiver=args[1]
            keys=int(args[2])
            n=int((9*keys)/2)
            alice=network_topo.nodes[sender]
            bob = network_topo.nodes[receiver]
            e91=E91()
            alice,bob=e91.roles(alice,bob,n)
            tl.init()
            tl.run()  
            e91.runE91(alice,bob,n)
         else:
            print("incorrect sender or receiver or no.of.keys") 

      elif command=='exit':
         break

      elif command=='--help':
         print("\nCommand to Load topology $: load_topology <path_to_json_file>")
         print("\n$:load_topology config.json")
         print("\n\nCommand to run E91 $:run_e91 <sender> <receiver> <9k/2>")
         print("\n$:run_e91 endnode1 endnode2 112")

      else:
         print("Enter correct command")




def input_entanglements(e2e_state):
   
   print("\nEnter command for help page $:--help")
   print("\nEnter command for backend $:backend Qiskit/backend Qutip")
   print("\nEnter command to Load topology $: load_topo <path_to_json_file>")
   print("\nEnter command to create requests $: entanglement_req  <src node-name> <dst node-name> <start_time> <size> <end_time> <priority> <target_fidelity> <timeout>")
   print("\nEnter command to run simulation $: run_sim ")    
   print("\nEnter command to get results $: get_res ")
   print("\nEnter command to exit Simulation $:exit")
   while True:
      
      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      args=tokens[1:]

      if command=='backend'and (e2e_state==0 or e2e_state==1):

         if args[0]=='Qiskit':
            backend="Qiskit"
            print("Qiskit was selected")

         if args[0]=='Qutip':
            backend="Qutip"
            print("Qutip was selected")

         else :
            print("Enter correct command")
         e2e_state=1


      elif command == 'load_topology'and (e2e_state==1 or e2e_state==2):
         if len(args)==1:
            print('\nLoaded topology')
            path=args[0]
            tl,network_topo=load_topo(path,"Qiskit")
            set_parameters(network_topo)
            req_pairs=[]
            e2e_state=2
         else:
            print("Path to config file is not given")


      elif command == 'entanglement_req'and (e2e_state==2):
         if len(args)==8:
            node1=args[0]
            node2=args[1]
            start_time=args[2]
            size=args[3]
            end_time=args[4]
            priority=args[5]
            target_fidelity=args[6]
            timeout=args[7]
            req_pairs.append((node1,node2))
            tm=network_topo.nodes[node1].transport_manager
            tm.request(node2, float(start_time),int(size), float(end_time), int(priority) ,float(target_fidelity), float(timeout) )
         else:
            print("Incorrect request parameters")
      
      elif command == 'run_sim'and (e2e_state==2):
         tl.init()
         tl.run()


     
      elif command == 'get_res'and (e2e_state==2):
         print('get_res')
         get_res(network_topo,req_pairs)

      elif command == 'exit':
         break

      elif command=='--help':
         print("\ncommand for backend $:backend <Qiskit/Qutip>")
         print("\n$:backend Qiskit")
         print("\n\ncommand to Load topology $: load_topo <path_to_json_file>")
         print("\n$:load_topology config.json")
         print("\n\ncommand to create requests $: entanglement_req  <src node-name> <dst node-name> <start_time> <size> <end_time> <priority> <target_fidelity> <timeout>")
         print("$:entanglement_req endnode1 endnode2 5e12 10 20e12 0 0.5 2e12 ")
         print("\n\ncommand to run simulation $: run_sim ")    
         print("\n\ncommand to get results $: get_res ")
         print("\n\ncommand to exit Simulation $:exit")


      else:
         print('Enter correct command')




def main():

   print("\n-------------------------------------------------------------------")
   print("!!!!!!!!!!!!!!!!!!!!Welcome to QNTSim!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
   print("-------------------------------------------------------------------\n")

   while True :

      print("Enter 1 for e91 to get secret key")
      print("Enter 2 for 2 party end-to-end Entanglements between remote Nodes")
      print("Enter Q to Quit")

      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      
      if command=='1':
         print("\n ----E91 QKD--- ")
         e91_state=0
         input_e91(e91_state)
      
      elif command=='2':
         e2e_state=0
         input_entanglements(e2e_state)  

      elif command=='Q':         
         break
   
      else:
         print("Enter correct command")
        
main()














"""
def input_e91():

   print("\n ----E91 QKD--- ")   
   print("\nEnter command to Load topology $: load_topology <path_to_json_file>")

   user_input = input('>>>')
   tokens = user_input.split()
   command = tokens[0]
   args = tokens[1]
   if command == 'load_topology':
      print('Load_topo')
      tl,network_topo=load_topo(args,"Qiskit")
   else:
      print("Enter correct command")

   set_parameters(network_topo)

   
   print("\nEnter command to run E91")
   user_input = input('>>>')
   tokens = user_input.split()
   command = tokens[0]
   sender = tokens[1]
   receiver = tokens[2]
   if command == 'run_e91':
      print('run_e91')
      n=100
      alice=network_topo.nodes[sender]
      bob = network_topo.nodes[receiver]
      e91=E91()
      alice,bob=e91.roles(alice,bob,n)
      
      tl.init()
      tl.run()  
      e91.runE91(alice,bob,n)
   else:
      print("Enter correct command")

"""

"""
def input_entanglements():
   while True:
      print("\nChoose Backend for Simulator")
      print("Enter Qiskit for Qiskit backend ,Qutip for Qutip backend")
      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      if command=='Qiskit':
         backend="Qiskit"
         print("Qiskit was selected")
      elif command=='Qutip':
         backend="Qutip"
         print("Qutip was selected")
      else :
         print("Enter correct command")



      print("\nEnter command to Load topology $: load_topo <path_to_json_file>")
      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      args = tokens[1]
      if command == 'load_topo':
         print('Load_topo')
         tl,network_topo=load_topo(args,backend)
      else:
         print("Enter correct command")
      set_parameters(network_topo)

      req=True
      req_pairs=[]
      #dst=[]
      while req:
         
         print("\nEnter command to Load topology $: create_req  <src node-name> <dst node-name> <start_time> <size> <end_time> <priority> <target_fidelity> <timeout>")
         user_input = input('>>>')
         tokens = user_input.split()
         command = tokens[0]
         node1=tokens[1]
         node2=tokens[2]
         start_time=tokens[3]
         size=tokens[4]
         end_time=tokens[5]
         priority=tokens[6]
         target_fidelity=tokens[7]
         timeout=tokens[8]
         if command == 'create_req':
            print('create_req')
            #load_topo(args)
            req_pairs.append((node1,node2))
            tm=network_topo.nodes[node1].transport_manager
            tm.request(node2, float(start_time),int(size), float(end_time), int(priority) ,float(target_fidelity), float(timeout) )
         else:
            print("Enter correct command")
         print("\n Enter Y to continue to give more requests")
         user_input = input('>>>')
         tokens = user_input.split()
         command = tokens[0]
         if command != 'Y':
            req=False
         

      print("\nEnter command to start simulation")
      print("Enter command to run simulation $: run_sim \n")
      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      args = tokens[1:]
      if command == 'run_sim':
         print('run_sim')
         #load_topo(args)
         tl.init()
         tl.run()


      print("\nEnter command to Get Result")
      print("Enter command to Load topology $: get_res \n")
      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      if command == 'get_res':
         print('get_res')
         get_res(network_topo,req_pairs)

      print("Enter Quit to exit Simulation")
      user_input = input('>>>')
      tokens = user_input.split()
      command = tokens[0]
      if command == 'Quit':
         break

"""


