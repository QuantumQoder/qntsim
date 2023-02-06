from functools import partial
from typing import List, Dict
from IPython.display import clear_output

from .network import Network
from .attacks import Attack

class Protocol:
    def __init__(self, messages_list:List[Dict[int, str]], *args, **kwargs) -> None:
        encode_params, decode_params = [], []
        self.messages_list = messages_list
        self.functions = kwargs.get('functions', [])
        if not self.functions:
            if 'state' in kwargs: self.functions.append(partial(Network._generate_state_, state=kwargs.get('state')))
            encode = kwargs.get('encode', Network.encode)
            if isinstance(encode, (List, list)):
                encode_params = encode[1:]
                encode = encode[0]
            self.functions.append(partial(Network.teleport) if 'encode' not in kwargs and 'label' in kwargs else partial(encode, *encode_params, msg_index=0))
            attack = kwargs.get('attack')
            if attack: self.functions.append(partial(Attack.implement, attack=attack))
            if 'label' not in kwargs: self.functions.extend([partial(encode, *encode_params, msg_index=i) for i in range(1, len(messages_list[0]))])
            if 'decode' not in kwargs: self.functions.append(partial(Network.measure))
        Network._functions = self.functions
        self.networks = [Network(*args, **kwargs, messages=messages) for messages in messages_list]
        Network.execute(networks=self.networks)
        decode = kwargs.get('decode', Network.decode)
        if isinstance(decode, (List, list)):
            decode_params = decode[1:]
            decode = decode[0]
        self.recv_msgs_list = decode(*decode_params, networks=self.networks)
        from .error_analyzer import ErrorAnalyzer
        self.full_err_list, self.mean_list, self.sd_list = ErrorAnalyzer.analyse(protocol=self)
    
    @staticmethod
    def execute():
        pass