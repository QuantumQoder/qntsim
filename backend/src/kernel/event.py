"""Definition of the Event class.

This module defines the Event class, which is executed by the timeline.
Events should be scheduled through the timeline to take effect.
"""

from functools import partial
from typing import Any, Callable, List, Optional, Union, overload

from fibheap import Node


class Event(Node):
    @overload
    def __init__(self, time: float, owner: type, activation_method: str, act_params: List[Any] = [], priority: float = 0) -> None: ...

    @overload
    def __init__(self, time: float, activation_method: Callable[..., None], act_params: List[Any] = [], priority: float = 0, **kwds) -> None: ...
    
    def __init__(self, time: float, owner: Optional[type] = None, activation_method: Union[str, Callable[..., None]] = "", act_params: List[Any] = [], priority: float = 0, **kwds) -> None:
        Node.__init__(self, (time, priority))
        self.time = time
        self.owner = owner
        self.activation = activation_method if owner else partial(activation_method, **kwds)
        self.act_params = act_params
        self.priority = priority

    def run(self) -> None:
        (getattr(self.owner, self.activation) if self.owner else self.activation)(*self.act_params)

    def __repr__(self) -> str:
        return f"Event(time = {self.time}, owner = {self.owner}, method = {self.activation}, parameters = {self.act_params}, priority = {self.priority})"