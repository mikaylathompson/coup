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



class RandomAgent(BaseAgent):
    def selectAction(self, playerView):
        return random.choice(find_eligible_actions(playerView.selfstate))

    def selectReaction(self, playerView, actionInfo):
        return None

    def selectExchangeCards(self, playerView, cards):
        return random.sample(cards, len(playerView.selfstate.cards))
