from enum import Enum, auto
from collections import namedtuple


class Role(Enum):
    DUKE = auto()
    ASSASSIN = auto()
    CONTESSA = auto()
    AMBASSADOR = auto()
    CAPTAIN = auto()

class Action(Enum):
    INCOME = auto()
    FOREIGN_AID = auto()
    ASSASSINATE = auto()
    STEAL = auto()
    EXCHANGE = auto()
    COUP = auto()


namedtuple('PlayerState',
        ['cards', 'coins'])

namedtuple('GameState',
        ['players', 'deck'])
