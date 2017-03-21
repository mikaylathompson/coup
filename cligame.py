import coup
from agents.bots import *
from agents.cli import CLInteractiveAgent

import sys

bots = dict(
    random=RandomAgent,
    bay=BayBot,
    sean=SeanAgent,
    mikayla=MrtBot
)


def selectOpponents():
    print("Available bots are:")
    for n in bots.keys():
        print(n)
    oppRequest = input("Input the bots you'd like to play against, seperated by commas.\n")
    botRequests = map(lambda x: x.strip(), oppRequest.strip().split(','))
    players = [CLInteractiveAgent()]
    for b in botRequests:
        if b in bots:
            players.append(bots[b]())
        else:
            print(b, "doesn't seem to be a valid bot name. Skipping.")

    if len(players) == 1:
        print("You didn't select any players. Now exiting.")
        sys.exit(0)
    print("Players have been selected.")
    return players


def main():
    players = selectOpponents()
    yes = input("Press [q] to cancel game, or enter to start game.\n")
    if 'q' in yes:
        sys.exit(0)
    winner = coup.gameLoop(players, humanInput=False)
    print("Winner is:", winner)

if __name__ == "__main__":
    main()
