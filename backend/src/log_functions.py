"""This module provides logging functions to be logged into the logger.
TODO: Currently the logs are printed with the log level. Once, the logger
      has been setup, convert the prints to proper logs and use the log module
      from rich library.
"""

import os
from typing import TYPE_CHECKING

from rich import print

from .utils import log

if TYPE_CHECKING:
    from .kernel.event import Event
    from .kernel.kernel_utils import EventList
    from .message import Message

log.set_logger_level("debug")
log.set_logger("out", "out.log")

def log_debug(debug_msg: str):
    log.logger.debug(debug_msg)
    print(f"[green]DEBUG[/green]: {debug_msg}\n")

def log_info(info_msg: str):
    log.logger.debug(info_msg)
    print(f"[blue]INFO[/blue]: {info_msg}\n")

def log_entry_point(_class:type, method_name:str) -> None:
    log_debug(f" \t\t\t\t [b green]in {_class.__name__}.{method_name}[/b green]")

def log_schedule_event(event: "Event", event_heap: "EventList") -> None:
    log_info(f" [i yellow]scheduling event:{len(event_heap.event_nodes) + 1} {event}[/i yellow]")

def log_function_call(obj:object, method_name:str) -> None:
    log_debug(f" \t\t\t\t [uu red]calling {obj.__class__.__name__}.{method_name}[/uu red]")

def log_message(msg: "Message") -> None:
    log_debug(f" {msg}")

def log_object(obj:object) -> None:
    log_debug(f" [bold yellow on green]{obj}")

def log_event_list(events:"EventList") -> None:
    log_info(f" {events}")

def log_start(_class:type) -> None:
    # TODO: Centralized the string. Refer to rich documentation
    log_info(f" \t\t\t\t\t\t [bold yellow on red blink]Starting {_class.__name__}[/bold yellow on red blink]")

def log_object_instantiation(obj:object) -> None:
    log_debug(f" [bold italic yellow on red]instantiating {obj.__class__.__name__}[/bold italic yellow on red]")