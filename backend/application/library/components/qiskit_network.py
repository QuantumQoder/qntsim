#!/usr/bin/env python
# coding: utf-8
# %%

# %%

from typing import List
from qiskit import *
from qiskit.converters import circuit_to_dag
# from qiskit_experiments.framework import BackendData
# from qiskit.providers.ibmq.managed import IBMQJobManager
from numpy import pi
from numpy.random import randint, uniform
from statistics import mean, stdev
from IPython.display import clear_output, display
import matplotlib.pyplot as plt, time, itertools, numpy as np


# %%
def ignore(obj):
    def _():
        pass
    return _

# %%


class QCircuit(QuantumCircuit):
    def __init__(self, *args):
        super().__init__(*args)
    
    @property
    def registers(self):
        registers = {}
        registers.update({register.name:register for register in self.qregs})
        registers.update({register.name:register for register in self.cregs})
        
        return registers
    
    def get_register(self, reg_name:str):
        register = self.registers.get(reg_name)
        
        return register if register else print(f'{reg_name} not found.')
    
    @property
    def measured_qubits(self):
        measured_qubits = set([data.qubits[0] for data in self.data if data.clbits])
#         measured_qubits.add()
        for data in self.data:
            if data.clbits:
                measured_qubits.add(data.qubits[0])
        return list(measured_qubits)

# %%


