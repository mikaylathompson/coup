import coup

moneyEmoji = "💰"
cardEmoji = "🃏"

# Each of these takes up 3 rows:
# Name(s)
# Cards & coins (up to 4 coins)
# Extra coins

def printCenteredPlayer(playerState, width):
    print("{:^{width}}".format(playerState.name, width=width))
    if playerState.coins <= 4:
        line1 = (cardEmoji + ' ') * playerState.cards + (' ' + moneyEmoji) * playerState.coins
        line2 = ""
    else:
        line1 = (cardEmoji + ' ') * playerState.cards + (' ' + moneyEmoji) * 4
        line2 = '     ' + (' ' + moneyEmoji) * (playerState.coins - 4)
    print("{:^{width}}\n{:^{width}}".format(line1, line2,
                                            width=width))

def printLeftRightPlayers(leftPlayer, rightPlayer, width):
    midwidth = width // 2
    print('{:^{w}}{:^{w}}'.format(leftPlayer.name, rightPlayer.name, w=midwidth))
    if leftPlayer.coins <= 4:
        leftLine1 = (cardEmoji + ' ') * leftPlayer.cards + (' ' + moneyEmoji) * leftPlayer.coins
        leftLine2 = ""
    else:
        leftLine1 = (cardEmoji + ' ') * leftPlayer.cards + (' ' + moneyEmoji) * 4
        leftLine2 = (' ' + moneyEmoji) * (leftPlayer.coins - 4)
    if rightPlayer.coins <= 4:
        rightLine1 = (cardEmoji + ' ') * rightPlayer.cards + (' ' + moneyEmoji) * rightPlayer.coins
        rightLine2 = ""
    else:
        rightLine1 = (cardEmoji + ' ') * rightPlayer.cards + (' ' + moneyEmoji) * 4
        rightLine2 = (' ' + moneyEmoji) * (rightPlayer.coins - 4)
    print('{:^{w}}{:^{w}}\n{:^{w}}{:^{w}}'.format(leftLine1, rightLine1, leftLine2, rightLine2,
                                                  w=midwidth))

def printSelf(playerState, width):
    print('{:^{w}}'.format("YOU", w=width))
    for card in playerState.cards:
        print('{:^{w}}'.format(cardEmoji + ' ' + card.name, w=width))
    print('{:^{w}}'.format((moneyEmoji + ' ') * playerState.coins, w=width))

def printView(playerView):
    nOpps = len(playerView.opponents)
    # I'm pretty sure there's an elegant way to do this, but I'm not going to try to find it.
    width = 60
    print('\n')
    if nOpps == 1:
        printCenteredPlayer(playerView.opponents[0], width)
    elif nOpps == 2:
        printLeftRightPlayers(playerView.opponents[1], playerView.opponents[0], width)
    elif nOpps == 3:
        printCenteredPlayer(playerView.opponents[1], width)
        print()
        printLeftRightPlayers(playerView.opponents[2], playerView.opponents[0], width)
    elif nOpps == 4:
        printLeftRightPlayers(playerView.opponents[2], playerView.opponents[1], width)
        print()
        printLeftRightPlayers(playerView.opponents[3], playerView.opponents[0], width)
    elif nOpps == 5:
        printCenteredPlayer(playerView.opponents[2], width)
        print()
        printLeftRightPlayers(playerView.opponents[3], playerView.opponents[1], width)
        print()
        printLeftRightPlayers(playerView.opponents[4], playerView.opponents[0], width)
    print()
    printSelf(playerView.selfstate, width)
    print()

phrases = dict(
    income = "{p} took 1 coin as income and now has {n} coins.",
    foreign_aid = "{p} took 2 coins as foreign aid and now has {n} coins.",
    foreign_aid_blocked = "{p} tried to take foreign aid, but was blocked.",
    tax = "{p} took 3 coins as tax and now has {n} coins.",
    exchange = "{p} exchanged {n} cards.",
    steal = "{p} stole from {t} and now had {n} coins.",
    steal_blocked = "{p} tried to steal from {n}, but was blocked.",
    assassinate = "{p} assassinated {t}.",
    assassinate_blocked = "{p} tried to assassinate {t}, but was blocked.",
    coup = "{p} staged a coup on {t}.",
    eliminated = "{t} has been eliminated from the game."
)

