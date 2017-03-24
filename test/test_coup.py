import pytest

# import ..coup
from ..coup import Role, Action, Reaction
from .. import coup

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
    # this is the edge case of incorrect input, where the function can remove either card
    player = coup.PlayerState(cards=[Role.CAPTAIN, Role.CONTESSA], coins=0, agent=None, name=None)
    options = [player._replace(cards=[Role.CAPTAIN]), player._replace(cards=[Role.CONTESSA])]
    assert coup.removeCard(player, Role.ASSASSIN) in options

    player = coup.PlayerState(cards=[Role.DUKE], coins=0, agent=None, name=None)
    assert coup.removeCard(player, Role.AMBASSADOR) == None











