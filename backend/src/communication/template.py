from abc import ABC, abstractclassmethod
from typing import Any, Dict, Tuple
from qntsim.library import Network

class Party(ABC):
    """Abstract base class for a party in a communication network."""

    id = str
    messages = Dict[Tuple, str]
    rcvd_msgs = Dict[int, str]
    
    @abstractclassmethod
    def encode(cls, network: Network, returns: Any):
        """
        Abstract class method for encoding a message to be sent over the network.
        
        Args:
            network (Network): The communication network.
            returns (Any): Returns from the previous function call.
            
        Returns:
            The encoded message.
        """
        pass
    
    @abstractclassmethod
    def decode(cls, network: Network, returns: Any):
        """
        Abstract class method for decoding a received message from the network.
        
        Args:```
            network (Network): The communication network.
            returns (Any): Returns from the previous function call.
            
        Returns:
            The decoded message.
        """
        pass
    
    @abstractclassmethod
    def measure(cls, network:Network, returns:Any):
        """
        Abstract class method for performing measurements on qubits.
        
        Args:
            network (Network): The communication network.
            returns (Any): Returns from the previous function call.
            
        Returns:
            The measurement outcomes.
        """
        pass