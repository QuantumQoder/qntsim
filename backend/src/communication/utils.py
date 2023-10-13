from copy import deepcopy
from typing import Any, Dict, Tuple

from ..log_functions import log_info
from ..types import Types

__is_binary: Dict[str, bool] = {}

def to_binary(message_packets: Types.messages) -> Types.messages:
    global __is_binary
    __is_binary = {package.get("receiver", ""): all(char in "01"
                                                    for char in package.get("message", ""))
                   for packet in message_packets
                   for package in packet.values()
                   if isinstance(package, dict)}
    binary_packets: Types.messages = deepcopy(message_packets)
    for binary_packet in binary_packets:
        for binary_message, is_binary in zip(binary_packet.values(), __is_binary):
            if not is_binary and "message" in binary_message:
                binary_message["message"] = "".join("{:08b}".format(ord(char)) for char in binary_message.get("message"))
    log_info("converted messages to binary")
    return binary_packets

def to_characters(binary_packets: Types.messages) -> Types.messages:
    global __is_binary
    message_packets: Types.messages = deepcopy(binary_packets)
    for packet in message_packets:
        package = packet.get("output_message", {})
        package = {key: binary if __is_binary.get(key) else "".join("{:c}".format(int(binary[8 * i: 8 * (i + 1)], 2)) for i in range(len(binary) // 8))
                   for key, binary in package.items()}
    log_info("converted messages to string")
    return message_packets

def pass_values(_, returns:Any, *args, **kwds) -> Tuple[Any, Tuple[Any], Dict[str, Any]]:
    """A do-nothing funciton which passes the arguments from the previous call to the next call

    Args:
        _ (_type_): Ignored arguement
        returns (Any): Returns from the previous function call

    Returns:
        Tuple[Any, Tuple[Any], Dict]: Passes to the next function call
    """
    return returns, args, kwds