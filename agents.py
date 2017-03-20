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



class SeanAgent(RandomAgent):

    def selectAction(self, playerView):
        action_list = coup.find_eligible_actions(playerView.selfstate)

        # This is in order of desirability
        # More effort here?
        action = coup.Action.INCOME
        if coup.Action.DUKE_MONEY in action_list:
            action = coup.Action.DUKE_MONEY
        if coup.Action.STEAL in action_list:
            action = coup.Action.STEAL
        if coup.Action.ASSASSINATE in action_list:
            action = coup.Action.ASSASSINATE
        if coup.Action.COUP in action_list:
            action = coup.Action.COUP

        # Exchange if we are doing a weak income move
        if action.value == coup.Action.INCOME.value:
            if coup.Action.EXCHANGE in action_list:
                action = coup.Action.EXCHANGE

        if action.value == coup.Action.INCOME.value:
            # Choose foreign aid once in a while randomly
            if random.random() > 0.5:
                action = coup.Action.FOREIGN_AID

        if action in [coup.Action.ASSASSINATE, coup.Action.COUP]:
            target = random.randint(1, (len(playerView.opponents)))
        elif action == coup.Action.STEAL:
            try:
                target = random.choice([i+1 for i, opp in enumerate(playerView.opponents) if opp.coins >= 2])
            except IndexError:
                action = coup.Action.INCOME
                if coup.Action.DUKE_MONEY in action_list:
                    action = coup.Action.DUKE_MONEY
                target = None
        else:
            target = None
        return (action, target)

    def selectExchangeCards(self, playerView, cards):
        import pdb; pdb.set_trace()

        cards = [card.value for card in cards]

        mycards = playerView.selfstate.cards
        if len(mycards) == 1:
            if coup.Role.CONTESSA.value in cards:
                return [coup.Role.CONTESSA]
            if coup.Role.DUKE.value in cards:
                return [coup.Role.DUKE]
            if coup.Role.CAPTAIN.value in cards:
                return [coup.Role.CAPTAIN]
            if coup.Role.AMBASSADOR.value in cards:
                return [coup.Role.AMBASSADOR]
            if coup.Role.ASSASSIN.value in cards:
                return [coup.Role.ASSASSIN]
            return random.sample(cards, len(playerView.selfstate.cards))

        # Ordering of best
        if coup.Role.DUKE.value in cards and coup.Role.CONTESSA.value in cards:
            return [coup.Role.DUKE, coup.Role.CONTESSA]
        if coup.Role.CAPTAIN.value in cards and coup.Role.DUKE.value in cards:
            return [coup.Role.CAPTAIN, coup.Role.DUKE]
        if coup.Role.CAPTAIN.value in cards and coup.Role.CONTESSA.value in cards:
            return [coup.Role.CAPTAIN, coup.Role.CONTESSA]
        if coup.Role.DUKE.value in cards and coup.Role.ASSASSIN.value in cards:
            return [coup.Role.DUKE, coup.Role.ASSASSIN]
        if coup.Role.DUKE.value in cards and coup.Role.AMBASSADOR.value in cards:
            return [coup.Role.DUKE, coup.Role.AMBASSADOR]
        return random.sample(cards, len(playerView.selfstate.cards))

    def selectKilledCard(self, playerView):
        og_cards = playerView.selfstate.cards
        if len(og_cards) == 1:
            # SAD WE LOST
            return og_cards[0]

        cards = [card.value for card in og_cards]

        i = self._save_role(coup.Role.CONTESSA, cards)
        if i >= 0:
            return og_cards[i]
        i = self._save_role(coup.Role.DUKE, cards)
        if i >= 0:
            return og_cards[i]
        i = self._save_role(coup.Role.CAPTAIN, cards)
        if i >= 0:
            return og_cards[i]
        i = self._save_role(coup.Role.ASSASSIN, cards)
        if i >= 0:
            return og_cards[i]

        return random.choice(playerView.selfstate.cards)

    def _save_role(self, role, cards):
        try:
            i = cards.index(role.value)
        except ValueError:
            return -1
        else:
            return 0 if i == 1 else 1










