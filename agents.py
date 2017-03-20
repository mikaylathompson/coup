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


class MrtBot(RandomAgent):
    def selectAction(self, playerView):
        action_list = list(map(lambda x: x.name, coup.find_eligible_actions(playerView.selfstate)))
        if "COUP" in action_list:
            # COUP SOMEONE
            for i, opp in enumerate(playerView.opponents):
                if opp.cards == 2 and opp.coins >= 7:
                    return (coup.Action.COUP, i)

            for i, opp in enumerate(playerView.opponents):
                if opp.coins >= 6:
                    return (coup.Action.COUP, i)

            for i, opp in enumerate(playerView.opponents):
                if opp.cards == 2:
                    return (coup.Action.COUP, i)
            return (coup.Action.COUP, 0)

        if "ASSASSINATE" in action_list:
            for i, opp in enumerate(playerView.opponents):
                if opp.cards == 2 and opp.coins >= 7:
                    return (coup.Action.ASSASSINATE, i)

            for i, opp in enumerate(playerView.opponents):
                if opp.coins >= 6:
                    return (coup.Action.ASSASSINATE, i)

            for i, opp in enumerate(playerView.opponents):
                if opp.cards == 2:
                    return (coup.Action.ASSASSINATE, i)
            return (coup.Action.ASSASSINATE, 0)

        if "DUKE_MONEY" in action_list:
            return (coup.Action.DUKE_MONEY, None)

        if "EXCHANGE" in action_list:
            return (coup.Action.EXCHANGE, None)
        return (coup.Action.INCOME, None)


    def selectExchangeCards(self, playerView, cards):
        cardnames = list(map(lambda x: x.name, cards))
        selects = []
        n_to_select = len(playerView.selfstate.cards)
        while len(selects) < n_to_select:
            if "ASSASSIN" in cardnames:
                selects.append(coup.Role.ASSASSIN)
                cardnames.remove("ASSASIN")
            if "CONTESSA" in cardnames:
                selects.append(coup.Role.CONTESSA)
                cardnames.remove("CONTESSA")
            if "DUKE" in cardnames:
                selects.append(coup.Role.DUKE)
                cardnames.remove("DUKE")
            if len(selects) == 0:
                break
        if "CAPTAIN" in cardnames:
                selects.append(coup.Role.CAPTAIN)
        if "AMBASSADOR" in cardnames:
                selects.append(coup.Role.AMBASSADOR)
        print(selects[:n_to_select])
        return selects[:n_to_select]

    def selectKilledCard(self, playerView):
        if len(playerView.selfstate.cards) == 1:
            return playerView.selfstate.cards[0]
        cardnames = list(map(lambda x: x.name, playerView.selfstate.cards))
        if 'AMBASSADOR' in cardnames:
            return coup.Role.AMBASSADOR
        if 'CAPTAIN' in cardnames:
            return coup.Role.CAPTAIN
        if 'DUKE' in cardnames:
            return coup.Role.DUKE
        if 'ASSASSIN' in cardnames:
            return coup.Role.ASSASSIN
        return coup.Role.CONTESSA












