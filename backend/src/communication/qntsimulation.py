import inspect
import time
from functools import cached_property
from statistics import mean
from typing import (Any, Callable, Dict, Iterable, List, Optional, Self, Tuple,
                    Union)

from fibheap import makefheap
from qntsim.kernel.event import Event
from qntsim.kernel.quantum_manager import DensityManager

from .attack import ATTACK_TYPE, OnMemoryAttack
from .qntsim import QNtSim
from .utils import pass_values


class QNtSimulation(QNtSim):
    def __init__(self, topology:Union[str, Dict[str, Dict[str, Any]]], messages_list:List[Dict[Tuple[str], str]], **kwds) -> None:
        QNtSim.__init__(self=self, topology=topology, messages=messages_list[0], **kwds)
        self.interfaces = [self]
        self.interfaces.extend([QNtSimulation(topology=topology, messages_list=[messages], **kwds) for messages in messages_list[1:]])

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.events.push(event=Event(time=self.now(), owner=self, activation_method="", act_params=[]))
        self.__encode = kwds.pop("encode", self._teleport)
        for nodes in QNtSim.__iter__(self=self):
            src_node = nodes[0]
            dst_nodes = nodes[1:]
            for dst_node in dst_nodes:
                self.events.push(event=Event(time=self.now()+time.time(), activation_method=self.__encode, act_params=[self.nodes.get(src_node), self.nodes.get(dst_node)]))
                self.events.push(event=Event(time=self.now()+time.time(), owner=OnMemoryAttack, activation_method="implement", act_params=[self, None, ATTACK_TYPE[attack].value] if (attack := kwds.get("attack")) in ATTACK_TYPE.__members__ else pass_values))
        self.__measure = kwds.pop("measure", self._measure)
        self.events.push(event=Event(time=self.now()+time.time(), activation_method=self.__measure, act_params=[]))
        if (event_queue := kwds.get("event_queue")):
            self.events = makefheap()
            self.events.event_nodes = []
            for event in event_queue:
                setattr(self, event[0].__name__, event[0])
                self.events.push(event=Event(time=self.now()+time.time(), owner=self, activation_method=event[0].__name__, act_params=event[1:]))
        self.run()
        self.is_running = False

    def decode_and_analyse(self, decode_func:Optional[Callable[..., List[Dict[Tuple[str], str]]]] = None):
        for qcomm_event in self: qcomm_event()
        self.recv_msg_list = (decode_func or self.decode)(interfaces=self.interfaces)
        from .error_analyzer import ErrorAnalyzer
        self.err_mat, self.leak_mat, self.mean_err_list, self.sd_list, self.mean_leak_list, self.mean_fid_list = ErrorAnalyzer.analyse(event_generator=self)

        return self.recv_msg_list, mean(self.mean_err_list), mean(self.sd_list), mean(self.mean_leak_list), mean(self.mean_fid_list)

    def __iter__(self) -> Iterable[Self]:
        return iter(self.interfaces)

    # def __next__(self):
        
    
    @staticmethod
    def execute(topology:Dict, app_settings:Dict):
        response = {}
        netcor = QNtSimulation(name="network", topology=topology)
        recv_msgs, avg_err, std_dev, info_leak, msg_fidelity = netcor()
        return response