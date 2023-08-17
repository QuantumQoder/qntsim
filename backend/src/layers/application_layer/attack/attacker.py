from typing import Any, Callable, Dict, List, Optional, Self, Union
import deepcopy
import json5
import numpy as np

from backend.src.core.kernel.timeline import Timeline
from backend.src.core.topology.node import Node
from backend.src.layers.physical_layer.components.photon import Photon

from ....core.topology.node import BSMNode, EndNode, ServiceNode
from ....utils import encoding
from ...physical_layer.components.optical_channel import QuantumChannel
from ...physical_layer.components.waveplates import QuarterWaveplate, Waveplate
from ..communication import Communication, Network
from .attack import Attack

class Attacker(ServiceNode, QuantumChannel):
    """A class representing an attacker node in a quantum communication network."""

    def __init__(self, name: str, timeline: Timeline, memo_size: Optional[int], attack: Optional[Union[Callable, str]]):
        """
        Initialize an Attacker node.

        Args:
            name (str): Name of the attacker node.
            timeline (Timeline): Timeline of the quantum communication network.
            memo_size (int, optional): Size of the memory for the attacker node.
            attack (Callable or str, optional): The attack strategy to be used.
        """
        self.__attack = attack or "DS"
        super().__init__(name, timeline, memo_size or 500)

    def attack(self, qubit: Photon) -> Optional[Photon]:
        """
        Apply an attack on the input qubit.

        Args:
            qubit (Photon): The input qubit.

        Returns:
            Optional[Photon]: The modified qubit after applying the attack.
        """
        encoder = getattr(encoding, qubit.encoding_type)
        bases = encoder.get("bases")
        match self.__attack:
            case "DS": #Denial of service
                qubit.random_noise()
            case "EM": #Entangle and measure
                photon = deepcopy(qubit)
                photon.set_state(state=bases[0][0])
                qubit.entangle(photon=photon)
                Photon.measure(basis=bases[0], photon=photon)
            case "IR": #Intercept and Response
                photon = deepcopy(qubit)
                photon.set_state(state=(basis := bases[np.random.randint(2)])[Photon.measure(basis=basis, photon=qubit)])
                return photon
            case Callable():
                return self.__attack(qubit)

    # Other methods can have similar docstrings

    @classmethod
    def modify_topology(cls, topology: Union[str, Dict[str, Dict[str, Any]]], insert_locations: Optional[List[List[str]]], attack: Optional[Union[Callable, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """Modify the topology of the communication network by adding attacker nodes."""
        # ...

    @staticmethod
    def _modify_new_topology(topology: Dict[str, List[Dict[str, Any]]], insert_locations: List[List[str]], attack: Optional[Union[Callable, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """Modify the topology with new attacker nodes."""
        # ...

    # Other classmethods and staticmethods can have similar docstrings
