from qntsim.kernel.timeline import Timeline
from qntsim.topology.node import QKDNode
from qntsim.components.optical_channel import QuantumChannel, ClassicalChannel
from qntsim.qkd.E91 import pair_e91_protocols
from matplotlib import pyplot as plt
import time

class KeyManager():
    def __init__(self, timeline, keysize, num_keys):
        self.timeline = timeline
        self.lower_protocols = []
        self.keysize = keysize
        self.num_keys = num_keys
        self.keys = []
        self.times = []
        
    def send_request(self):
        for p in self.lower_protocols:
            p.push(self.keysize, self.num_keys) # interface for E91 to generate key
            
    def pop(self, info): # interface for E91 to return generated keys
        self.keys.append(info)
        self.times.append(self.timeline.now() * 1e-9)


def test(sim_time, keysize):
    """
    sim_time: duration of simulation time (ms)
    keysize: size of generated secure key (bits)
    """
    # begin by defining the simulation timeline with the correct simulation time
    tl = Timeline(sim_time * 1e12)
    tl.seed(0)
    
    # Here, we create nodes for the network (QKD nodes for key distribution)
    # stack_size=1 indicates that only the BB84 protocol should be included
    n1 = QKDNode("n1", tl, stack_size=3)
    n2 = QKDNode("n2", tl, stack_size=3)
    print('n1 n1',n1.protocol_stack[2],n2.protocol_stack[2])
    pair_e91_protocols(n1.protocol_stack[2], n2.protocol_stack[2])
    
    # connect the nodes and set parameters for the fibers
    # note that channels are one-way
    # construct a classical communication channel
    # (with arguments for the channel name, timeline, and length (in m))
    cc0 = ClassicalChannel("cc_n1_n2", tl, distance=1e3)
    cc1 = ClassicalChannel("cc_n2_n1", tl, distance=1e3)
    cc0.set_ends(n1, n2)
    cc1.set_ends(n2, n1)
    # construct a quantum communication channel
    # (with arguments for the channel name, timeline, attenuation (in dB/km), and distance (in m))
    qc0 = QuantumChannel("qc_n1_n2", tl, attenuation=1e-5, distance=1e3,
                         polarization_fidelity=0.97)
    qc1 = QuantumChannel("qc_n2_n1", tl, attenuation=1e-5, distance=1e3,
                         polarization_fidelity=0.97)
    qc0.set_ends(n1, n2)
    qc1.set_ends(n2, n1)
    
    # instantiate our written keysize protocol
    km1 = KeyManager(tl, keysize, 25)
    print('km1',km1.lower_protocols,n1.protocol_stack[2])
    km1.lower_protocols.append(n1.protocol_stack[2])
    n1.protocol_stack[2].upper_protocols.append(km1)
    print('km1',km1.lower_protocols,n1.protocol_stack[2],n1.protocol_stack[2].upper_protocols)
    km2 = KeyManager(tl, keysize, 25)
    km2.lower_protocols.append(n2.protocol_stack[2])
    n2.protocol_stack[2].upper_protocols.append(km2)
    print('km2',km2.lower_protocols,n2.protocol_stack[2],n2.protocol_stack[2].upper_protocols)
    # start simulation and record timing
    
    tl.init()
    km1.send_request()
    tick = time.time()
    tl.run()
    print("execution time %.2f sec" % (time.time() - tick))
    
    # display our collected metrics
    plt.plot(km1.times, range(1, len(km1.keys) + 1), marker="o")
    plt.xlabel("Simulation time (ms)")
    plt.ylabel("Number of Completed Keys")
    plt.show()
    
    print("key error rates:")
    for i, e in enumerate(n1.protocol_stack[0].error_rates):
        print("\tkey {}:\t{}%".format(i + 1, e * 100))


test(10,128)