"""Definition of abstract message type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


@dataclass(slots=True)
class Message:
    """
     Abstract message used by entanglement management protocols.
    """
    receiver_type: Enum
    receiver: Enum
    msg_type: Enum
    kwargs: Dict[str, Any] = field(dict, kw_only=True)