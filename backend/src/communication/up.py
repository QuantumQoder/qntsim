from typing import Any, Dict

from ..kernel._event import Event


class CONetR:
    def __init__(self, topology:Dict, name:str=None) -> None:
        self.__name = name or __class__.__name__

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass
    
    @staticmethod
    def execute(topology:Dict, app_settings:Dict):
        response = {}
        netcor = CONetR(name="network", topology=topology)
        recv_msgs, avg_err, std_dev, info_leak, msg_fidelity = netcor()
        return response