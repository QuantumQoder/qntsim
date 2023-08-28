import logging
from typing import Any, Dict, List, Tuple, TypeAlias

__msg_type:TypeAlias = Dict[Tuple[str], str]

def to_binary(msg_dict:__msg_type) -> Tuple[bool, __msg_type]:
    """Converts any character string to their binary equivalent.
    Args:
        messages (List[str]): Messages to be converted into binary.

    Returns:
        strings (List[str]): Binary equivalents of the input messages

    Example:
        # print(to_binary(messages={('n1', 'n2'):'h'})
    """
    __is_binary = all(char in "01" for message in msg_dict.values() for char in message)
    binary_strings = msg_dict if __is_binary else {node_seq:"".join("{:08b}".format(ord(char)) for char in message) for node_seq, message in msg_dict.items()}
    logging.info("converted")
    return __is_binary, binary_strings

def to_characters(bin_dict:__msg_type, __was_binary:bool) -> __msg_type:
    """Converts any binary string to their character equivalent.

    Args:
        bin_dict (__msg_type): Binary strings to be converted into character strings
        __was_binary (bool): If the input was previously binary.
        NOTE: For an independent use of the function, set __was_binary = False

    Returns:
        __msg_type: Messages converted from the binary strings
    """
    messages = bin_dict if __was_binary else {node_seq:"".join("{:c}".format(int(binary[8*i:8*(i+1)], 2)) for i in range(len(binary)//8)) for node_seq, binary in bin_dict.items()}
    return messages

def pass_values(_, returns:Any, *args, **kwds) -> Tuple[Any, Tuple[Any], Dict]:
    """A do-nothing funciton which passes the arguments from the previous call to the next call

    Args:
        _ (_type_): Ignored arguement
        returns (Any): Returns from the previous function call

    Returns:
        Tuple[Any, Tuple[Any], Dict]: Passes to the next function call
    """
    return returns, args, kwds