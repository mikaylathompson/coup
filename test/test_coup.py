import pytest

from coup import coup
from coup.coup import Role, Action, Reaction

def test_eligible_duke_actions():
    player = coup.PlayerState(cards=[Role.DUKE], coins=0, agent=None, name=None)
    correct_actions = {Action.INCOME, Action.FOREIGN_AID, Action.TAX}
    assert coup.findEligibleActions(player) == correct_actions
    
    player = player._replace(coins=7)
    assert coup.findEligibleActions(player) == correct_actions | {Action.COUP}
    
    player = player._replace(coins=10)
    assert coup.findEligibleActions(player) == {Action.COUP}


def test_eligible_assassin_actions():
    player = coup.PlayerState(cards=[Role.ASSASSIN], coins=0, agent=None, name=None)
    correct_actions = {Action.INCOME, Action.FOREIGN_AID}
    assert coup.findEligibleActions(player) == correct_actions

    player = player._replace(coins=3)
    assert coup.findEligibleActions(player) == correct_actions | {Action.ASSASSINATE}

    player = player._replace(coins=7)
    assert coup.findEligibleActions(player) == correct_actions | {Action.ASSASSINATE, Action.COUP}

    player = player._replace(coins=10)
    assert coup.findEligibleActions(player) == {Action.COUP}

    
def test_eligible_contessa_actions():
    player = coup.PlayerState(cards=[Role.CONTESSA], coins=0, agent=None, name=None)
    correct_actions = {Action.INCOME, Action.FOREIGN_AID}
    assert coup.findEligibleActions(player) == correct_actions

    player = player._replace(coins=7)
    assert coup.findEligibleActions(player) == correct_actions | {Action.COUP}

    player = player._replace(coins=10)
    assert coup.findEligibleActions(player) == {Action.COUP}


def test_eligible_ambassador_actions():
    player = coup.PlayerState(cards=[Role.AMBASSADOR], coins=0, agent=None, name=None)
    correct_actions = {Action.INCOME, Action.FOREIGN_AID, Action.EXCHANGE}
    assert coup.findEligibleActions(player) == correct_actions

    player = player._replace(coins=7)
    assert coup.findEligibleActions(player) == correct_actions | {Action.COUP}

    player = player._replace(coins=10)
    assert coup.findEligibleActions(player) == {Action.COUP}


def test_eligible_captain_actions():
    player = coup.PlayerState(cards=[Role.CAPTAIN], coins=0, agent=None, name=None)
    correct_actions = {Action.INCOME, Action.FOREIGN_AID, Action.STEAL}
    assert coup.findEligibleActions(player) == correct_actions

    player = player._replace(coins=7)
    assert coup.findEligibleActions(player) == correct_actions | {Action.COUP}

    player = player._replace(coins=10)
    assert coup.findEligibleActions(player) == {Action.COUP}


def test_get_player_view():
    game = coup.GameState(players = [coup.PlayerState(cards=[Role.CAPTAIN],
                                                      coins=0, agent=None, name='0th'),
                                     coup.PlayerState(cards=[Role.ASSASSIN, Role.CAPTAIN],
                                                      coins=9, agent=None, name='1st'),
                                     coup.PlayerState(cards=[Role.DUKE, Role.DUKE],
                                                      coins=5, agent=None, name='2nd')],
                         deck=[]) 
    view0 = coup.PlayerView(selfstate=game.players[0],
                            opponents=[coup.PlayerState(cards=2, coins=9, agent=None, name='1st'),
                                       coup.PlayerState(cards=2, coins=5, agent=None, name='2nd')])
    assert coup.getPlayerView(game, 0) == view0 

    view1 = coup.PlayerView(selfstate=game.players[1],
                            opponents=[coup.PlayerState(cards=2, coins=5, agent=None, name='2nd'),
                                       coup.PlayerState(cards=1, coins=0, agent=None, name='0th')])
    assert coup.getPlayerView(game, 1) == view1 

    view2 = coup.PlayerView(selfstate=game.players[2],
                            opponents=[coup.PlayerState(cards=1, coins=0, agent=None, name='0th'),
                                       coup.PlayerState(cards=2, coins=9, agent=None, name='1st')])
    assert coup.getPlayerView(game, 2) == view2


@pytest.mark.parametrize("coins,action,expected", [
            (0, Action.INCOME, True),
            (0, Action.FOREIGN_AID, True),
            (0, Action.TAX, True),
            (0, Action.ASSASSINATE, False),
            (0, Action.STEAL, True),
            (0, Action.EXCHANGE, True),
            (0, Action.COUP, False),
            (3, Action.ASSASSINATE, True),
            (7, Action.INCOME, True),
            (7, Action.FOREIGN_AID, True),
            (7, Action.TAX, True),
            (7, Action.ASSASSINATE, True),
            (7, Action.STEAL, True),
            (7, Action.EXCHANGE, True),
            (7, Action.COUP, True),
            (10, Action.TAX, False),
            (10, Action.ASSASSINATE, False),
            (10, Action.STEAL, False),
            (10, Action.EXCHANGE, False),
            (10, Action.COUP, True)])
def test_can_afford_action(coins, action, expected):
    player = coup.PlayerState(cards=None, coins=coins, agent=None, name=None)
    assert coup.canAffordAction(player, action) == expected


