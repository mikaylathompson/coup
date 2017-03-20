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
        action = random.sample(action_list, 1)[0]

        if action in [coup.Action.ASSASSINATE, coup.Action.COUP]:
            target = random.randint(1, (len(playerView.opponents)))
        elif action == coup.Action.STEAL: 
            try:
                target = random.choice([i+1 for i, opp in enumerate(playerView.opponents) if opp.coins >= 2])
            except IndexError:
                # No opponents, retry
                return self.selectAction(playerView)
        else:
            target = None
        return (action, target)

    # Returns a blocking reaction if possible.
    def selectReaction(self, playerView, actionInfo):
        reactions = set([act for card in playerView.selfstate.cards for act in coup.available_actions[coup.Role[card.name]]
                        if isinstance(act, coup.Reaction)])

        if actionInfo[0].name == "STEAL":
            if coup.Reaction.BLOCK_STEAL in reactions:
                return True
            return None
        elif actionInfo[0].name == "ASSASSINATE":
            if coup.Reaction.BLOCK_ASSASINATION in reactions:
                return True
            return None
        elif actionInfo[0].name == "FOREIGN_AID":
            if len(list(filter(lambda x: x.name == 'BLOCK_FOREIGN_AID', reactions))):
                return True
            return None

    # Returns a random selection of cards.
    def selectExchangeCards(self, playerView, cards):
        return random.sample(cards, len(playerView.selfstate.cards))

    # Returns a random card from hand.
    def selectKilledCard(self, playerView):
        return random.choice(playerView.selfstate.cards)
