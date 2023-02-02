from typing import List, Dict
from IPython.display import clear_output

from .network import Network
from .attacks import Attack

class Protocol:
    def __init__(self, messages_list:List[Dict[int, str]], **kwargs) -> None:
        attack = kwargs.get('attack')
        networks = []
        encode = kwargs.get('encode', Network.encode)
        decode = kwargs.get('decode', Network.decode)
        encode_args, decode_args = [], []
        if isinstance(encode, (List, list)):
            encode_args = encode[1:]
            encode = encode[0]
        if isinstance(decode, (List, list)):
            decode_args = decode[1:]
            decode = decode[0]
        for messages in messages_list:
            network = Network(**kwargs, messages=messages)
            clear_output()
            if 'state' in kwargs: network._generate_state_(state=kwargs.get('state'))
            if 'encode' not in kwargs and 'label' in kwargs: network.teleport()
            else: encode(*encode_args, network=network, msg_index=0)
            nodes = range(1, len(network.nodes)) if len(network.nodes)>1 else [0]
            if attack=='DoS': Attack.denial_of_service(network=network, nodes=nodes)
            if attack=='EM': Attack.entangle_and_measure(network=network, nodes=nodes)
            if attack=='IR': Attack.intercept_and_resend(network=network, nodes=nodes)
            # print('')
            if 'label' not in kwargs:
                for i, _ in enumerate(network.bin_msgs[1:], 1):
                    encode(*encode_args, network=network, msg_index=i)
            if 'decode' not in kwargs:
                network.measure()
            networks.append(network)
        self.networks = networks
        self.messages_list = messages_list
        self.recv_msgs_list = decode(*decode_args, networks=networks)
        from .error_analyzer import ErrorAnalyzer
        self.full_err_list, self.mean_list, self.sd_list = ErrorAnalyzer.analyse(protocol=self)
    
    @staticmethod
    def execute():
        pass