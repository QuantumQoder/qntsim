from qntsim.kernel.timeline import Timeline
Timeline.DLCZ=False
Timeline.bk=True
from qntsim.topology.topology import Topology
from tabulate import tabulate
from qntsim.components.circuit import Circuit
from qiskit import *
from qutip.qip.circuit import QubitCircuit, Gate
from qutip.qip.operations import gate_sequence_product
from qiskit.extensions import Initialize
#from qiskit.ignis.verification import marginal_counts
from qiskit.quantum_info import random_statevector

#random.seed(0)
network_config = "/home/bhanusree/Desktop/QNTv1/QNTSim-Demo/QNTSim/example/3node.json"

n,k,lamda=10,6,40

tl = Timeline(10e12,"Qiskit")
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)
# network_topo.create_random_topology(n,network_config)



def set_parameters(topology: Topology):
   
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
    # for node in topology.get_nodes_by_type("QuantumRouter"):
    #     node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
    #     node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
  
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)


node1='a'
node2='b'
tm=network_topo.nodes[node1].transport_manager
tm.request(node2, start_time=5e12,size=1, end_time=10e12, priority=0 , target_fidelity= 0.5, timeout=2e12) 



tl.init()
tl.run()


table=[]
print('a memories')
for info in network_topo.nodes["a"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'a',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])

print(tabulate(table, headers=['Index','Source node', 'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('b memories')
for info in network_topo.nodes["b"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'b',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])

print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))
table=[]
print('s1 memories')
for info in network_topo.nodes["s1"].resource_manager.memory_manager:
    if info.state == 'ENTANGLED' or info.state == 'OCCUPIED':
        table.append([info.index,'s1',info.remote_node,info.fidelity,info.entangle_time * 1e-12,info.entangle_time * 1e-12+info.memory.coherence_time,info.state])

print(tabulate(table, headers=['Index','Source node' ,'Entangled Node' , 'Fidelity', 'Entanglement Time' ,'Expire Time', 'State'], tablefmt='grid'))




def alice_keys():
    qm_alice = network_topo.nodes[node1].timeline.quantum_manager
    for mem_info in network_topo.nodes[node1].resource_manager.memory_manager:
        if mem_info.state == 'ENTANGLED':
            key=mem_info.memory.qstate_key
            state= qm_alice.get(key)
            print("alice keys",key, state)
            return qm_alice,key,state

def bob_keys():
    qm_bob = network_topo.nodes[node2].timeline.quantum_manager
    for mem_info in network_topo.nodes[node2].resource_manager.memory_manager:
        if mem_info.state == 'ENTANGLED':
            key=mem_info.memory.qstate_key
            state= qm_bob.get(key)
            print("bob keys",key,state)
            return qm_bob,key,state
            print("bob keys",key,state)
#alice_keys()
bob_keys()

def create_random_qubit():
    qc = QuantumCircuit(1)
    initial_state = [1,0]
    qc.initialize(initial_state,0)
    print('Random state', qc)
    return qc





def alice_measurement(qubit):
    """
    psi = random_statevector(2)
    init_gate = Initialize(psi)
    init_gate.label = "init"
    qr = QuantumRegister(3, name="q")
    crz= ClassicalRegister(1,name="crz")
    crx= ClassicalRegister(1,name="crx")
    new_qc=QuantumCircuit(qr,crz,crx)
    qm_alice,key,alice_state=alice_keys()
    #q0=qubit
    #
    #new_c.barrier()
    circ=new_qc.compose(alice_state,[1,2])
    circ.append(init_gate, [0])
    
    print(circ)
    circ.cx(0,1)
    circ.h(0)
    print(circ)
    circ.barrier()
    t1=circ.measure(0,0)
    t2=circ.measure(1,1)
    print("t1,t2",t2)
    
    qm_alice.get(key)

    print('size',crz,crx)
    
    return init_gate ,circ,crz,crx
    
    """
    #output = qm.run_circuit(circ,[key])
    # circ.cx(0,1)
    """
    psi = random_statevector(2)
    init_gate = Initialize(psi)
    init_gate.label = "init"
    qm_alice,key,alice_state=alice_keys()
    qc= alice_state
    #qc.compose(alice_state,[1,2])

    qc.append(init_gate, [0])
    qc.cx(0,1)
    qc.h(0)
    print("t",qc)
    print("t",key)
    #qc.barrier()
    #qc.measure(0,0)
    #qc.measure(1,1)
    #print("t1,t2",t1,t2)
    #qm_alice.run_circuit(qc,[key])
    #return init_gate ,qc
    """
    # psi = random_statevector(2)
    qm_alice,key,alice_state=alice_keys()
    key_0=qm_alice.new2()
    print("alice key new key",key,key_0,qm_alice.get(key_0))
    circ=Circuit(2)
    circ.cx(1,2)
    circ.h(1)
    circ.measure(0)
    circ.measure(2)
    output=qm_alice.run_circuit(circ,[key_0,key])
    crz=output.get(key_0)
    crx=output.get(key)
    # circ.measure(1)
    #qm_alice,key,alice_state=alice_keys()
    #alice_state.append()
    print('output',key_0,key,output,crz,crx)
    return crz,crx

   

def bob_gates(crz,crx):

    
    qm_bob, key, state= bob_keys()
    circ=Circuit(1)
    if crz == 1:
        circ.z(0)
        # circ.measure(0)
    if crx == 1:
        circ.x(0)
        # circ.measure(0)

    output = qm_bob.run_circuit(circ,[key])
    bob_state = qm_bob.get(key)
    print("bob output", output,type(circ),type(state))
    print("\n\n", bob_state)
    
    print('Measurement check', bob_state)
    """circ.z(2).c_if(c1, 1)
    circ.x(2).c_if(c2, 1)
    
    #bob_state.z(1).c_if(c1,1) # Apply gates if the registers 
    #bob_state.x(1).c_if(c2,1)#
    print("bob ",circ)
    inverse_init_gate = init_gate.gates_to_uncompute()
    circ.append(inverse_init_gate, [2])
    cr_result = ClassicalRegister(1)
    circ.add_register(cr_result)

    circ.measure(2,2)
    print("bob final",circ)"""


    

qubit=create_random_qubit()
#qm,key,state = alice_keys()

crz,crx=alice_measurement(qubit)
bob_gates(crz,crx)
