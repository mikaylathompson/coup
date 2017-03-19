import coup

import random

# Base Agent.
# Custom AIs inherent from this and implement methods.
class BaseAgent:
    def __init__(self, playerView):
        pass

    def selectAction(self, playerView):
        pass

    def selectReaction(self, playerView, actionInfo):
        pass

    def selectExchangeCards(self, playerView, cards):
        pass

    def selectKilledCard(self, playerView):
        pass



class RandomAgent(BaseAgent):
    # Returns a random eligible action.
    def selectAction(self, playerView):
        return random.choice(coup.find_eligible_actions(playerView.selfstate))

    # Returns a blocking reaction if possible.
    def selectReaction(self, playerView, actionInfo):
        reactions = set([act for card in playerState.cards for act in available_actions[card]
                        if isinstance(act, Reaction)])
        if actionInfo[0] == Action.STEAL:
            if Reaction.BLOCK_STEAL in reactions:
                return Reaction.BLOCK_STEAL
            return None
        elif actionInfo[0] == Action.ASSASSINATE:
            if Reaction.BLOCK_ASSASINATION in reactions:
                return Reaction.BLOCK_ASSASINATION
            return None
        elif actionInfo[0] == Action.FOREIGN_AID:
            if Reaction.BLOCK_FOREIGN_AID in reactions:
                return Reaction.BLOCK_FOREIGN_AID
            return None

    # Returns a random selection of cards.
    def selectExchangeCards(self, playerView, cards):
        return random.sample(cards, len(playerView.selfstate.cards))

    # Returns a random card from hand.
    def selectKilledCard(self, playerView):
        return random.choice(playerView.selfstate.cards)
