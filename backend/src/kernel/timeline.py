"""Definition of main Timeline class.

This module defines the Timeline class, which provides an interface for the simulation kernel and drives event execution.
All entities are required to have an attached timeline for simulation.
"""

import time
from typing import TYPE_CHECKING, List, Literal

from ..utils import log
from .kernel_utils import EventList
# from .quantum_kernel import QuantumKernel
# from .quantum_manager import DensityManager
from .quantum import QuantumManager

if TYPE_CHECKING:
    from .entity import Entity


class Timeline:
    DLCZ: bool = False
    BK: bool = False

    def __init__(self, stop_time: float = -1, backend: Literal["qiskit", "qutip", "density"] = "qutip") -> None:
        self.events = EventList()
        self.entities: List["Entity"] = []
        self.time: float = 0
        self.stop_time = stop_time
        self.schedule_counter: int = 0
        self.run_counter: int = 0
        self._is_running = False
        self.backend = backend.lower()
        self.quantum_manager = QuantumManager(self.backend)
        # match formalism:
        #     case "ket": self.quantum_manager = QuantumKernel(backend)
        #     case "density": self.quantum_manager = DensityManager()
        #     case _: raise ValueError(f"Invalid formalism {formalism}")

    def __repr__(self) -> str:
        return f"Timeline(current_time = {self.time}, stop_time = {self.stop_time}, total_events = {len(self.events)}, executed_events = {self.run_counter}, scheduled_events = {self.schedule_counter}, quantum_manager = {self.quantum_manager.__class__.__name__})\n{self.events}"

    def now(self) -> float:
        """Returns current simulation time."""
        return self.time

    def init(self) -> None:
        """Method to initialize all simulated entities."""
        log.logger.info("Timeline initial network")
        for entity in self.entities: entity.init()

    def run(self, show_progress: bool = False) -> None:
        """Main simulation method.

        The `run` method begins simulation of events.
        Events are continuously popped and executed, until the simulation time limit is reached or events are exhausted.
        A progress bar may also be displayed, if the `show_progress` flag is set.
        """
        log.logger.info("Timeline start simulation")
        start: float = time.time()
        self._is_running = True
        for event in self.events:
            event.run()
            self.time = event.time
            self.run_counter += 1
        self._is_running = False
        stop: float = time.time()

    def stop(self) -> None:
        """Method to stop simulation."""
        log.logger.info("Timeline is stopped")
        self.stop_time = self.now()