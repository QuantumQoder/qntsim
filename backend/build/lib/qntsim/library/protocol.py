import logging
from functools import partial
from typing import Any, List, Dict, Tuple
from time import time_ns, time
from IPython.display import clear_output

from .network import Network
from .attacks import Attack, ATTACK_TYPE
from .security_checks import insert_check_bits

class Protocol:
    def __init__(self, messages_list:List[Dict[Tuple, str]], name:str='protocol', **kwds) -> None:
        self.__name = name
        logging.basicConfig(filename=self.__name+'.log', filemode='w', level=logging.INFO, format='%(pathname)s > %(threadName)s : %(module)s . %(funcName)s %(message)s')
        self.messages_list = messages_list
        self.__funcs = []
        if 'state' in kwds: self.__funcs.append(partial(Network.generate_state, state=kwds.get('state'), label=kwds.get('label')))
        self.__funcs.append(partial(Network.teleport) if 'encode' not in kwds and 'label' in kwds else partial(kwds.get('encode', Network.encode), msg_index=0))
        if (attack:=kwds.get('attack')) is not None: self.__funcs.append(partial(Attack.implement, attack=ATTACK_TYPE[attack].value))
        if len(messages_list[0])>1: self.__funcs.extend(partial(kwds.get('encode', Network.encode), msg_index=i) for i in range(1, len(messages_list[0])))
        self.__funcs.append(kwds.get('measure', partial(Network.measure)))
    
    def __iter__(self):
        for network in self.networks:
            yield network
    
    def __call__(self, topology, functions:List[partial]=None, *args: Any, **kwds: Any) -> Any:
        Network._flow = functions if functions else self.__funcs
        start_time = time_ns()
        self.networks = [Network(**kwds, name=self.__name, topology=topology, messages=messages) for messages in self.messages_list]
        mid_time = time_ns()
        logging.info('generated all networks')
        _ = Network.execute(networks=self.networks)
        if Network._flow==self.__funcs: self.recv_msgs_list = kwds.get('decode', Network.decode)(networks=self.networks)
        logging.info(f'completed execution within {time_ns()-start_time-mid_time} ns')
        from .error_analyzer import ErrorAnalyzer
        self.full_err_list, self.mean_list, self.sd_list = list(zip(*ErrorAnalyzer.analyse(protocol=self)))
    
    def __repr__(self) -> str:
        string = ''
        for network in self:
            string+='Network:'+str(network._Network__name)+'\n'
            for node in network:
                string+='Memory keys of node:'+node.owner.name+'\n'
                for info in node.resource_manager.memory_manager:
                    state = network.manager.get(info.memory.qstate_key)
                    string+=str(state.keys)+'\t'+str(state.state)+'\n'
        return string
    
    @staticmethod
    def execute():
        pass