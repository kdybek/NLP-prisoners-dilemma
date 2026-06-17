from typing import Tuple, List
from enum import Enum


class Action(Enum):
    COOPERATE = 0
    DEFECT = 1


GameHistory = List[Tuple[Action, Action]]
