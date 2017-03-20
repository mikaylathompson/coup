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
            target = random.randint(0, (len(playerView.opponents)) - 1)
        elif action == coup.Action.STEAL: 
            try:
                target = random.choice([i for i, opp in enumerate(playerView.opponents) if opp.coins >= 2])
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



class BayBot(BaseAgent):

    # ordered preference for cards
    card_preferences = [
        "DUKE",
        "CONTESSA",
        "CAPTAIN",
        "ASSASSIN",
        "AMBASSADOR"
    ]

    # ordered preference for actions 
    action_preferences = [
        "ASSASINATE",
        "COUP",
        "EXCHANGE", 
        "DUKE_MONEY",
        "STEAL",
        "INCOME",
        "FOREIGN_AID"
    ]


    def selectAction(self, playerView):

        # return first legal action by preference
        action_list = coup.find_eligible_actions(playerView.selfstate)
        action_names = list(map(lambda x: x.name, action_list))
        action = [i for i in self.action_preferences if (i in action_names)][0]
        action = coup.Action[action]

        # quit here, if no need to target
        if not action.name in ["ASSASSINATE", "COUP", "STEAL"]:
            return (action, None)

        #otherwise, proceed with targeting

        # sort players by strength, mapping to tuples w/ original index
        opps = list(enumerate(playerView.opponents))
        opps.sort(key=lambda x: (x[1].cards*10 + x[1].coins))
        opps.reverse()

        # default is to attack strongest player
        target = opps[0][0]

        # TODO: unless stealing, in which case choose strongest player 
        #       w/ at least 2 coins who has not blocked you before
       
        return (action, target)


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

    def selectExchangeCards(self, playerView, cards):
        ordered_cards = sorted(cards, key=lambda x: self.card_preferences.index(x.name))
        return ordered_cards[:len(playerView.selfstate.cards)]   

    # Returns a random card from hand.
    def selectKilledCard(self, playerView):
        ordered_cards = sorted(playerView.selfstate.cards, key=lambda x: self.card_preferences.index(x.name))
        return ordered_cards[-1]   

      
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
        card_nums = [card.value for card in cards]
        mycards = playerView.selfstate.cards
        if len(mycards) == 1:
            if coup.Role.CONTESSA.value in card_nums:
                return [coup.Role.CONTESSA]
            if coup.Role.DUKE.value in card_nums:
                return [coup.Role.DUKE]
            if coup.Role.CAPTAIN.value in card_nums:
                return [coup.Role.CAPTAIN]
            if coup.Role.AMBASSADOR.value in card_nums:
                return [coup.Role.AMBASSADOR]
            if coup.Role.ASSASSIN.value in card_nums:
                return [coup.Role.ASSASSIN]
            return random.sample(cards, len(playerView.selfstate.cards))

        # Ordering of best
        if coup.Role.DUKE.value in card_nums and coup.Role.CONTESSA.value in card_nums:
            return [coup.Role.DUKE, coup.Role.CONTESSA]
        if coup.Role.CAPTAIN.value in card_nums and coup.Role.DUKE.value in card_nums:
            return [coup.Role.CAPTAIN, coup.Role.DUKE]
        if coup.Role.CAPTAIN.value in card_nums and coup.Role.CONTESSA.value in card_nums:
            return [coup.Role.CAPTAIN, coup.Role.CONTESSA]
        if coup.Role.DUKE.value in card_nums and coup.Role.ASSASSIN.value in card_nums:
            return [coup.Role.DUKE, coup.Role.ASSASSIN]
        if coup.Role.DUKE.value in card_nums and coup.Role.AMBASSADOR.value in card_nums:
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





