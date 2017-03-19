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

# PlayerState is the description of a particular player's state at a given time.
# Cards is a list of roles, coins is an integer number of coins.
PlayerState = namedtuple('PlayerState', ['cards', 'coins', 'agent'])

# GameState is the state of an entire game.
# Players is a list of PlayerStates for all active players (dead players are dropped)
# Deck is the shuffled list of roles remaining in the deck.
GameState = namedtuple('GameState', ['players', 'deck'])

# PlayerView is a the view of a game from a single players perspective.
# Selfstate is the PlayerState of the active player.
# Oppenent is a list of PlayerStates of the other players, but cards is an int, not a list.
PlayerView = namedtuple('PlayerView', ['selfstate', 'opponents'])


def find_eligible_actions(playerState):
    if playerState.coins >= 10:
        return set(Action.COUP)

    return set([act for card in playerState.cards for act in available_actions[card]
                    if (isinstance(act, Action) and action_expense[act] <= playerState.coins)])



def getPlayerView(gameState, activePlayer):
    return PlayerView(selfstate=gameState.players[activePlayer],
            opponents= list(map(lambda x: x._replace(cards=len(x.cards), agent=None),
                    gameState.players[activePlayer+1:] + gameState.players[:activePlayer])))


# Return the new gameState after a player takes an action
def apply_action(gameState, activePlayer, action, targetPlayer=None):
    playerList = gameState.players[:]
    player = playerList.pop(activePlayer)
    assert action in find_eligible_actions(player)

    if action == Action.INCOME:
        player = player._replace(coins = player.coins + 1)
        playerList.insert(activePlayer, player)
        return gameState._replace(players=playerList)

    elif action == Action.FOREIGN_AID:
        # Opportunity to block goes here.
        player = player._replace(coins = player.coins + 2)
        playerList.insert(activePlayer, player)
        return gameState._replace(players=playerList)

    elif action == Action.DUKE_MONEY:
        player = player._replace(coins = player.coins + 3)
        playerList.insert(activePlayer, player)
        return gameState._replace(players=playerList)

    elif action == Action.STEAL:
        # opportunity to block goes here
        target = playerList.pop(targetPlayer + (0 if targetPlayer < activePlayer else 1))
        player = player._replace(coins = player.coins + 2)
        target = target._replace(coins = target.coins- 2)
        playerList.insert(activePlayer - (0 if activePlayer > targetPlayer else 1), player)
        playerList.insert(targetPlayer, target)
        return gameState._replace(players=playerList)



if __name__ == "__main__":
    assert find_eligible_actions(PlayerState(cards=[Role.DUKE], coins=0, agent=None)) == \
            {Action.INCOME, Action.FOREIGN_AID, Action.DUKE_MONEY}

    assert find_eligible_actions(PlayerState(cards=[Role.CAPTAIN], coins=0, agent=None)) ==\
            {Action.INCOME, Action.FOREIGN_AID, Action.STEAL}

    assert find_eligible_actions(PlayerState(cards=[Role.CONTESSA, Role.DUKE], coins=0, agent=None)) ==\
            {Action.INCOME, Action.FOREIGN_AID, Action.DUKE_MONEY}

    assert find_eligible_actions(PlayerState(cards=[Role.ASSASSIN], coins=8, agent=None)) ==\
            {Action.INCOME, Action.FOREIGN_AID, Action.ASSASSINATE, Action.COUP}


    p1 = PlayerState(cards=[Role.CONTESSA], coins=0)
    p2 = PlayerState(cards=[Role.DUKE], coins=0)
    gameState = GameState(players=[p1, p2], deck=[])
    print(apply_action(gameState, 0, Action.INCOME))
    print(apply_action(gameState, 1, Action.DUKE_MONEY))

    print(getPlayerView(gameState, 0))
    print(getPlayerView(gameState, 1))

