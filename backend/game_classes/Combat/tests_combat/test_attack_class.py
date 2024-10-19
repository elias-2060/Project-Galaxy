

from backend.game_classes.Combat.Attack import Attack, GameResult

from backend.game_classes import User, Planet, Settlement, Barrack, SpaceMarine, SpaceCommando, SpaceDrone
from database.database_access import DefaultSession
import pytest


@pytest.fixture
def basic_setup_attacks():
    """
    The basic setup for the Attack class tests
    """
    session = DefaultSession(autoflush=True)

    # Make 2 users with 2 planets
    user1 = User(user_name="user1", user_password="Test_password1")
    user2 = User(user_name="user2", user_password="Test_password1")
    session.add_all([user1, user2])
    session.commit()

    planet1 = Planet(user_id=user1.user_id, planet_x=1, planet_y=1, name="planet1")
    planet2 = Planet(user_id=user2.user_id, planet_x=3, planet_y=3, name="planet2")
    session.add_all([planet1, planet2])
    session.commit()

    settlement1 = Settlement(planet_id=planet1.planet_id, settlement_nr=1)
    settlement2 = Settlement(planet_id=planet2.planet_id, settlement_nr=1)
    session.add_all([settlement1, settlement2])
    session.commit()

    barrack1 = Barrack(settlement_id=settlement1.settlement_id, grid_pos_x=1, grid_pos_y=1)
    barrack2 = Barrack(settlement_id=settlement2.settlement_id, grid_pos_x=1, grid_pos_y=1)
    session.add_all([barrack1, barrack2])
    session.commit()

    space_marine1 = SpaceMarine(barrack1.building_id)
    space_marine2 = SpaceMarine(barrack2.building_id)
    session.add_all([space_marine1, space_marine2])
    session.commit()

    attack = planet1.attack(planet2.planet_id)
    session.commit()
    return (user1, user2, session, space_marine1, space_marine2, barrack1, barrack2, settlement1, settlement2,
            attack, planet1, planet2)


@pytest.mark.usefixtures("clear-db")
def test_attack_class(basic_setup_attacks):
    """
    Tests the attack class
    """
    (user1, user2, session, space_marine1, space_marine2, barrack1, barrack2, settlement1, settlement2, attack, planet1,
     planet2) = basic_setup_attacks

    attacking_units = attack.get_attacking_units()
    defending_units = attack.get_defending_units()
    assert len(attacking_units) == 1
    assert len(defending_units) == 1
    assert attack.attacking_planet.planet_id == planet1.planet_id
    assert attacking_units[0].unit_id == space_marine1.unit_id
    assert defending_units[0].unit_id == space_marine2.unit_id


@pytest.mark.usefixtures("clear-db")
def test_attack_selecting_units(basic_setup_attacks):
    """
    Tests the selecting units and play_round() function
    """
    (user1, user2, session, space_marine1, space_marine2, barrack1, barrack2, settlement1, settlement2, attack, planet1,
     planet2) = basic_setup_attacks

    # Check that no unit is selected
    assert attack._selected_attack_unit_id is None
    assert attack._selected_defence_unit_id is None
    assert attack.get_selected_attack_unit() is None
    assert attack.get_selected_defence_unit() is None

    # Select the units
    attack.set_selected_attack_unit(space_marine1.unit_id)
    attack.set_selected_defence_unit(space_marine2.unit_id)

    # Check it with the getter
    assert attack._selected_attack_unit_id is space_marine1.unit_id
    assert attack._selected_defence_unit_id is space_marine2.unit_id
    assert attack.get_selected_attack_unit() is space_marine1
    assert attack.get_selected_defence_unit() is space_marine2

    # Play 1 round
    round_result = attack.play_round(auto_delete=False)
    session.commit()
    roll_1 = round_result["attack_roll"]
    roll_2 = round_result["defence_roll"]

    # Check whether 1 of the units got removed
    assert attack._selected_attack_unit_id is None or attack._selected_defence_unit_id is None
    attack_units = attack.get_attacking_units()
    defence_units = attack.get_defending_units()

    # With the space marine passive, there are no exceptions here, so we can test this
    assert len(attack_units) + len(defence_units) <= 1
    if len(attack_units) == 1:
        assert roll_1 > roll_2
        assert space_marine1.combats_survived == 1
    elif len(defence_units) == 1:
        assert roll_1 < roll_2
        assert space_marine2.combats_survived == 1
    else:
        assert roll_1 == roll_2


