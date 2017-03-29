import coup
from agents.bots import *
from agents.slack import SlackAgent

import sys
import os
from functools import partial
from collections import namedtuple
from datetime import datetime
import time

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

def gen_userlist(slack):
    return slack.users.list().body['members']

def to_user_id(userlist, user):
    match = [x for x in userlist if x['name'] == user]
    return match[0]['id']

def listen(slack, user, prompt=None):
    ts = datetime.now().timestamp()
    if prompt:
        postToUser(slack, user, prompt)
    user_id = slack.to_user_id(user)
    new_messages = None
    while not new_messages:
        time.sleep(0.5)
        new_messages = slack.channels.history(channel=slack.coup_channel,
                                              oldest=ts,
                                              inclusive=True).body['messages']
        print(new_messages)
        new_messages = [m['text'] for m in new_messages if m['user'] == user_id]
    return new_messages

def get_channel_id(slack, channelName):
    channels = slack.channels.list().body
    match = [x for x in slack.channels.list().body['channels'] if x['name'] == 'coup']
    return match[0]['id']

def setup(slack):
    # rtm = slack.rtm.start(simple_latest=True, no_unreads=True)
    slack.coup_channel = get_channel_id(slack, 'coup')
    slack.to_user_id = partial(to_user_id, gen_userlist(slack))
    players = ['mikayla']
    agents = []
    for player in players:
        # Give each agent a partial for a direct-post function
        # and a listenerRegistration function

        agents.append(SlackAgent(post=partial(postToUser, slack, player),
                                listen=partial(listen, slack, player),
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
    # print(listen(slack, 'mikayla'))
    # listener(test_message)
    # postToChannel(slack, 'CoupBot is booting up!')
    pass


if __name__ == "__main__":
    main()
