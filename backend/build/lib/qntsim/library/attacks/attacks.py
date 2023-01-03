from enum import Enum

from qntsim.library.attacks import qntsim_attacks

class Attack(Enum):

    qntsim = qntsim_attacks.Attack