@pytest.mark.usefixtures("clear-db")
def test_attack_commando_space_drone(basic_setup_attacks):
    """
    Tests the main use functions for space commandos and space drones
    """
    (user1, user2, session, space_marine1, space_marine2, barrack1, barrack2, settlement1, settlement2, attack, planet1,
     planet2) = basic_setup_attacks
    space_commando1 = SpaceCommando(barrack_id=barrack1.building_id)
    space_commando2 = SpaceCommando(barrack_id=barrack2.building_id)
    session.add_all([space_commando1, space_commando2])
    session.commit()

    attack.select_unit_attacking(space_commando1.unit_id)
    attack.select_unit_defending(space_commando2.unit_id)
    assert len(attack.get_attacking_units()) + len(attack.get_defending_units()) == 4

    attack.play_round()
    assert len(attack.get_attacking_units()) + len(attack.get_defending_units()) <= 3

    space_drone1 = SpaceDrone(barrack_id=barrack1.building_id)
    space_drone2 = SpaceDrone(barrack_id=barrack2.building_id)
    session.add_all([space_drone1, space_drone2])
    session.commit()

    attack.select_unit_attacking(space_drone1.unit_id)
    attack.select_unit_defending(space_drone2.unit_id)
    assert len(attack.get_attacking_units()) + len(attack.get_defending_units()) <= 5

    attack.play_round()

    assert len(attack.get_attacking_units()) + len(attack.get_defending_units()) <= 4


@pytest.mark.usefixtures("clear-db")
def test_auto_selection(basic_setup_attacks):
    """
    Tests the auto select function
    """
    (user1, user2, session, space_marine1, space_marine2, barrack1, barrack2, settlement1, settlement2, attack, planet1,
     planet2) = basic_setup_attacks
    """"
    # Save the resources of each planet
    rations_planet_1 = planet1.rations
    building_mats_planet_1 = planet1.building_materials
    rations_planet_2 = planet2.rations
    building_mats_planet_2 = planet2.building_materials

    result_str = attack.play_round(auto_select_attack=True, auto_select_defence=True)[-1]

    # Check whether the round is ended
    assert isinstance(result_str, GameResult)

    # Check the resources lost / gained
    if result_str == GameResult.WIN:
        assert planet1.rations > rations_planet_1
        assert planet1.building_materials > building_mats_planet_1
        assert planet2.rations < rations_planet_2
        assert planet2.building_materials < building_mats_planet_2
    elif result_str == GameResult.DRAW:
        assert planet1.rations < rations_planet_1
        assert planet1.building_materials == building_mats_planet_1
        assert planet2.rations == rations_planet_2
        assert planet2.building_materials == building_mats_planet_2
    else:
        assert result_str == GameResult.LOSE
        assert planet1.rations < rations_planet_1
        assert planet1.building_materials < building_mats_planet_1
        assert planet2.rations == rations_planet_2
        assert planet2.building_materials == building_mats_planet_2
        """


@pytest.mark.usefixtures("clear-db")
def test_win(basic_setup_attacks):
    """
    Tests the win function
    """
    (user1, user2, session, space_marine1, space_marine2, barrack1, barrack2, settlement1, settlement2, attack, planet1,
     planet2) = basic_setup_attacks

    # Set some values for the rations and building materials
    planet1.rations = 1000
    planet1.building_materials = 1000
    planet2.rations = 1000
    planet2.building_materials = 1000

    # Win
    attack.win()

    # 25% of resources are moved
    assert planet1.rations == 1250
    assert planet1.building_materials == 1250
    assert planet2.rations == 750
    assert planet2.building_materials == 750


@pytest.mark.usefixtures("clear-db")
def test_lose(basic_setup_attacks):
    """
    Tests the loss function
    """
    (user1, user2, session, space_marine1, space_marine2, barrack1, barrack2, settlement1, settlement2, attack, planet1,
     planet2) = basic_setup_attacks

    # Set some values for the rations and building materials
    planet1.rations = 1000
    planet1.building_materials = 1000
    planet2.rations = 1000
    planet2.building_materials = 1000

    # Lose
    attack.lose()

    # 10% of resources are lost
    assert planet1.rations == 900
    assert planet1.building_materials == 900
    assert planet2.rations == 1000
    assert planet2.building_materials == 1000