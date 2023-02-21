import logging
from functools import partial
from typing import Any, List, Dict
from IPython.display import clear_output

from .network import Network
from .attacks import Attack, ATTACK_TYPE
from .security_checks import insert_check_bits

class Protocol:
    def __init__(self, topology:str, messages_list:List[Dict[int, str]], name:str='protocol', **kwds) -> None:
        self._name = name
        self._topology = topology
        logging.basicConfig(filename=self._name+'.log', filemode='w', level=logging.INFO, format='%(asctime)s %(message)s')
        encode_params, decode_params = [], []
        self.messages_list = messages_list
        self.functions = kwds.get('funcs', [])
        if not self.functions:
            if 'state' in kwds: self.functions.append(partial(Network._generate_state_, state=kwds.get('state')))
            encode = kwds.get('encode', Network.encode)
            if isinstance(encode, (List, list)):
                encode_params = encode[1:]
                encode = encode[0]
            self.functions.append(partial(Network.teleport) if 'encode' not in kwds and 'label' in kwds else partial(encode, *encode_params, msg_index=0))
            attack = kwds.get('attack')
            if attack is not None:
                self.functions.append(partial(Attack.implement, attack=ATTACK_TYPE[attack].value))
            if 'label' not in kwds: self.functions.extend([partial(encode, *encode_params, msg_index=i) for i in range(1, len(messages_list[0]))])
            if 'decode' not in kwds: self.functions.append(partial(Network.measure))
        Network._functions = self.functions
        self.networks = [Network(**kwds, topology=topology, messages=messages) for messages in self.messages_list]
        logging.info('All networks have been generated.')
        Network.execute(networks=self.networks)
        logging.info('All networks have been executed!!')
        decode = kwds.get('decode', Network.decode)
        if isinstance(decode, (List, list)):
            decode_params = decode[1:]
            decode = decode[0]
        self.recv_msgs_list = decode(*decode_params, networks=self.networks)
        from .error_analyzer import ErrorAnalyzer
        self.full_err_list, self.mean_list, self.sd_list = list(zip(*ErrorAnalyzer.analyse(protocol=self)))
    
    def __iter__(self):
        for network in self.networks:
            yield network
    
    # def __call__(self, functions:List[partial], *args: Any, **kwds: Any) -> Any:
    #     Network._functions = functions
    #     self.networks = [Network(**kwds, topology=self.topology, messages=messages) for messages in self.messages_list]
    #     logging.info('All networks have been generated.')
    #     Network.execute(networks=self.networks)
    #     logging.info('All networks have been executed!!')
    #     decode = kwds.get('decode', Network.decode)
    #     if isinstance(decode, (List, list)):
    #         decode_params = decode[1:]
    #         decode = decode[0]
    #     self.recv_msgs_list = decode(*decode_params, networks=self.networks)
    #     from .error_analyzer import ErrorAnalyzer
    #     self.full_err_list, self.mean_list, self.sd_list = list(zip(*ErrorAnalyzer.analyse(protocol=self)))
        
    #     return self
    
    @staticmethod
    def execute():
        pass