def test_remove_card():
    player = coup.PlayerState(cards=[Role.CAPTAIN, Role.CONTESSA], coins=0, agent=None, name=None)

    postPlayer = player._replace(cards=[Role.CONTESSA])
    assert postPlayer == coup.removeCard(player, Role.CAPTAIN)

    postPlayer = player._replace(cards=[Role.CAPTAIN])
    assert postPlayer == coup.removeCard(player, Role.CONTESSA)


def test_remove_card_elimination():
    player = coup.PlayerState(cards=[Role.DUKE], coins=0, agent=None, name=None)
    assert coup.removeCard(player, Role.DUKE) == None

    player = coup.PlayerState(cards=[Role.CAPTAIN, Role.CONTESSA], coins=0, agent=None, name=None)
    assert coup.removeCard(coup.removeCard(player, Role.CAPTAIN), Role.CONTESSA) == None


def test_remove_card_with_replacement():
    player = coup.PlayerState(cards=[Role.DUKE], coins=0, agent=None, name=None)
    postPlayer = player._replace(cards=[Role.ASSASSIN])
    assert coup.removeCard(player, Role.DUKE, replacement=Role.ASSASSIN) == postPlayer


def test_remove_missing_card():
    # This is the edge case of incorrect input, where the function can remove either card.
    player = coup.PlayerState(cards=[Role.CAPTAIN, Role.CONTESSA], coins=0, agent=None, name=None)
    options = [player._replace(cards=[Role.CAPTAIN]), player._replace(cards=[Role.CONTESSA])]
    assert coup.removeCard(player, Role.ASSASSIN) in options

    player = coup.PlayerState(cards=[Role.DUKE], coins=0, agent=None, name=None)
    assert coup.removeCard(player, Role.AMBASSADOR) == None



###  TEST APPLYING EACH ACTION ###

# This needs a super easy MockAgent that turns down all Reactions/etc.
from coup.agents.agent import BaseAgent

class MockAgent(BaseAgent):
    def selectReaction(self, playerView, actionInfo):
        return False

    def selectKilledCard(self, playerView):
        return playerView.selfstate.cards[-1]

    def selectExchangeCards(self, playerView, cards):
        return cards[:-2]

game = coup.GameState(players = [
    coup.PlayerState(cards=[Role.CAPTAIN], coins=0, agent=MockAgent(), name='0th'),
    coup.PlayerState(cards=[Role.ASSASSIN, Role.CAPTAIN], coins=9, agent=MockAgent(), name='1st'),
    coup.PlayerState(cards=[Role.DUKE, Role.AMBASSADOR], coins=5, agent=MockAgent(), name='2nd')
    ], deck = [Role.DUKE, Role.CONTESSA])

def test_apply_income():
    new0th = game.players[0]._replace(coins=1)
    summary = coup.Summary(Action.INCOME, 0, '0th')

    applied = coup.applyIncome(game, 0)
    assert applied[0].players[0] == new0th
    assert applied[1] == summary
    
    applied = coup.applyAction(game, 0, Action.INCOME)
    assert applied[0].players[0] == new0th
    assert applied[1] == summary


def test_apply_foreign_aid():
    new0th = game.players[0]._replace(coins=2)
    summary = coup.SummaryWSuccess(Action.FOREIGN_AID, 0, '0th', success=True)

    applied = coup.applyForeignAid(game, 0)
    # Can I verify that the selectReaction method was called on the agents?
    assert applied[0].players[0] == new0th
    assert applied[1] == summary

    applied = coup.applyAction(game, 0, Action.FOREIGN_AID)
    assert applied[0].players[0] == new0th
    assert applied[1] == summary


def test_apply_tax():
    new2nd = game.players[2]._replace(coins=8)
    summary = coup.Summary(Action.TAX, 2, '2nd')
    
    applied = coup.applyTax(game, 2)
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary

    applied = coup.applyAction(game, 2, Action.TAX)
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary


def test_apply_steal():
    new0th = game.players[0]._replace(coins=2)
    new2nd = game.players[2]._replace(coins=3)
    summary = coup.SummaryWTargetSuccess(Action.STEAL, 0, '0th', 2, '2nd', True)

    applied = coup.applySteal(game, 0, 2)
    assert applied[0].players[0] == new0th
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary

    applied = coup.applyAction(game, 0, Action.STEAL, 2)
    assert applied[0].players[0] == new0th
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary


def test_apply_assassinate():
    new1st = game.players[1]._replace(coins=6)
    new2nd = game.players[2]._replace(cards=[Role.DUKE])
    summary = coup.SummaryWTargetSuccess(Action.ASSASSINATE, 1, '1st', 2, '2nd', True)

    applied = coup.applyAssassinate(game, 1, 2)
    assert applied[0].players[1] == new1st
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary

    applied = coup.applyAction(game, 1, Action.ASSASSINATE, 2)
    assert applied[0].players[1] == new1st
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary


def test_apply_coup():
    new1st = game.players[1]._replace(coins=2)
    new2nd = game.players[2]._replace(cards=[Role.DUKE])
    summary = coup.SummaryWTarget(Action.COUP, 1, '1st', 2, '2nd')

    applied = coup.applyCoup(game, 1, 2)
    assert applied[0].players[1] == new1st
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary

    applied = coup.applyAction(game, 1, Action.COUP, 2)
    assert applied[0].players[1] == new1st
    assert applied[0].players[2] == new2nd
    assert applied[1] == summary

