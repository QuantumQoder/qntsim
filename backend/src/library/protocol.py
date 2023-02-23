import logging
from functools import partial
from typing import Any, List, Dict
from time import time_ns
from IPython.display import clear_output

from .network import Network
from .attacks import Attack, ATTACK_TYPE
from .security_checks import insert_check_bits

class Protocol:
    def __init__(self, messages_list:List[Dict[int, str]], name:str='protocol', **kwds) -> None:
        self._name = name
        logging.basicConfig(filename=self._name+'.log', filemode='w', level=logging.INFO, format='%(pathname)s %(threadName)s %(module)s %(funcName)s %(message)s')
        self.messages_list = messages_list
        self.funcs = []
        if 'state' in kwds: self.funcs.append(partial(Network._generate_state_, state=kwds.get('state'), label=kwds.get('label')))
        self.funcs.append(partial(Network.teleport) if 'encode' not in kwds and 'label' in kwds else partial(kwds.get('encode', Network.encode), msg_index=0))
        if (attack:=kwds.get('attack')) is not None: self.funcs.append(partial(Attack.implement, attack=ATTACK_TYPE[attack].value))
        if 'label' not in kwds: self.funcs.extend([partial(kwds.get('encode', Network.encode), msg_index=i) for i in range(1, len(messages_list[0]))])
        self.funcs.append(kwds.get('measure', partial(Network.measure)))
    
    def __iter__(self):
        for network in self.networks:
            yield network
    
    def __call__(self, topology:str, functions:List[partial]=None, *args: Any, **kwds: Any) -> Any:
        Network._funcs = functions if functions else self.funcs
        start_time = time_ns()
        self.networks = [Network(**kwds, name=self._name, topology=topology, messages=messages) for messages in self.messages_list]
        mid_time = time_ns()
        logging.info('generated all networks')
        Network.execute(networks=self.networks)
        if Network._funcs==self.funcs: self.recv_msgs_list = kwds.get('decode', Network.decode)(networks=self.networks)
        logging.info(f'completed execution within {time_ns()-start_time-mid_time} ns')
        from .error_analyzer import ErrorAnalyzer
        self.full_err_list, self.mean_list, self.sd_list = list(zip(*ErrorAnalyzer.analyse(protocol=self)))
        
        return self
    
    @staticmethod
    def execute():
        pass