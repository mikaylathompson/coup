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
    assert card in playerState.cards
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


# Return the new gameState after a player takes an action
def applyAction(gameState, activePlayer, action, targetPlayer=None):
    # WHY DO I HAVE TO DO THIS?!?!
    action = Action[action.name]

    playerList = gameState.players[:]
    player = playerList[activePlayer]

    assert canAffordAction(player, action)

    if action == Action.INCOME:
        player = player._replace(coins = player.coins + 1)
        playerList[activePlayer] =  player
        return gameState._replace(players=playerList)

    elif action == Action.FOREIGN_AID:
        # All opponents get the opportunity to block
        blockAttempt = [opp.agent.selectReaction(getPlayerView(gameState, i),
                                              (Action.FOREIGN_AID, (activePlayer - i) % len(playerList)))
                                            for i, opp in enumerate(playerList) if opp is not player]
        if not any(blockAttempt):
            player = player._replace(coins = player.coins + 2)

        playerList[activePlayer] = player
        return gameState._replace(players=playerList)

    elif action == Action.TAX:
        player = player._replace(coins = player.coins + 3)
        playerList[activePlayer] = player
        return gameState._replace(players=playerList)

    elif action == Action.STEAL:
        target = playerList[targetPlayer]

        # Target gets the opportunity to block:
        blockAttempt = target.agent.selectReaction(getPlayerView(gameState, targetPlayer),
                                    (Action.STEAL, (activePlayer - targetPlayer) % len(playerList)))
        if not blockAttempt:
            # Verify/adjust the number of coins being stolen.
            newTargetCoins = max(target.coins - 2, 0)
            delta = target.coins - newTargetCoins
            player = player._replace(coins = player.coins + delta)
            target = target._replace(coins = newTargetCoins)
        playerList[activePlayer] = player
        playerList[targetPlayer] = target
        return gameState._replace(players=playerList)

    elif action == Action.EXCHANGE:
        # Select two cards from deck.
        # Offer agent these two + their current cards.
        offers = random.sample(gameState.deck, 2) + player.cards # TODO: I added a bug where this now doesn't remove the chosen cards from the deck
        selected = player.agent.selectExchangeCards(getPlayerView(gameState, activePlayer), offers)
        selected = selected[:len(player.cards)]

        # Set hand to selected cards, and return remaining to deck.
        for card in selected:
            try:
                offers.remove(card)
            except Exception:
                # Handle Enum issues by forcing usage of values
                offer_values = [offer.value for offer in offers]
                if card.value in offer_values:
                    offer_values.remove(card.value)
                    # Rebuild offers
                    offers = [Role(value) for value in offer_values]
                else:
                    # This shouldn't happen
                    raise
        playerList[activePlayer] = player._replace(cards=selected)
        return gameState._replace(players=playerList, deck=deck + offers)

    elif action == Action.ASSASSINATE:
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

    elif action == Action.COUP:
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


# Set up an initial gameState for the list of agents.
def dealGame(deck, agents):
    random.shuffle(deck)
    return GameState(players=[PlayerState(coins=2,
                                          cards=deck[i*2:i*2+2],
                                          agent=a,
                                          name=f"{type(a)}-{i}")
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
    from agents import *
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


