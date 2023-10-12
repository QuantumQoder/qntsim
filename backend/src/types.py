from typing import (Any, Callable, Dict, List, Literal, NamedTuple, TypeAlias,
                    Union)


class Types(NamedTuple):
    topology: TypeAlias = Union[str, Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]]]
    backend: TypeAlias = Literal["qiskit", "qutip", "density"]
    encoding: TypeAlias = Literal["polarization", "time_bin", "single_atom"]
    messages: TypeAlias = List[Dict[str, Union[Dict[str, str], str, Union[int, Callable[..., int]]]]]