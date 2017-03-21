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
    TAX = auto()
    ASSASSINATE = auto()
    STEAL = auto()
    EXCHANGE = auto()
    COUP = auto()

class Reaction(Enum):
    BLOCK_FOREIGN_AID = auto()
    BLOCK_ASSASSINATION = auto()
    BLOCK_STEAL = auto()


universal_actions = [Action.INCOME, Action.FOREIGN_AID, Action.COUP]

available_actions = {
        Role.DUKE: universal_actions + [Action.TAX, Reaction.BLOCK_FOREIGN_AID],
        Role.ASSASSIN: universal_actions + [Action.ASSASSINATE],
        Role.CONTESSA: universal_actions + [Reaction.BLOCK_ASSASSINATION],
        Role.AMBASSADOR: universal_actions + [Action.EXCHANGE, Reaction.BLOCK_STEAL],
        Role.CAPTAIN: universal_actions + [Action.STEAL, Reaction.BLOCK_STEAL]
}

action_expense = {
        Action.INCOME: 0,
        Action.FOREIGN_AID: 0,
        Action.TAX: 0,
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


def findEligibleActions(playerState):
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


def canAffordAction(playerState, action):
    '''Returns true if a player can afford an action.
    Additionally, returns false if a player has more than 10 coins
        and the action is not coup.
    '''
    return playerState.coins >= action_expense[action] and \
                action == Action.COUP if playerState.coins > 10 else True


def removeCard(playerState, card, replacement=None):
    ''' Remove a card from a players hand, and (possibly) replace it with a new one.
    The player's new state is returned.
    If the card is not in the player's hand, an arbitrary card from their hand will be taken.
    If they are left with 0 cards, and no replacement, None will be returned.
    '''
    if card not in playerState.cards:
        # You didn't follow the rules, so I get to take any card.
        card = playerState.cards[-1]

    cards = playerState.cards[:] # make copy to preserve immutability
    cards.remove(card)
    if replacement:
        cards.append(replacement)
    if len(cards) == 0:
        return None
    return playerState._replace(cards=cards)

def getCardsFromDeck(gameState, nCards):
    '''Basically, sample without replacement from the game deck.
    Returns the cards, and the updated gameState.
    '''
    deck = random.sample(gameState.deck, len(gameState.deck))
    cards = []
    for _ in range(nCards):
        cards.append(deck.pop())
    return cards, gameState._replace(deck=deck)

def applyIncome(gameState, activePlayer):
    playerList = gameState.players[:]
    player = playerList[activePlayer]
    playerList[activePlayer] = player._replace(coins = player.coins + 1)
    return gameState._replace(players=playerList)

def applyForeignAid(gameState, activePlayer):
    playerList = gameState.players[:]
    # All opponents get the opporunity to block
    blockAttempt = [opp.agent.selectReaction(getPlayerView(gameState, i),
                                             (Action.FOREIGN_AID, (activePlayer - i) % len(playerList)))
                        for i, opp in enumerate(playerList) if opp is not player]
    if not any(blockAttempt):
        player = player._replace(coins = player.coins + 2)

    playerList[activePlayer] = player
    return gameState._replace(players=playerList)

def applyTax(gameState, activePlayer):
    playerList = gameState.players[:]
    player = playerList[activePlayer]
    playerList[activePlayer] = player._replace(coins = player.coins + 3)
    return gameState._replace(players=playerList)

def applySteal(gameState, activePlayer, targetPlayer):
    playerList = playerList[:]
    player = playerList[activePlayer]
    target = playerList[targetPlayer]
    # Target gets the opportunity to block:
    blockAttempt = target.agent.selectReaction(getPlayerView(gameState, targetPlayer),
                                    (Action.STEAL, (activePlayer - targetPlayer) % len(playerList)))
    if not blockAttempt:
        targetCoins = max(target.coins - 2, 0) # target cannot have negative coins.
        delta = target.coins - targetCoins
        playerList[activePlayer] = player._replace(coins = player.coins + delta)
        playerList[targetPlayer] = target._replace(coins = targetCoins)
    return gameState._replace(players=playerList)

def applyAssassinate(gameState, activePlayer, targetPlayer):
    playerList = playerList[:]
    player = playerList[activePlayer]
    target = playerList[targetPlayer]
    # Player must pay for assassination
    playerList[activePlayer] = player._replace(coins = player.coins - 3)

    # Target gets the opportunity to block:
    blockAttempt = target.agent.selectReaction(getPlayerView(gameState, targetPlayer),
                                (Action.ASSASSINATE, (activePlayer - targetPlayer) % len(playerList)))
    if not blockAttempt:
        # Target gets opportunity to select which card is killed.
        target = removeCard(target,
                            target.agent.selectKilledCard(getPlayerView(gameState, targetPlayer)))
        if target:
            playerList[targetPlayer] = target
        else:
            # Target was knocked out of game.
            playerList.pop(targetPlayer)
    return gameState._replace(players=playerList)

def applyCoup(gameState, activePlayer, targetPlayer):
    playerList = playerList[:]
    player = playerList[activePlayer]
    target = playerList[targetPlayer]
    # Player must pay for assassination
    player = player._replace(coins = player.coins - 7)
    target = removeCard(target,
                        target.agent.selectKilledCard(getPlayerView(gameState, targetPlayer)))
    if target:
        playerList[targetPlayer] = target
    else:
        playerList.pop(targetPlayer)
    return gameState._replace(players=playerList)

def applyExchange(gameState, activePlayer):
    # Select two cards from deck.
    # Offer agent these two + their current cards.
    offers, gameState = getCardsFromDeck(gameState, 2)
    offers += player.cards
    selected = player.agent.selectExchangeCards(getPlayerView(gameState, activePlayer), offers)
    selected = selected[:len(player.cards)]
    # Set hand to selected cards, and return remaining to deck.
    for i, card in enumerate(selected):
        # re-cast card to a Role in case enums are being absurd.
        card = Role[card.name]
        try:
            offers.remove(card)
        except:
            # If this failed, its because the player selected a card they don't have.
            # So I'm going to give them an arbitrary card from the ones they were offered.
            selected[i] = offers.pop()

    playerList[activePlayer] = player._replace(cards=selected)
    return gameState._replace(players=playerList, deck=gameState.deck + offers)

# Return the new gameState after a player takes an action
def applyAction(gameState, activePlayer, action, targetPlayer=None):
    # WHY DO I HAVE TO DO THIS?!?!
    action = Action[action.name]

    playerList = gameState.players[:]
    player = playerList[activePlayer]
    assert canAffordAction(player, action)

    if action == Action.INCOME:
        return applyIncome(gameState, activePlayer)

    elif action == Action.FOREIGN_AID:
        return applyForeignAid(gameState, activePlayer)

    elif action == Action.TAX:
        return applyTax(gameState, activePlayer)

    elif action == Action.STEAL:
        return applySteal(gameState, activePlayer, targetPlayer)

    elif action == Action.EXCHANGE:
        return applyExchange(gameState, activePlayer)

    elif action == Action.ASSASSINATE:
        return applyAssassinate(gameState, activePlayer, targetPlayer)

    elif action == Action.COUP:
        return applyCoup(gameState, activePlayer, targetPlayer)


# Set up an initial gameState for the list of agents.
def dealGame(deck, agents):
    random.shuffle(deck)
    return GameState(players=[PlayerState(coins=2,
                                          cards=deck[i*2:i*2+2],
                                          agent=a,
                                          name="{name}-{i}".format(name=str(type(a)).split("'")[1].split(".")[-1], i=i))
                                    for i, a in enumerate(agents)],
                    deck=deck[len(agents)+2:])


def printState(gameState):
    for i, player in enumerate(gameState.players):
        print(f"{player.name}\tCoins: {player.coins}\tCards: {[card.name for card in player.cards]}")
        print()
    print()


def randomGameLoop(agents, humanInput=False):
    baseDeck = [Role.DUKE, Role.ASSASSIN, Role.CONTESSA, Role.AMBASSADOR, Role.CAPTAIN] * 3

    initalState = dealGame(baseDeck, agents)
    gameState = initalState
    turns = 0
    while len(gameState.players) > 1:
        if (turns > 1000):
            return None
        if humanInput:
            printState(gameState)
        i = turns % len(gameState.players)
        # print(turns, gameState.players[i].name)
        player = gameState.players[i].agent
        action, relativeTarget = player.selectAction(getPlayerView(gameState, i))
        if relativeTarget is not None:
            target = (i + relativeTarget + 1) % len(gameState.players)
        else:
            target = None
        if humanInput:
            print(f"Action: {action} directed at target {target} by Player {gameState.players[i].name}")
        gameState = applyAction(gameState, i, action, target)
        turns += 1
        if humanInput:
            x = input().strip()
            if x == 'q':
                return
    winner_name = gameState.players[0].name
    print("WINNER: ", winner_name)
    if 'Sean'in winner_name:
        print("SEAN WON")
    return(winner_name.split('-')[0])


if __name__ == "__main__":
    from agents.bots import *
    from agents.cli import CLInteractiveAgent
    from statistics import mean
    from collections import Counter

    # agentList = [SeanAgent(), BayBot(), MrtBot()]
    # for i in range(5):
    #     randomGameLoop(agentList, humanInput=True)

    winners = []
    for i in range(1000):
        agentList = [SeanAgent(), BayBot(), MrtBot(), RandomAgent()]
        random.shuffle(agentList)
        winners.append(randomGameLoop(agentList, humanInput=False))

    print("Done.")
    c = Counter(winners)
    for val, winner in c.most_common(5):
        print(val, '\t', winner)


