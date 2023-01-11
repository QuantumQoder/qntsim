from enum import Enum

from qntsim.library.attacks import qiskit_attacks, qntsim_attacks

class Attack(Enum):
    qiskit = qiskit_attacks.Attack
    qntsim = qntsim_attacks.Attack
