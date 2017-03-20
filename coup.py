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
    BLOCK_ASSASSINATION = auto()
    BLOCK_STEAL = auto()


universal_actions = [Action.INCOME, Action.FOREIGN_AID, Action.COUP]

available_actions = {
        Role.DUKE: universal_actions + [Action.DUKE_MONEY, Reaction.BLOCK_FOREIGN_AID],
        Role.ASSASSIN: universal_actions + [Action.ASSASSINATE],
        Role.CONTESSA: universal_actions + [Reaction.BLOCK_ASSASSINATION],
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


class GameState(object):
    '''
    GameState is the state of an entire game.
    self.players is a list of PlayerStates for all active players (dead players are dropped)
    self.deck is the shuffled list of roles remaining in the deck.
    '''

    def __init__(self, deck, agents):
        '''Deal the game from inputs'''
        random.shuffle(deck)
        self.deck = deck[len(agents)+2:]
        self.players = [PlayerState(coins=2, cards=deck[i*2:i*2+2], agent=a, name=f"{type(a)}-{i}") for i, a in enumerate(agents)]

    def __repr__(self):
        '''Allows for print(gamestate)'''
        game_str = '{}: \n'.format(self.__class__.__name__)
        for i, player in enumerate(self.players):
            game_str += 'Coins: {}\tCards: {}\n'.format(player.coins, [card.name for card in player.cards])
        game_str += '\n'
        return game_str

    def apply_action(self, activePlayer, action, targetPlayer=None):
        '''Apply a specific action by a given player (sometimes targeting another player)

        Note: this changes the state of this object.
        '''

        # WHY DO I HAVE TO DO THIS?!?!
        action = Action[action.name]

        if action in {Action.STEAL, Action.ASSASSINATE, Action.COUP}:
            if targetPlayer is None:
                raise ValueError('A target player must be specifed for a {} action'.format(action.name))

        if action == Action.INCOME:
            self._income_handler(activePlayer)
        elif action == Action.FOREIGN_AID:
            self._foriegn_aid_handler(activePlayer)
        elif action == Action.DUKE_MONEY:
            self._duke_money_handler(activePlayer)
        elif action == Action.STEAL:
            self._steal_handler(activePlayer, targetPlayer)
        elif action == Action.EXCHANGE:
            self._exchange_handler(activePlayer)
        elif action == Action.ASSASSINATE:
            self._assassinate_handler(activePlayer, targetPlayer)
        elif action == Action.COUP:
            self._coup_handler(activePlayer, targetPlayer)
        else:
            raise ValueError('Action {} not supported'.format(action.name))

    def get_player_view(self, activePlayer):
        '''Get a representation of the game from the perspective of a given player'''
        opponents = list(map(lambda x: x._replace(cards=len(x.cards), agent=None),
                    self.players[activePlayer+1:] + self.players[:activePlayer]))
        return PlayerView(selfstate=self.players[activePlayer], opponents=opponents)

    # Private methods

    def _income_handler(self, activePlayer):
        playerList = self.players[:]
        player = playerList[activePlayer]
        player = player._replace(coins = player.coins + 1)
        playerList[activePlayer] =  player
        self.players = playerList

    def _foriegn_aid_handler(self, activePlayer):
        playerList = self.players[:]
        player = playerList[activePlayer]

        # All opponents get the opportunity to block
        blockAttempt = [opp.agent.selectReaction(self.get_player_view(i),
                                              (Action.FOREIGN_AID, activePlayer))
                                            for i, opp in enumerate(playerList) if opp is not player]
        if not any(blockAttempt):
            player = player._replace(coins = player.coins + 2)

        playerList[activePlayer] = player
        self.players = playerList

    def _duke_money_handler(self, activePlayer):
        playerList = self.players[:]
        player = playerList[activePlayer]
        player = player._replace(coins = player.coins + 3)
        playerList[activePlayer] = player
        self.players = playerList

    def _steal_handler(self, activePlayer, targetPlayer):
        playerList = self.players[:]
        player = playerList[activePlayer]
        target = playerList[targetPlayer]

        # Target gets the opportunity to block:
        blockAttempt = target.agent.selectReaction(self.get_player_view(targetPlayer),
                                    (Action.STEAL, activePlayer)) #should adjust for relative position
        if not blockAttempt:
            newTargetCoins = max(target.coins - 2, 0)
            delta = target.coins - newTargetCoins
            player = player._replace(coins = player.coins + delta)
            target = target._replace(coins = newTargetCoins)
        playerList[activePlayer] = player
        playerList[targetPlayer] = target
        self.players = playerList

    def _exchange_handler(self, activePlayer):
        playerList = self.players[:]
        player = playerList[activePlayer]

        # Select two cards from deck.
        deck = random.sample(self.deck, len(self.deck))
        # Offer agent these two + their current cards.
        offers = [deck.pop(), deck.pop()] + player.cards
        selected = player.agent.selectExchangeCards(self.get_player_view(activePlayer), offers)
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

        self.players = playerList
        self.deck = deck + offers

    def _assassinate_handler(self, activePlayer, targetPlayer):
        playerList = self.players[:]
        player = playerList[activePlayer]
        target = playerList[targetPlayer]

        # Player must pay for assassination
        player = player._replace(coins = player.coins - 3)
        # Target gets the opportunity to block:
        blockAttempt = target.agent.selectReaction(self.get_player_view(targetPlayer),
                                    (Action.ASSASSINATE, activePlayer)) #should adjust for relative position
        if not blockAttempt:
            # Assasination will go forward. Target now gets to select card.
            killedCard = target.agent.selectKilledCard(self.get_player_view(targetPlayer))
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

        self.players = playerList

    def _coup_handler(self, activePlayer, targetPlayer):
        playerList = self.players[:]
        player = playerList[activePlayer]

        target = playerList[targetPlayer]
        # Player must pay for assassination
        player = player._replace(coins = player.coins - 7)
        killedCard = target.agent.selectKilledCard(self.get_player_view(targetPlayer))
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

        self.players = playerList


def randomGameLoop(agents, humanInput=False):
    baseDeck = [Role.DUKE, Role.ASSASSIN, Role.CONTESSA, Role.AMBASSADOR, Role.CAPTAIN] * 3

    gameState = GameState(baseDeck, agents)
    initial_players = gameState.players
    turns = 0
    while len(gameState.players) > 1:
        if (turns > 1000):
            return None
        if humanInput:
            printState(gameState)
        i = turns % len(gameState.players)
        player = gameState.players[i].agent
        action, relativeTarget = player.selectAction(gameState.get_player_view(i))
        if relativeTarget is not None:
            target = (i + relativeTarget + 1) % len(gameState.players)
        else:
            target = None
        if humanInput:
            print(f"Action: {action} directed at target {target} by Player {gameState.players[i].name}")
        gameState.apply_action(i, action, target)
        turns += 1
        if humanInput:
            x = input().strip()
            if x == 'q':
                return
    winner_name = gameState.players[0].name
    print("WINNER: ", winner_name)
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