class Network:
    user_encode = 0
    user_decode = 0
    def __init__(self, messages:List[str], **kwargs):
        assert all(len(messages[0])==len(message) for message in messages[1:]), 'The length of all messages must be equal.'
        self.filename = kwargs.get('filename')
        self.backend = kwargs.get('backend')
        assert self.filename, 'Provide filename.'
        assert self.backend, 'Provide backend.'
        self.messages = messages if all(char=='0' or char=='1' for message in messages for char in message) else string_to_binary(messages)
        if callable((size:=kwargs.get('size', len(self.messages[0])))):
            size = size(len(messages[0]))
        self.size = size
        self.label = kwargs.get('label')
        self.state = kwargs.get
        self.shots = kwargs.get('shots', self.backend.configuration().max_shots)
        self.job_manager = IBMQJobManager()
        self.kwargs = kwargs
        self.corrections = {}
        self.counts = None
        self.outputs = None
        self.strings = []
        self.initiate()
    
    def initiate(self):
        kwargs = self.kwargs
        label = kwargs.get('label')
        state = kwargs.get('state')
        size = self.size
        circuits = []
        if label:
            for i in range(size):
                qc = QCircuit(len(label))
                for j, l in enumerate(label):
                    if int(l): qc.x(j)
                qc.h(range(~-qc.num_qubits) if state else 0)
                qc.cx(range(~-qc.num_qubits) if state else [0]*~-qc.num_qubits,
                      [~-qc.num_qubits]*~-qc.num_qubits if state else range(1, qc.num_qubits))
                qc.barrier()
                circuits.append(qc)
            self.initials = 0
        else:
            initials = randint(4, size=size)
            for i, initial in enumerate(initials):
                qc = QCircuit(1)
                qc.i(0)
                q, r = divmod(initial, 2)
                if r: qc.x(0)
                if q: qc.h(0)
                qc.barrier()
                circuits.append(qc)
            self.initials = initials.tolist()
        self.circuits = circuits
    
    def set_attribute(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.backend = kwargs.get('backend')
    
    @staticmethod
    def encode(network_obj, i:int, **kwargs):
        message = network_obj.messages[i]
        circuits = network_obj.circuits
        for circuit, char in zip(circuits, message):
            circuit.i(0)
            if int(char):
                circuit.x(0)
                circuit.z(0)
            circuit.barrier()
    
    def teleport(self, i:int):
        message = self.messages[i]
        qr = QuantumRegister(1)
        circuits = self.circuits
        state = self.kwargs.get('state')
        for (i, circuit), m in zip(enumerate(circuits), message):
            circuit.add_register(qr)
            if int(m): circuit.x(-1)
            circuit.h(-1)
            circuit.cx(-1, -2)
            circuit.h(-1)
            if state==0:
                circuit.h(-3)
                circuit.cz(-3, 0)
            elif state==1:
                circuit.cx(-3, 0)
            circuit.cx(-2, 0)
            circuit.cz(-1, 0)
            circuit.h(circuit.qubits)
    
    @staticmethod
    def superdense_code(network_obj, message:int, qbit:int):
        message = network_obj.messages[message]
        circuits = network_obj.circuits
        for circuit, char0, char1 in zip(circuits, message[::2], message[1::2]):
            if int(char1): circuit.x(qbit)
            if int(char0): circuit.z(qbit)
    
    @staticmethod
    def decode(network_objs:list, **kwargs):
        for network_obj in network_objs:
            network_obj.rearrange_circuits()
            network_obj.dump()
        generate_job_file(network_objs)
        for network_obj in network_objs:
            counts, outputs = retrieve_jobs(network_obj)
            tots = sum(counts.values())
            messages = network_obj.messages
            initials = network_obj.initials
            if initials:
                if all(len(count)>len(initials) for count in counts):
                    new_counts = {}
                    for key, value in counts.items(): new_counts.update({key[1::2]:new_counts.get(key[1::2], 0)+value})
                    counts, outputs = new_counts, list(new_counts)
                strings = [{''.join(str(int(m)^int(o)^(i%2)) for m, o, i in zip(message if ~-len(messages) else '0'*len(message), output, initials)):value/tots for output, value in counts.items()} for message in messages]
            else:
                circuits = network_obj.circuits_copy
                num_qubits = circuits[0].num_qubits
                strings = []
                for message in messages:
                    string = {}
                    for count, value in counts.items():
                        key = ''.join(count[i] for i in range(0, len(count), num_qubits))
                        string.update({key:string.get(key, 0)+value/tots})
                    strings.append(string)
            network_obj.strings = strings
            print('Received messages!!')
            for i, string in enumerate(strings, 1):
                print(f'Received message {i}', ''.join(chr(int(string[j*8:-~j*8], 2)) for j in range(len(string)//8)))
    
    def dump(self, circuits=None, i=None):
        circuits = self.circuits if not circuits else circuits
        if i: display(circuits[i].draw(fold=-1))
        else: _ = [display(circuit.draw(fold=-1)) for circuit in circuits]
    
    def measure(self):
        circuits = self.circuits
        if (initials := self.initials):
            for circuit, initial in zip(circuits, initials):
                circuit.i(0)
                if initial//2:
                    circuit.h(0)
                circuit.barrier()
        else:
#             circuits = self.circuits
            for circuit in circuits:
                for i in range(1, circuit.num_qubits): circuit.cx(0, i)
                circuit.h(0)
                circuit.barrier()
    
    def rearrange_circuits(self, add_measure=True):
        backend = self.backend
        backend_data = BackendData(backend)
        max_qubits = backend_data.num_qubits
        # maximum number of qubits the backend can support
        self.circuits_copy = self.circuits.copy()
        circuit = self.circuits[0]
        num_qubits = circuit.num_qubits
        # number of qubits in the each of the circuits in the network
        num_circuits, num_idle_qubits = divmod(max_qubits, num_qubits)
        # number of circuits from the list of circuits in the network one can
        # fit within max_qubits of the backend,
        # and the number of qubits that would be left in the last circuit on
        # the backend
        circuits = []
        self.remove_barriers()
        total_circuits = len(self.circuits)
        sections, circuits_left = divmod(total_circuits, num_circuits)
        # number of circuits (each of max_qubits) one needs on the backend to
        # fit all the circuits in the network,
        # and the number of circuits from the list of circuits of the network
        # which could not be implemented into the backend-circuits of max_qubits
        for i in range(sections):
            # the for-block handles the implementation of the network-circuits
            # into the backend-circuits
            qc = QCircuit(max_qubits)
            qc.add_register(ClassicalRegister(num_circuits*num_qubits))
            # each circuit in the network contains num_qubits, and hence total
            # number of classical bits would be num_circuits*num_qubits
            start = 0
            for circuit in self.circuits[i*num_circuits:-~i*num_circuits]:
                if backend_data.is_simulator:
                    has_measure = 'measure' in [instruction.operation.name for instruction in circuit.data]
                    # this checks if the circuits in the network have some
                    # mid-circuit measurement or not (like, in the case of
                    # intercept & resend and entangle & measure attacks). If,
                    # these mid-circuit measurements are present, then the map
                    # must be provided to the classical bits, as well.
                    qc.append(circuit, range(start, start+num_qubits),
                              range(start, start+circuit.num_clbits) if has_measure else None)
                else:
                    tqc = transpile(circuit, backend, optimization_level=3,
                                    initial_layout=list(range(start,
                                                              start+num_qubits)))
                    qc.data.extend(tqc.data)
                start+=num_qubits
            qc.barrier()
            if add_measure: qc.measure(qc.qubits[:max_qubits-num_idle_qubits][::-1], qc.clbits)
            circuits.append(qc)
        else:
            # the else-block handles the implementation of the left-out
            # circuits of the network into an extra backend-circuit, although
            # all the qubits of this backend-circuit won't be utilized.
            # Precisely, 'num_idle_qubits' would remain unutilized.
            qc = QCircuit(max_qubits)
            qc.add_register(ClassicalRegister(circuits_left*num_qubits))
            # each circuit in the network contains num_qubits, but this time
            # total number of classical bits would be
            # number of circuits_left*num_qubits
            start = 0
            for circuit in self.circuits[total_circuits-circuits_left:]:
                if backend_data.is_simulator:
                    has_measure = 'measure' in [instruction.operation.name for instruction in circuit.data]
                    qc.append(circuit, range(start, start+num_qubits),
                              range(start, start+circuit.num_clbits) if has_measure else None)
                else:
                    tqc = transpile(circuit, backend, optimization_level=3,
                                    initial_layout=list(range(start, start+num_qubits)))
                    qc.data.extend(tqc.data)
                start+=num_qubits
            qc.barrier()
            if add_measure: qc.measure(qc.qubits[:num_qubits*circuits_left][::-1], qc.clbits)
            _ = circuits.append(qc) if circuits_left else None
        if backend_data.is_simulator:
            circuits = transpile([circuit.decompose() for circuit in circuits],
                                 basis_gates=backend.configuration().basis_gates)
        self.circuits = circuits
    
    def remove_barriers(self):
        circuits = self.circuits
        for circuit in circuits:
            for instruction in circuit.data:
                if instruction.operation.name=='barrier': circuit.data.remove(instruction)


# %%


class Attack:
    @staticmethod
    def entangle_and_measure(network_obj):
        circuits = network_obj.circuits
        for circuit in circuits:
            register = circuit.get_register('q')
            qr = QuantumRegister(register.size, 'ancilla')
            cr = ClassicalRegister(register.size-circuit.num_clbits, 'c')
            circuit.add_register(qr, cr)
            circuit.cx(register, qr)
            circuit.measure(qr, circuit.clbits)
            circuit.barrier()
    
    @staticmethod
    def denial_of_service(network_obj):
        circuits = network_obj.circuits
        for circuit in circuits:
            choices = randint(2, size=~-circuit.num_qubits)
            for i, choice in enumerate(choices, 2):
                if choice: circuit.u(2*uniform()*pi, 2*uniform()*pi,
                                     2*uniform()*pi, circuit.num_qubits-i)
            circuit.barrier()
    
    @staticmethod
    def intercept_and_resend(network_obj):
        circuits = network_obj.circuits
        for circuit in circuits:
            register = circuit.get_register('q')
            circuit.add_register(ClassicalRegister(register.size-circuit.num_clbits, 'c'))
            bases = randint(2, size=register.size)
            for i, base in enumerate(bases):
                if base: circuit.h(i)
                circuit.measure(i, i)
                if base: circuit.h(i)
            circuit.barrier()


# %%


def generate_job_file(network_obj_list):
    shots = network_obj_list[0].shots
    job_manager = network_obj_list[0].job_manager
    filename = network_obj_list[0].filename
    backend = network_obj_list[0].backend
    assert filename, f'<{network_obj_list[0].__class__.__name__}> object has no filename or, provide your own.'
    assert backend, f'<{network_obj_list[0].__class__.__name__}> object has no backend or, provide your own.'
    
#     if not job_manager: job_manager = IBMQJobManager()
    with open(filename, 'w') as file:
        circuits = [circuit for network_obj in network_obj_list for circuit in network_obj.circuits]
        job_set = job_manager.run(circuits, backend=backend, shots=shots)
        file.write(f'{job_set.job_set_id()}\n')
        print(job_set.report())
#         job_set.retrieve_jobs()
        file.close()

# %%


def retrieve_jobs(network_obj, wait_time=60, filename=None, backend=None, job_manager=None):
#     if filename:
#         backend
#     if filename:
#         assert backend, 'Provide the corresponding backend.'
#         assert job_manager, 'Provide the corresponding job manager.'
#         with open(filename, 'r') as file:
#             for job_set_id in file:
#                 job_set = job_manager.retrieve_jobs(job_set_id=job_set_id[:-1],
#                                                     provider=backend.provider())
#                 while
#                 results = job_set.results
#                 counts = results.get_counts()
    if not network_obj.counts:
        counts = []
        filename = network_obj.filename
        backend = network_obj.backend
        job_manager = network_obj.job_manager
        with open(filename, 'r') as file:
            for job_set_id in file:
                job_set = job_manager.retrieve_job_set(job_set_id=job_set_id[:-1],
                                                       provider=backend.provider())
                while 'queued' in (report:=job_set.report()):
                    print(report)
                    time.sleep(wait_time)
                    clear_output()
                clear_output()
                print(report)
                results = job_set.results()
#                 counts = results.get_counts()
                for circuit in network_obj.circuits:
                    counts.append(results.get_counts(circuit))
            file.close()
        clear_output()
        print(report)
        new_counts = {}
        for keys in itertools.product(*counts):
            key, value = '', 1
            for i, kee in enumerate(keys):
                key+=kee
                value*=counts[i].get(kee)
            new_counts.update({key:value})
        network_obj.counts = new_counts
        network_obj.outputs = list(new_counts)
    
    return network_obj.counts, network_obj.outputs

# %%


def _(network_obj, wait_time_in_sec=900, filename=None, backend=None):
    filename = network_obj.filename if not filename else filename
    backend = network_obj.backend if not backend else backend
    assert filename, f'<{network_obj.__class__.__name__}> object has no filename.'
    assert backend, f'<{network_obj.__class__.__name__}> object has no backend.'
    
    counts = []
    job_manager = network_obj.job_manager
    with open(filename, 'r') as file:
        for job_set_id in file:
            job_set = job_manager.retrieve_job_set(job_set_id=job_set_id[:-1], provider=backend.provider())
            while True:
                report = job_set.report()
                print(report)
                if 'queued' not in report: break
                else: time.sleep(wait_time_in_sec)
#                 clear_output()
            results = job_set.results()
            for circuit in network_obj.circuits: counts.append(results.get_counts(circuit))
        file.close()
    clear_output()
    print(job_set.report())
    if not network_obj.counts:
        new_counts = {}
        for count in itertools.product(*counts):
            key, value = '', 1
            for i, k in enumerate(count):
                key+=k
                value*=counts[i].get(k)
            new_counts.update({key:value})
        network_obj.counts = new_counts
        network_obj.outputs = list(counts)
#     print(counts, outputs)
    
    return network_obj.counts, network_obj.outputs


# %%


def string_to_binary(messages):
    strings = []
    for message in messages:
        strings.append(''.join(''.join('0'*(8-len(bin(ord(char))[2:])))+''.join(bin(ord(char))[2:]) for char in message))
    return strings


# %%


class Protocol:
    def __init__(self, messages_list:list, **kwargs):
        filename = kwargs.get('filename')
        backend = kwargs.get('backend')
        assert filename, 'Provide filename.'
        assert backend, 'Provide backend.'
        networks = []
        attack = kwargs.get('attack')
        encode_params, decode_params = {}, {}
        if 'encode' in kwargs:
            encode = kwargs.get('encode')
            encode_params = encode[1:]
            encode = encode[0]
        else: encode = Network.encode
        if 'decode' in kwargs:
            decode = kwargs.get('decode')
            decode_params = decode[1:]
            decode = decode[0]
        else: decode = Network.decode
        for messages in messages_list:
            network = Network(messages=messages, **kwargs)
            if 'label' not in kwargs: encode(network, 0, *encode_params)
            if attack=='DoS': Attack.denial_of_service(network)
            if attack=='EM': Attack.entangle_and_measure(network)
            if attack=='IR': Attack.intercept_and_resend(network)
            if 'label' in kwargs: network.teleport(0)
            else:
                for i, _ in enumerate(messages[1:], 1):
                    encode(network, i, **encode_params)
                network.measure()
#             decode(network)
#             network.dump()
            networks.append(network)
        decode(networks, **decode_params)
        self.networks = networks
        self.messages_list = messages_list
        full_err_list, mean_list, sd_list = ErrorAnalyzer.analyse(self)
        self.full_err_list = full_err_list
        self.mean_list = mean_list
        self.sd_list = sd_list
    
    @staticmethod
    def execute(messages:list, filename:str, backend, **kwargs):
        assert all(len(messages[0])==len(message) for message in messages[1:]), 'The length of all the messages must be equal.'
        print('Messages for transmission: ', messages)
        messages = messages if all(char=='0' or char=='1' for message in messages for char in message) else string_to_binary(messages)
        secure = kwargs.get('secure')
        if not secure:
            func = kwargs.get('security_function')
            err_list, mean, sd = check_bits(messages, filename, backend, **kwargs) if not func else func(messages, filename, backend, **kwargs)
            if mean>threshold:
                plt.figure(figsize=(20, 5))
                plt.plot(range(1, -~len(err_list)), err_list)
                plt.xlabel('Number of Iterations')
                plt.ylabel('Mean error percentage per iteration')
                print("error in the network:", mean)
                print('deviation in the error:', sd)
        protocol = Protocol(filename=filename,
                            messages_list=[messages],
                            backend=backend,
                            **kwargs)
        network = protocol.networks[0]
        strings = network.strings
        for i, string in enumerate(strings):
            print(f'Decoded by {i}:', string)

# %% [markdown]
# # Error Calculation (single iteration)
#
# \begin{align}
# &\begin{bmatrix}
# 1 & 0 & 1 & 1 & 0 & 1 & 0 & 0\\
# 0 & 0 & 0 & 0 & 1 & 0 & 0 & 1\\
# 0 & 1 & 0 & 1 & 0 & 1 & 0 & 1\\
# 0 & 0 & 1 & 0 & 1 & 0 & 1 & 0\\
# 1 & 1 & 0 & 1 & 0 & 1 & 0 & 1\\
# 0 & 1 & 0 & 0 & 1 & 0 & 1 & 0
# \end{bmatrix}^T
# \cdot
# \begin{bmatrix}
# 30 \\
# 25 \\
# 52 \\
# 40 \\
# 23 \\
# 30
# \end{bmatrix}\\
# =& \begin{bmatrix}
# 53 \\
# 105 \\
# 70 \\
# 105 \\
# 95 \\
# 105 \\
# 70 \\
# 100
# \end{bmatrix}
# = \begin{bmatrix}
# 53 & 105 & 70 & 105 & 95 & 105 & 70 & 100
# \end{bmatrix}\\
# =& \begin{bmatrix}
# \frac{53}{200} & \frac{21}{40} & \frac{7}{20} & \frac{21}{40} & \frac{19}{40} & \frac{21}{40} & \frac{7}{20} & \frac{1}{2}
# \end{bmatrix}
# \end{align}

# %%


class ErrorAnalyzer:
    @staticmethod
    def analyse(protocol_obj):
        networks = protocol_obj.networks
        full_err_list, mean_list, sd_list = [], [], []
        for i, network in enumerate(networks, 1):
            messages = network.messages
            strings_list = network.strings[::-1]
            err_list, prob_list = [], []
            for message, strings in zip(messages, strings_list):
                for string, prob in strings.items():
                    err_list.append([int(m)^int(s) for m, s in zip(message, string)])
                    prob_list.append(prob)
            err_list = np.array(err_list)
            prob_list = np.array(prob_list)
            err_list = err_list.T@prob_list
            full_err_list.append(err_list)
            err_prct = mean(err_list)*100
            err_sd = stdev(err_list)
            mean_list.append(err_prct)
            sd_list.append(err_sd)
            print(f'Average error for iteration {i}: {err_prct}')
            print(f'Deviation in the error for iteration {i}: {err_sd}')
        
        return full_err_list, mean_list, sd_list
    
#     @staticmethod
#     def analyse(protocol_obj):
#         networks = protocol_obj.networks
#         final_err_list, mean_list, sd_list = [], [], []
#         for i, network in enumerate(networks, 1):
#             messages = network.messages
#             strings_list = network.strings[::-1]
#             err_val, err_sd = [], []
#             for message, strings in zip(messages, strings_list):
#                 full_err_list, prob_list = [], []
#                 for string, prob in strings.items():
#                     err_list = [int(m)^int(s) for m, s in zip(message, string)]
#                     full_err_list.append(err_list)
#                     prob_list.append(prob)
#                 full_err_list = np.array(full_err_list)
#                 prob_list = np.array(prob_list)
#                 err_val.append(mean(full_err_list.T@prob_list))
#                 err_sd.append(stdev(full_err_list.T@prob_list))
#             final_err_list.append(full_err_list)
#             err_prct = mean(err_val)*100
#             mean_list.append(err_prct)
#             err_sd = mean(err_sd)
#             sd_list.append(err_sd)
#             print(f'Average error for iteration {i}: {err_prct}')
#             print(f'Standard deviation of error for iteration {i}: {err_sd}')
        
#         return final_err_list, mean_list, sd_list
    
#     @ignore
#     @staticmethod
#     def _(i, network_obj):
#         filename = network_obj.filename
#         backend = network_obj.backend
#         counts, outcomes = retrieve_jobs(network_obj)
#         messages = network_obj.messages
# #         goes into decode
#         initials = network_obj.initials
#         if initials:
#             ideals = [initial%2 for initial in initials]
#             for message in messages: ideals = [ideal^int(char) for ideal, char in zip(ideals, message)]
#             ideals = [''.join(str(i) for i in ideals[i*network_obj.circuits[0].num_qubits:-~i*network_obj.circuits[0].num_qubits]) for i in range(len(network_obj.circuits))]
#         else:
#             ideals = list(messages[0])
#             for message in messages[1:]: ideals = [int(ideal)^int(char) for ideal, char in zip(ideals, message)]
#         shots = network_obj.shots
#         for count in counts:
#             for key, value in count.items():
#                 count[key] = value/shots
# #         print(counts)
#         full_count = {}
#         full_counts = []
#         for count in itertools.product(*counts):
#             key, value = '', 1
#             for i, j in enumerate(count):
#                 value*=counts[i][j]
#                 key+=j
#             full_count.update({key:value})
#         full_counts = network_obj
#         print(full_counts)
#         err_list = [mean([int(ideal)^int(k) for ideal, k in zip(ideals, key)])*value for key, value in full_counts.items()]
# #       err_list =   mean([1, 0, 0, 1, ... 16 bits])*#shots for (string)/ total shots
#         print(err_list)
#         err_prct = mean(err_list)
#         err_sd = stdev(err_list)
#         print('Average error:', err_prct)
#         print('Deviation in error:', err_sd)
        
#         return err_list, err_prct, err_sd
    
    @staticmethod
    def full_analysis(iterations:int, message_length:int, filename:str, backend, **kwargs):
        q = kwargs.get('q', 1)
        attack = kwargs.get('attack')
        full_err_list, mean_list, sd_list = [], [], []
        all_messages = [[''.join(str(randint(2)) for i in range(message_length)) for j in range(q)] for i in range(iterations)]
        protocol = Protocol(messages_list=all_messages, filename=filename, backend=backend, **kwargs)
        full_err_list = protocol.full_err_list
        mean_list = protocol.mean_list
        sd_list = protocol.sd_list
        print(f"Error analysis for {attack}")
        bit_error = sum(full_err_list)
        plt.figure(figsize=(20, 5))
        plt.bar(range(len(bit_error)), bit_error)
        plt.xlabel('Bits')
        plt.ylabel(f'Error per bit for {iterations} iterations')
        plt.show()
        plt.figure(figsize=(20, 5))
        plt.plot(range(len(mean_list)), mean_list)
        plt.xlabel('Number of Iterations')
        plt.ylabel('Mean error percentage per iteration')
        plt.show()
        plt.figure(figsize=(20, 5))
        plt.plot(range(len(sd_list)), sd_list)
        plt.xlabel('Number of Iterations')
        plt.ylabel('Error deviation per iteration')
        plt.show()
#         print(mean_list, sd_list)
        print(f'Total error over all the bits for {iterations} iterations: {mean(bit_error)}')
        print(f"Total mean error over all the {iterations} iterations: {mean(mean_list)}")
        print(f"Total error deviation over all the {iterations} iterations: {mean(sd_list)}")


# %%
# message = '010010010' #sender
# string =  '100010010' #receiver
# err_lis = [1, 1,0 0,0,0,0,0,0] #qntsim
# err = mean(err_lis) #qntsim
# # qiskit
# err = [1,1,0 0,0,0,0,0,0]*counts/total shots
# err = [0,1,0,0,1,0,1,0,0]*counts/total shots
# total shots = 1, 100
# err = mean(each of the elements)
# total shots
# 1024 on local simulators
# 200000 on cloud simulators
