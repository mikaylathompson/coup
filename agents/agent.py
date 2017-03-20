# Base Agent.
# Custom AIs inherent from this and implement methods.
class BaseAgent:
    def __init__(self, **kwargs):
        pass

    def selectAction(self, playerView):
        '''Select an action on your turn
        playerView is a namedtuple with selfstate and opponents.
        Selfstate contains your coins & cards.
        Opponents is a list of your opponents (in their order relative to you)
            with their number of coins and number of cards.

        Return a tuple: (action, target), where action is a Action enum member
        and target is None for a victimless action and the index of the target
        in your playerView.opponents list otherwise.
        '''
        pass

    def selectReaction(self, playerView, actionInfo):
        '''Select whether to block an action (usually directed at you)
        playerView is as described above.
        actionInfo is a tuple: (Action, ActivePlayer),
            where action is one of: Steal, Assassinate, Foreign_Aid

        Return True to block the action, False to allow it to occur.
        '''
        pass

    def selectExchangeCards(self, playerView, cards):
        '''Select which cards to keep, of the options presented.
        cards is a list of roles, from which you must discard two and keep the remainder.

        Return an ordered list of n or more cards (extras will be discarded), where n
        is the number of cards you have in your hand.
        '''
        pass

    def selectKilledCard(self, playerView):
        '''Select which one of your cards must be discarded.

        Return the role of one card in your hand.
        '''
        pass

