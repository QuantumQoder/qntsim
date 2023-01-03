from typing import List
from IPython.display import clear_output

from qntsim.library.components.network import Network
from qntsim.library.attacks.attacks import Attack


def ignore(obj):
    def _():
        pass
    return _

class Protocol:
    def __init__(self, platform:str, messages_list:List[List[str]], **kwargs) -> None:
        self.backend = kwargs.get('backend')
        assert self.backend, 'Provide backend.'
        if Network[platform]==Network.qiskit:
            self.filename = kwargs.get('filename')
            assert self.filename, 'Provide filename.'
        networks = []
        attack = kwargs.get('attack')
        # Network = Network[platform]
        encode_args, decode_args = [], []
        network_factory = Network[platform].value
        encode = kwargs.get('encode', network_factory.encode)
        decode = kwargs.get('decode', network_factory.decode)
        if isinstance(encode, list):
            encode_args = encode[1:]
            encode = encode[0]
        if isinstance(decode, list):
            decode_args = decode[1:]
            decode = decode[0]
        for messages in messages_list:
            network = network_factory(**kwargs, messages=messages)
            clear_output()
            print('Entangled pairs generated!!')
            # if attack=='DoS': Attack.denial_of_service(network)
            # if attack=='EM': Attack.entangle_and_measure(network)
            # if attack=='IR': Attack.intercept_and_resend(network)
            if 'label' in kwargs:
                network.teleport()
            else: encode(network, 0, *encode_args)
            attack_factory = Attack[platform].value
            nodes = range(1, len(network.nodes if platform=='qntsim' else network.circuits[0].num_qubits)) if ~-len(network.nodes if platform=='qntsim' else network.circuits[0].num_qubits) else [0]
            if attack=='DoS': attack_factory.denial_of_service(network, nodes=nodes)
            if attack=='EM': attack_factory.entangle_and_measure(network, nodes=nodes)
            if attack=='IR': attack_factory.intercept_and_resend(network, nodes=nodes)
            # match attack:
            #     case 'DoS': attack_factory.denial_of_service(network)
            #     case 'EM': attack_factory.entangle_and_measure(network)
            #     case 'IR': attack_factory.intercept_and_resend(network)
            if 'label' not in kwargs:
                for i in range(len(messages[1:])):
                    encode(network, -~i, *encode_args)
            if 'decode' not in kwargs:
                network.measure(state=kwargs.get('state'))
            networks.append(network)
        decode(networks, *decode_args)
        self.networks = networks
        self.messages_list = messages_list
        from ..error_analyzer.error_analyzer import ErrorAnalyzer
        self.full_err_list, self.mean_list, self.sd_list = ErrorAnalyzer.analyse(self)


def generate_job_file(protocol_obj:Protocol):
    networks = protocol_obj.networks
    shots = networks[0].shots
    job_manager = protocol_obj.manager
    filename = protocol_obj.filename
    backend = protocol_obj.backend
    assert filename, f'Provide filename to the {protocol_obj.__class__.__name__} object.'
    assert backend, f'Provide backend to the {protocol_obj.__class__.__name__} object.'

    with open(filename, 'w') as file:
        circuits = [circuit for network in networks for circuit in network.circuits]
        job_set = job_manager.run(circuits, backend=backend, shots=shots)
        file.write(f'{job_set.job_set_id()}\n')
        print(job_set.report())
        file.close()

def retrieve_jobs(**kwargs):
    protocol = kwargs.get('protocol')
    network = kwargs.get('network')
    if protocol:
        pass
    elif network:
        if not network.counts:
            counts = []
            filename = network.filename
            backend = network.backend
            job_manager = network.job_manager
            with open(job_manager, 'r') as file:
                for job_set_id in file:
                    job_set = job_manager

@ignore
def __(network_obj, wait_time=60, filename=None, backend=None, job_manager=None):
    if not network_obj.counts:
        counts = []
        filename = network_obj.filename
        backend = network_obj.backend
        job_manager = network_obj.job_manager