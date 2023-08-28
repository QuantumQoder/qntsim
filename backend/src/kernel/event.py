"""Definition of the Event class.

This module defines the Event class, which is executed by the timeline.
Events should be scheduled through the timeline to take effect.
"""

import math
from functools import partial
from types import NoneType
from typing import (TYPE_CHECKING, Any, Callable, List, Optional, Self, Type,
                    Union, overload)

if TYPE_CHECKING:
    from .process import Process


class Event:
    @overload
    def __init__(self, time:int, activation_method:Callable[..., NoneType], act_params:List[Any], priority:float = math.inf, **kwds) -> None: ...

    @overload
    def __init__(self, time:int, owner:Type, activation_method:str, act_params:List[Any], priority:float = math.inf) -> None: ...
    
    def __init__(self,
                 time: int,
                 owner: Optional[Type] = None,
                 activation_method: Union[str, Callable[..., NoneType]] = "",
                 act_params: List[Any] = [],
                 priority:float = math.inf,
                 **kwds) -> None:
        assert (isinstance(activation_method, str) if owner else
                callable(activation_method)), ("If owner is provided, then activation_method should of type 'str'." if owner else
                                               "Without any owner, activation_method should be of type 'Callable'.")
        self.time = time
        self._is_removed = False
        self.owner = owner
        self.activation = activation_method if owner else partial(activation_method, **kwds)
        self.act_params = act_params
        self.priority = priority

    def __eq__(self, another:Self) -> bool:
        return (self.time == another.time) and (self.priority == another.priority)

    def __ne__(self, another:Self) -> bool:
        return (self.time != another.time) or (self.priority != another.priority)

    def __gt__(self, another:Self) -> bool:
        return (self.time > another.time) or (self.time == another.time and self.priority > another.priority)

    def __lt__(self, another:Self) -> bool:
        return (self.time < another.time) or (self.time == another.time and self.priority < another.priority)

        
    def run(self) -> None:
        return (getattr(self.owner, self.activation) if self.owner else self.activation)(*self.act_params)

    






