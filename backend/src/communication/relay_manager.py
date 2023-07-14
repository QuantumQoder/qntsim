import inspect
from statistics import mean
import time
from typing import Any, Dict, List, Self, Tuple

from fibheap import makefheap

from ..kernel._event import Event
from ..kernel.quantum_manager import QuantumManagerDensity
from .attack import ATTACK_TYPE, Attack
from .communication import Communication
from .utils import pass_returns


class RelayManager(Communication):
    def __init__(self, topology:Dict | List[Dict], messages_list:List[Dict[Tuple[str], str]], **kwds) -> None:
        Communication.__init__(self=self, topology=topology, messages=messages_list[0], **kwds)
        self.networks = [self]
        stack = inspect.stack()
        caller = stack[1][0].f_locals.get("self").__class__
        if caller != __class__:
            self.networks.extend([RelayManager(topology=topology, messages_list=[messages], **kwds) for messages in messages_list[1:]])

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.events.push(event=Event(time=self.now(), owner=self, activation_method="", act_params=[]))
        setattr(self, "__encode", kwds.get("encode", self._teleport))
        for nodes in self._bin_strs:
            src_node = nodes[0]
            dst_nodes = nodes[1:]
            for dst_node in dst_nodes:
                self.events.push(event=Event(time=self.now()+time.time(), owner=self, activation_method="__encode", act_params=[None, self.__topology.nodes.get(src_node), self.__topology.nodes.get(dst_node)]))
                self.events.push(event=Event(time=self.now()+time.time(), owner=Attack, activation_method="implement", act_params=[self, None, ATTACK_TYPE[attack].value] if (attack := kwds.get("attack")) in ATTACK_TYPE.__members__ else pass_returns))
        setattr(self, "__measure", kwds.get("measure", self._meas_all))
        self.events.push(event=Event(time=self.now()+time.time(), owner=self, activation_method="__measure", act_params=[]))
        if (event_queue := kwds.get("event_queue")):
            self.events.data = makefheap()
            self.events.data_list = []
            self.events.nodesl = []
            for event in event_queue:
                setattr(self, event[0].__name__, event[0])
                self.events.push(event=Event(time=self.now()+time.time(), owner=self, activation_method=event[0].__name__, act_params=event[1:]))
        self.run()
        for network in self:
            network.is_running = False
        self.recv_msg_list = kwds.get("decode", self.decode)(networks=self.networks)
        from .error_analyzer import ErrorAnalyzer
        self.err_mat, self.leak_mat, self.mean_err_list, self.sd_list, self.mean_leak_list, self.mean_fid_list = ErrorAnalyzer.analyse(protocol=self)

        return self.recv_msg_list, mean(self.mean_err_list), mean(self.sd_list), mean(self.mean_leak_list), mean(self.mean_fid_list)

    def __iter__(self):
        return iter(self.networks)

    # def __next__(self):
        
    
    @staticmethod
    def execute(topology:Dict, app_settings:Dict):
        response = {}
        netcor = RelayManager(name="network", topology=topology)
        recv_msgs, avg_err, std_dev, info_leak, msg_fidelity = netcor()
        return response