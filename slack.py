import coup
from agents.bots import *
# from agents.slack import SlackAgent

import sys
import os

from slacker import Slacker


def postToChannel(slack, message):
    print(f"#coup: {message}")
    slack.chat.post_message('#coup', message)

def setup():
    # setup the agents/players
    # deal the game
    pass

def postSummaryAndStateToChannel(gameState, summary):
    print(gameState)
    print(turnSummary)

def gameLoop():
    # initialstate

    turns = 0
    while len(gameState.players) > 1:
        if (turns > 1000): # shouldn't happen with people
            return None

        i = turns % len(gameState.players)

        player = gameState.players[i]
        action, relativeTarget = player.agent.selectAction(coup.getPlayerView(gameState, i))
        if relativeTarget:
            target = (i + relativeTarget + 1) % len(gameState.players)
        else:
            target = None

        gameState, turnSummary = coup.applyAction(gameState, i, action, target)
        coup.broadcastRelativeTurnSummaries(turnSummary, gameState)
        postSummaryAndStateToChannel(gameState, turnSummary)

        turns += 1
    postToChannel(f"Winner is {gameState.players[0].name}!")


def main():
    slack = Slacker(os.environ['SLACK_API_TOKEN'])
    postToChannel(slack, 'CoupBot is booting up!')
    pass


if __name__ == "__main__":
    main()
