import coup

import random

# Base Agent.
# Custom AIs inherent from this and implement methods.
class BaseAgent:
    def __init__(self):
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
        action_list = coup.find_eligible_actions(playerView.selfstate)
        print("Considered actions: ", action_list)
        action = random.sample(action_list, 1)[0]
        if action in [coup.Action.STEAL, coup.Action.ASSASSINATE, coup.Action.COUP]:
            target = random.randint(0, (len(playerView.opponents)) -1)
        else:
            target = None
        return (action, target)

    # Returns a blocking reaction if possible.
    def selectReaction(self, playerView, actionInfo):
        reactions = set([act for card in playerView.selfstate.cards for act in coup.available_actions[coup.Role[card.name]]
                        if isinstance(act, coup.Reaction)])
        if actionInfo[0] == coup.Action.STEAL:
            if Reaction.BLOCK_STEAL in reactions:
                return Reaction.BLOCK_STEAL
            return None
        elif actionInfo[0] == coup.Action.ASSASSINATE:
            if Reaction.BLOCK_ASSASINATION in reactions:
                return Reaction.BLOCK_ASSASINATION
            return None
        elif actionInfo[0] == coup.Action.FOREIGN_AID:
            if Reaction.BLOCK_FOREIGN_AID in reactions:
                return Reaction.BLOCK_FOREIGN_AID
            return None

    # Returns a random selection of cards.
    def selectExchangeCards(self, playerView, cards):
        return random.sample(cards, len(playerView.selfstate.cards))

    # Returns a random card from hand.
    def selectKilledCard(self, playerView):
        return random.choice(playerView.selfstate.cards)
