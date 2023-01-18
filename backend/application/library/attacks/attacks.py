from enum import Enum

from ..attacks import qiskit_attacks, qntsim_attacks

class Attack(Enum):
    qiskit = qiskit_attacks.Attack
    qntsim = qntsim_attacks.Attack