class CLInteractiveAgent:
    def __init__(self, **kwargs):
        pass

    def selectAction(self, playerView):
        printView(playerView)
        try:
            action = coup.Action[input('Action? ').upper()]
        except:
            print("Invalid. Try again.")
            return self.selectAction(playerView)
        if action not in coup.findEligibleActions(playerView.selfstate):
            print("That's probably not a valid action.")
            proceed = input("Are you sure you want to continue? ")
            if 'y' not in proceed.lower():
                return self.selectAction(playerView)
        if action.name in ['ASSASSINATE', 'STEAL', 'COUP']:
            targetInput = input('Target? ')
            try:
                target = int(targetInput)
            except:
                target = next((i for i,o in enumerate(playerView.opponents) if o.name == targetInput))
        else:
            target = None

        return (action, target)


    def selectReaction(self, playerView, actionInfo):
        '''Select whether to block an action (usually directed at you)
        playerView is as described above.
        actionInfo is a tuple: (Action, ActivePlayer),
            where action is one of: Steal, Assassinate, Foreign_Aid

        Return True to block the action, False to allow it to occur.
        '''
        return False

    def selectExchangeCards(self, playerView, cards):
        '''Select which cards to keep, of the options presented.
        cards is a list of roles, from which you must discard two and keep the remainder.

        Return an ordered list of n or more cards (extras will be discarded), where n
        is the number of cards you have in your hand.
        '''
        return cards[:2]

    def selectKilledCard(self, playerView):
        '''Select which one of your cards must be discarded.

        Return the role of one card in your hand.
        '''
        return playerView.selfstate.cards[-1]

    def turnSummary(self, playerView, summary):
        if summary.activePlayer == -1:
            activePlayer = playerView.selfstate
        else:
            activePlayer = playerView.opponents[summary.activePlayer]

        if summary.action.name == 'INCOME':
            print(phrases['income'].format(p=summary.activeName, n=activePlayer.coins))
        elif summary.action.name == 'FOREIGN_AID':
            if summary.success:
                print(phrases['foreign_aid'].format(p=summary.activeName,
                                                    n=activePlayer.coins))
            else:
                print(phrases['foreign_aid_blocked'].format(p=summary.activeName))
        elif summary.action.name == 'TAX':
            print(phrases['tax'].format(p=summary.activeName, n=activePlayer.coins))
        elif summary.action.name == 'EXCHANGE':
            print(phrases['exchange'].format(p=activePlayer.name, n=activePlayer.cards))
        elif summary.action.name == 'STEAL':
            if summary.targetPlayer == -1:
                target = playerView.selfstate
            else:
                target = playerView.opponents[summary.targetPlayer]
                if target.name != summary.targetName:
                    target = None
            # print message.
            if summary.success:
                print(phrases['steal'].format(
                    p=summary.activeName, t=summary.targetName, n=activePlayer.coins))
            else:
                print(phrases['steal_blocked'].format(
                    p=summary.activeName, t=summary.targetName, n=activePlayer.coins))
        elif summary.action.name == 'ASSASSINATE':
            if summary.targetPlayer == -1:
                target = playerView.selfstate
            else:
                try:
                    target = playerView.opponents[summary.targetPlayer] 
                    if target.name != summary.targetName:
                        target = None
                except IndexError:
                    target = None

            if summary.success:
                print(phrases['assassinate'].format(p=summary.activeName,t=summary.targetName))
            else:
                print(phrases['assassinate_blocked'].format(p=summary.activeName,
                                                            t=summary.targetName))
            if target is None:
                print(phrases['eliminated'].format(t=summary.targetName))
        elif summary.action.name == 'COUP':
            if summary.targetPlayer == -1:
                target = playerView.selfstate
            else:
                try:
                    target = playerView.opponents[summary.targetPlayer] 
                    if target.name != summary.targetName:
                        target = None
                except IndexError:
                    target = None
            print(phrases['coup'].format(p=summary.activeName,t=summary.targetName))
            if target is None:
                print(phrases['eliminated'].format(t=summary.targetName))

