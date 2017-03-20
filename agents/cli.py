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

    def turnSummary(self, playerView, actionInfo):
        if actionInfo[1] == -1:
            activePlayer = playerView.selfstate
        else:
            activePlayer = playerView.opponents[actionInfo[1]]

        if actionInfo[0].name == 'INCOME':
            print("{p} took 1 coin as income and now has {n} coins.".format(
                    p=activePlayer.name, n = activePlayer.coins))
        elif actionInfo[0].name == 'FOREIGN_AID':
            if actionInfo[2]:
                print("{p} took 2 coins as foreign aid and now has {n} coins.".format(
                    p=activePlayer.name, n=activePlayer.coins))
            else:
                print("{p} tried to take foreign aid, but was blocked.".format(
                    p=activePlayer.name))
        elif actionInfo[0].name == 'TAX':
            print("{p} took 3 coins as tax and now has {n} coins.".format(
                p=activePlayer.name, n=activePlayer.coins))
        elif actionInfo[0].name == 'EXCHANGE':
            print("{p} exchanged {n} cards.".format(p=activePlayer.name, n=activePlayer.cards))
        elif actionInfo[0].name == 'STEAL':
            if actionInfo[2] == -1:
                target = playerView.selfstate
            else:
                target = playerView.opponents[actionInfo[2]]
            if actionInfo[3]:
                print("{p} stole from {t} and now has {n} coins.".format(
                    p=activePlayer.name, t=target.name, n=activePlayer.coins))
            else:
                print("{p} tried to steal from {t} and was blocked.".format(
                    p=activePlayer.name, t=target.name))
        elif actionInfo[0].name == 'ASSASSINATE':
            if actionInfo[2] == -1:
                target = playerView.selfstate
                targetName = 'you'
            elif not(isinstance(actionInfo[2], int)):
                target = None
                targetName = actionInfo[2]
            else:
                target = playerView.opponents[actionInfo[2]]
                targetName = target.name
            if actionInfo[3]:
                if not target:
                    print("{p} assassinated {t}, who is now eliminated.".format(
                        p=activePlayer.name, t=targetName))
                else:
                    print("{p} assassinated {t}, but {t} is not yet eliminated.".format(
                        p=activePlayer.name, t=targetName))
            else:
                print("{p} attempted to assassinate {t}, but was blocked.".format(
                    p=activePlayer.name, t=targetName))
        elif actionInfo[0].name == 'COUP':
            if actionInfo[2] == -1:
                target = playerView.selfstate
                targetName = 'you'
            elif not(isinstance(actionInfo[2], int)):
                target = None
                targetName = actionInfo[2]
            else:
                target = playerView.opponents[actionInfo[2]]
                targetName = target.name
            if not target:
                print("{p} staged a coup on {t}, who is now eliminated.".format(
                    p=activePlayer.name, t=targetName))
            else:
                print("{p} staged a coup on {t}, but {t} is not yet eliminated.".format(
                    p=activePlayer.name, t=targetName))




