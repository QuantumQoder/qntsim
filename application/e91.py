
import numpy as np
from qntsim.components.circuit import BaseCircuit


class E91():

    # Request transport manager  
    def request_entanglements(self,sender,receiver,n):
        sender.transport_manager.request(receiver.owner.name,5e12,n,20e12,0,.7,5e12)
        return sender,receiver
    
    # Sets the sender and receiver as alice and bob respectively, and request entanglements 
    def roles(self,alice,bob,n):
        sender=alice
        receiver=bob
        print('sender, receiver',sender.owner.name,receiver.owner.name)
        return self.request_entanglements(sender,receiver,n)


    def measurement(self,qm,choice, key):
        #print('choice',choice)
        if choice == 1: 
            Circuit=BaseCircuit.create("Qiskit")      #X observable
            circ=Circuit(1)
            circ.h(0)
            circ.measure(0)
            output=qm.run_circuit(circ,[key])
        if choice == 2:  
            Circuit=BaseCircuit.create("Qiskit")       #W observable
            circ=Circuit(1)
            circ.s(0)
            # circ.
            circ.h(0)
            circ.t(0)
            circ.h(0)
            circ.measure(0)
            output=qm.run_circuit(circ,[key])
        if choice == 3:  
            Circuit=BaseCircuit.create("Qiskit")       #Z observable
            circ=Circuit(1)
            circ.measure(0)
            output=qm.run_circuit(circ,[key])
        if choice == 4: 
            Circuit=BaseCircuit.create("Qiskit")        #V observable
            circ=Circuit(1)
            circ.s(0)
            circ.h(0)
            circ.tdg(0)
            circ.h(0)
            circ.measure(0)
            output=qm.run_circuit(circ,[key])
        #print('output',output)
        return output


    def alice_measurement(self,alice):
        choice=[1,2,3]
        qm_alice=alice.timeline.quantum_manager
        meas_results_alice=[]
        alice_choice_list=[]
        for info in alice.resource_manager.memory_manager:
            key=info.memory.qstate_key
            state=qm_alice.get(key)
            #print('initial state',info.index,info.state,type(state))
            alice_choice=np.random.choice(choice)
            #print('keys alice',key)
            meas_results_alice.append(self.measurement(qm_alice,alice_choice,key))
            alice_choice_list.append(alice_choice)
        # print('Alice measuremnt reuslts',meas_results_alice)
        return alice_choice_list,meas_results_alice
    

    def bob_measurement(self,bob):
        qm_bob=bob.timeline.quantum_manager
        meas_results_bob=[]
        bob_choice_list=[]
        choice=[2,3,4]
        for info in bob.resource_manager.memory_manager:
            key=info.memory.qstate_key
            bob_choice=np.random.choice(choice)
            #print('keys bob',key)
            meas_results_bob.append(self.measurement(qm_bob,bob_choice,key))
            bob_choice_list.append(bob_choice)
        return bob_choice_list,meas_results_bob


    def chsh_correlation(self,alice_results,bob_results,alice_choice,bob_choice,n):

        countA1B2=[0,0,0,0]
        countA1B4=[0,0,0,0]
        countA3B2=[0,0,0,0]
        countA3B4=[0,0,0,0]
        check_list = ['00','01','10','11']
        res=[]
    
        for i in range(len(alice_results)):
            # res[i]=str(alice_results[i])+str(bob_results[i])
            res.append((alice_results[i],bob_results[i]))
        #print('reslist',res)
        for i in range(n):
            res2=''.join(map(str,res[i]))
            #print('aa',res[i],res2,alice_choice[i],bob_choice[i])
            if (alice_choice[i]==1 and bob_choice[i]==2):
                for j in range(4):
                    # print('rs and check',res[i],check_list[j])
                    if res2 == check_list[j]:
                        countA1B2[j] +=1
            if (alice_choice[i]==1 and bob_choice[i]==4):
                for j in range(4):
                    if res2 == check_list[j]:
                        countA1B4[j] +=1

            if (alice_choice[i]==3 and bob_choice[i]==2):
                for j in range(4):
                    if res2 == check_list[j]:
                        countA3B2[j] +=1
            
            if (alice_choice[i]==3 and bob_choice[i]==4):
                for j in range(4):
                    if res2 == check_list[j]:
                        countA3B4[j] +=1

        #print('countA1B2', countA1B2)
        #print('countA1B4', countA1B4)
        #print('countA3B2', countA3B2)
        #print('countA3B4', countA3B4)

        total12=sum(countA1B2)
        total14=sum(countA1B4)
        total32=sum(countA3B2)
        total34=sum(countA3B4)

        try:
            expect12 = (countA1B2[0]-countA1B2[1]-countA1B2[2]+countA1B2[3])/total12
            expect14 = (countA1B4[0]-countA1B4[1]-countA1B4[2]+countA1B4[3])/total14
            expect32 = (countA3B2[0]-countA3B2[1]-countA3B2[2]+countA3B2[3])/total32
            expect34 = (countA3B4[0]-countA3B4[1]-countA3B4[2]+countA3B4[3])/total34
        except ZeroDivisionError:
            print(f'Error occured,Retry e91 again')


        corr=expect12-expect14+expect32+expect34

        return corr

    def runE91(self,alice,bob,n):
        alice_choice,alice_meas=self.alice_measurement(alice)
        bob_choice,bob_meas=self.bob_measurement(bob)
        key_mismatch=0
        alice_key,bob_key=[],[]
        alice_results, bob_results =[],[]
        #print('Alice Measurements',alice_meas)
        #print('Bob Measuremenst', bob_meas)
        for i in range(n):
            alice_meas_i=list(alice_meas[i].items())
            bob_meas_i=list(bob_meas[i].items())
            alice_results.append(alice_meas_i[0][1]) 
            bob_results.append(bob_meas_i[0][1])
            #print("bob_results",bob_meas_i[0][1])
            if (alice_choice[i]==2 and bob_choice[i]==2) or (alice_choice[i]==3 and bob_choice[i]==3):
                #print('Base match',alice_meas[i],bob_meas[i])
                alice_key.append(alice_meas_i[0][1])
                bob_key.append(bob_meas_i[0][1])
        
    
        for j in range(len(alice_key)):
            if alice_key[j] != bob_key[j]:
                key_mismatch += 1
        #print('Alice choicec',alice_choice)
        #print('Bob choicec',bob_choice)
        #print('Alice results',alice_results)
        #print('Bob results',bob_results)
        print('Alice keys', alice_key)
        print('Bob keys', bob_key)
        print('Key length',len(alice_key))
        print('Mismatched keys', key_mismatch)
        chsh_value=self.chsh_correlation(alice_results,bob_results,alice_choice,bob_choice,n)
        print('Correlation value', str(round(chsh_value,3)))
# showFuncs : String : ["Qiskit", "Qutip"]
# network_config : String : File path for json configuration file
# sender : String : Sender node name
# receiver : String : Receiver node name
# keylength : Integer : Length of the key : 0 < keylength < 50

# def e91(framework,network_config, sender, receiver, keylength):
#     from qntsim.kernel.timeline import Timeline
#     Timeline.DLCZ=False
#     Timeline.bk=True
#     from qntsim.topology.topology import Topology

#     tl = Timeline(4e12,framework)

#     network_topo = Topology("network_topo", tl)
#     network_topo.load_config(network_config)

#     if keylength<50 and keylength>0:
#         n=int((9*keylength)/2)
#         alice=network_topo.nodes[sender]
#         bob = network_topo.nodes[receiver]
#         e91=E91()
#         alice,bob=e91.roles(alice,bob,n)
#         tl.init()
#         tl.run()
#         e91.runE91(alice,bob,n)
#     else:
#         print("key length should be between 0 and 50")

# e91("Qiskit","../example/3node.json", "a", "b", 20)