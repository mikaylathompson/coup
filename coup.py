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

class Reactions(Enum):
    BLOCK_FOREIGN_AID = auto()
    BLOCK_ASSASINATION = auto()
    BLOCK_STEAL = auto()


universal_actions = [Action.INCOME, Action.FOREIGN_AID, Action.COUP]

available_actions = dict(
        Role.DUKE = universal_actions + [Action.DUKE_MONEY, Reactions.BLOCK_FOREIGN_AID],
        Role.ASSASSIN = universal_actions + [Action.ASSASSINATE],
        Role.CONTESSA = universal_actions + [Reactions.BLOCK_ASSASINATION],
        Role.AMBASSADOR = universal_actions + [Action.EXCHANGE, Reactions.BLOCK_STEAL],
        Role.CAPTAIN = universal_actions + [Action.STEAL, Reactions.BLOCK_STEAL]
)



namedtuple('PlayerState',
        ['cards', 'coins'])

namedtuple('GameState',
        ['players', 'deck'])
