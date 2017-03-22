import coup
from agents.bots import *
from agents.slack import SlackAgent

import sys
import os
from functools import partial
from collections import namedtuple

from slacker import Slacker

listeners = {}

M = namedtuple('M', 'sender message')
test_message = M('mikayla', 'Hello, world. this is a fake received message.')

def postToChannel(slack, message):
    print(f"#coup: {message}")
    slack.chat.post_message('#coup', message)

def postToUser(slack, username, message):
    print(f"@{username}: {message}")
    slack.chat.post_message(f"@{username}", message, as_user=True, link_names=True)


def listener(mdata):
    # determine if this is a relevant message.
    # if so, determine who it is for.
    player = mdata.sender
    if player in listeners:
        listeners[player](mdata.message)
    pass


def setup(slack):
    # setup the agents/players
    players = ['mikayla']
    agents = []
    for player in players:
        # Give each agent a partial for a direct-post function
        # and a listenerRegistration function
        def registerListener(listenerFunction):
            listeners[player] = listenerFunction

        agents.append(SlackAgent(post=partial(postToUser, slack, player),
                                listenerRegistration=registerListener,
                                name=player))
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
    setup(slack)
    listener(test_message)
    # postToChannel(slack, 'CoupBot is booting up!')
    pass


if __name__ == "__main__":
    main()
