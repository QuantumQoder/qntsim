import logging
from typing import Dict, Tuple


def string_to_binary(messages: Dict[Tuple, str]):
    """Converts any character string to their binary equivalent.
    Args:
        messages (Dict[Tuple, str]): Dictionary of messages to be converted into binary.

    Returns:
        strings (List[str]): List of binary equivalent of the input messages

    Example:
        print(string_to_binary(messages={(1, 2):'h'}))
    """
    # strings = [''.join('0'*(8-len(bin(ord(char))[2:]))+bin(ord(char))[2:] for char in message) for _, message in messages.items()]
    strings = [
        "".join("{:08b}".format(ord(char)) for char in message)
        for message in messages.values()
    ]
    logging.info("converted")

    return strings
