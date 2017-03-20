from enum import Enum, auto
from collections import namedtuple
import random

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

class Reaction(Enum):
    BLOCK_FOREIGN_AID = auto()
    BLOCK_ASSASINATION = auto()
    BLOCK_STEAL = auto()


universal_actions = [Action.INCOME, Action.FOREIGN_AID, Action.COUP]

available_actions = {
        Role.DUKE: universal_actions + [Action.DUKE_MONEY, Reaction.BLOCK_FOREIGN_AID],
        Role.ASSASSIN: universal_actions + [Action.ASSASSINATE],
        Role.CONTESSA: universal_actions + [Reaction.BLOCK_ASSASINATION],
        Role.AMBASSADOR: universal_actions + [Action.EXCHANGE, Reaction.BLOCK_STEAL],
        Role.CAPTAIN: universal_actions + [Action.STEAL, Reaction.BLOCK_STEAL]
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
PlayerState = namedtuple('PlayerState', ['cards', 'coins', 'agent', 'name'])

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
        return set([Action.COUP])
    try:
        cards = playerState.cards
        return set([act for card in cards for act in available_actions[card]
                    if (isinstance(act, Action) and action_expense[act] <= playerState.coins)])
    except KeyError:
        # Who knows why I have to do this???
        cards = list(map(lambda x: Role[x.name], playerState.cards))
        return set([act for card in cards for act in available_actions[card]
                    if (isinstance(act, Action) and action_expense[act] <= playerState.coins)])




def getPlayerView(gameState, activePlayer):
    return PlayerView(selfstate=gameState.players[activePlayer],
            opponents = list(map(lambda x: x._replace(cards=len(x.cards), agent=None),
                    gameState.players[activePlayer+1:] + gameState.players[:activePlayer])))


# Return the new gameState after a player takes an action
def apply_action(gameState, activePlayer, action, targetPlayer=None):

    # WHY DO I HAVE TO DO THIS?!?!
    action = Action[action.name]

    playerList = gameState.players[:]
    player = playerList[activePlayer]

    if action == Action.INCOME:
        player = player._replace(coins = player.coins + 1)
        playerList[activePlayer] =  player
        return gameState._replace(players=playerList)

    elif action == Action.FOREIGN_AID:
        # All opponents get the opportunity to block
        blockAttempt = [opp.agent.selectReaction(getPlayerView(gameState, i),
                                              (Action.FOREIGN_AID, activePlayer))
                                            for i, opp in enumerate(playerList) if opp is not player]
        if not any(blockAttempt):
            player = player._replace(coins = player.coins + 2)

        playerList[activePlayer] = player
        return gameState._replace(players=playerList)

    elif action == Action.DUKE_MONEY:
        player = player._replace(coins = player.coins + 3)
        playerList[activePlayer] = player
        return gameState._replace(players=playerList)

    elif action == Action.STEAL:
        target = playerList[targetPlayer]

        # Target gets the opportunity to block:
        blockAttempt = target.agent.selectReaction(getPlayerView(gameState, targetPlayer),
                                    (Action.STEAL, activePlayer)) #should adjust for relative position
        if not blockAttempt:
            player = player._replace(coins = player.coins + 2)
            target = target._replace(coins = target.coins- 2)
        playerList[activePlayer] = player
        playerList[targetPlayer] = target
        return gameState._replace(players=playerList)

    elif action == Action.EXCHANGE:
        # Select two cards from deck.
        deck = random.sample(gameState.deck, len(gameState.deck))
        # Offer agent these two + their current cards.
        offers = [deck.pop(), deck.pop()] + player.cards
        selected = player.agent.selectExchangeCards(getPlayerView(gameState, activePlayer), offers)
        selected = selected[:len(player.cards)]

        # Set hand to selected cards, and return remaining to deck.
        print("Offers are: ", offers)
        for c in selected:
            offers.remove(c)
        playerList[activePlayer] = player._replace(cards=selected)
        return gameState._replace(players=playerList, deck=deck + offers)

    elif action == Action.ASSASSINATE:
        target = playerList[targetPlayer]
        # Player must pay for assassination
        player = player._replace(coins = player.coins - 3)
        # Target gets the opportunity to block:
        blockAttempt = target.agent.selectReaction(getPlayerView(gameState, targetPlayer),
                                    (Action.ASSASSINATE, activePlayer)) #should adjust for relative position
        if not blockAttempt:
            # Assasination will go forward. Target now gets to select card.
            killedCard = target.agent.selectKilledCard(getPlayerView(gameState, targetPlayer))
            newCards = list(set(target.cards) - set([killedCard]))

            if len(newCards) != len(target.cards) - 1:
                newCards = target.cards[:-1]

            if len(newCards) == 0:
                # target has been knocked out of game. Do not re-add them to gameState
                playerList[activePlayer] = player
                playerList.pop(targetPlayer)
            else:
                # target is still in game.
                playerList[activePlayer] = player
                playerList[targetPlayer] = target._replace(cards=newCards)
        else:
            # Assasination was blocked, just re-add players
            playerList[activePlayer] = player
            playerList[targetPlayer] = target
        return gameState._replace(players=playerList)

    elif action == Action.COUP:
        target = playerList[targetPlayer]
        # Player must pay for assassination
        player = player._replace(coins = player.coins - 7)
        killedCard = target.agent.selectKilledCard(getPlayerView(gameState, targetPlayer))
        newCards = list(set(target.cards) - set([killedCard]))

        if len(newCards) != len(target.cards) - 1:
            newCards = target.cards[:-1]

        if len(newCards) == 0:
            # target has been knocked out of game. Do not re-add them to gameState
            playerList[activePlayer] = player
            playerList.pop(targetPlayer)
        else:
            # target is still in game.
            playerList[activePlayer] = player
            playerList[targetPlayer] = target._replace(cards=newCards)
        return gameState._replace(players=playerList)


# Set up an initial gameState for the list of agents.
def dealGame(deck, agents):
    random.shuffle(deck)
    return GameState(players=[PlayerState(coins=2, cards=deck[i*2:i*2+2], agent=a, name=f"{type(a)}-{i}") for i, a in enumerate(agents)],
                    deck=deck[len(agents)+2:])


def printState(gameState):
    for i, player in enumerate(gameState.players):
        print(f"{player.name}\tCoins: {player.coins}\tCards: {[card.name for card in player.cards]}")
        print()
    print()


def randomGameLoop(agents):
    baseDeck = [Role.DUKE, Role.ASSASSIN, Role.CONTESSA, Role.AMBASSADOR, Role.CAPTAIN] * 3

    initalState = dealGame(baseDeck, agents)
    gameState = initalState
    turns = 0
    while len(gameState.players) > 1:
        printState(gameState)
        i = turns % len(gameState.players)
        player = gameState.players[i].agent
        action, relativeTarget = player.selectAction(getPlayerView(gameState, i))
        if relativeTarget is not None:
            target = (i + relativeTarget + 1) % len(gameState.players)
        else:
            target = None
        print(f"Action: {action} directed at target {target} by Player {gameState.players[i].name}")
        gameState = apply_action(gameState, i, action, target)
        turns += 1
        x = input().strip()
        if x == 'q':
            return
    winner_name = gameState.players[0].name
    print("WINNER: ", winner_name)


if __name__ == "__main__":
    from agents import RandomAgent, BayBot
    from statistics import mean
    from collections import Counter


    randomGameLoop([RandomAgent()] * 2 + [BayBot()])

    # winners = []
    # for i in range(1000):
    #     _, winningHand = randomGameLoop([RandomAgent()] * 3)
    #     winners.append(frozenset(winningHand))

    # for i in range(1000):
    #     _, winningHand = randomGameLoop([RandomAgent()] * 4)
    #     winners.append(frozenset(winningHand))

    # for i in range(1000):
    #     _, winningHand = randomGameLoop([RandomAgent()] * 5)
    #     winners.append(frozenset(winningHand))

    # c = Counter(winners)

    # for hand, count in c.most_common(5):
    #     print(count, '\t', hand)

    # print()
    # allCounts = c.most_common(len(c.keys()))
    # for hand, count in allCounts[::-1][:10]:
    #     print(count, '\t', hand)
    # print(len(allCounts))




