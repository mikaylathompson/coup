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
    DUKE_MONEY = auto()
    ASSASSINATE = auto()
    STEAL = auto()
    EXCHANGE = auto()
    COUP = auto()

class Reactions(Enum):
    BLOCK_FOREIGN_AID = auto()
    BLOCK_ASSASINATION = auto()
    BLOCK_STEAL = auto()


universal_actions = [Action.INCOME, Action.FOREIGN_AID, Action.COUP]

available_actions = {
        Role.DUKE: universal_actions + [Action.DUKE_MONEY, Reactions.BLOCK_FOREIGN_AID],
        Role.ASSASSIN: universal_actions + [Action.ASSASSINATE],
        Role.CONTESSA: universal_actions + [Reactions.BLOCK_ASSASINATION],
        Role.AMBASSADOR: universal_actions + [Action.EXCHANGE, Reactions.BLOCK_STEAL],
        Role.CAPTAIN: universal_actions + [Action.STEAL, Reactions.BLOCK_STEAL]
}

action_expense = {
        Action.INCOME: 0,
        Action.FOREIGN_AID: 0,
        Action.DUKE_MONEY: 0,
        Action.ASSASSINATE: 3,
        Action.STEAL: 0,
        Action.EXCHANGE: 0,
        Action.COUP: 7
}


def find_eligible_actions(playerState):
    return set([act for card in playerState.cards for act in available_actions[card] if (isinstance(act, Action) and action_expense[act] <= playerState.coins)])


# PlayerState is the description of a particular player's state at a given time.
# Cards is a list of roles, coins is an integer number of coins.
PlayerState = namedtuple('PlayerState', ['cards', 'coins'])

# GameState is the state of an entire game.
# Players is a list of PlayerStates for all active players (dead players are dropped)
# Deck is the shuffled list of roles remaining in the deck.
GameState = namedtuple('GameState', ['players', 'deck'])




if __name__ == "__main__":
    assert find_eligible_actions(PlayerState(cards=[Role.DUKE], coins=0)) == \
            {Action.INCOME, Action.FOREIGN_AID, Action.DUKE_MONEY}

    assert find_eligible_actions(PlayerState(cards=[Role.CAPTAIN], coins=0)) ==\
            {Action.INCOME, Action.FOREIGN_AID, Action.STEAL}

