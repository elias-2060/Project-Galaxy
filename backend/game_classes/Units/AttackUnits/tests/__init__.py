import pytest
from database.database_access import DefaultSession
from backend.game_classes import (
    User,
    Planet,
    Settlement,
    Barrack,
    SpaceMarine,
    SpaceCommando,
    SpaceDrone,
)


@pytest.fixture
def attack_unit_default_setup():
    """
    This is the default setup for attack units, it contains three different attack units, a user, a planet, a barrack
    and a session.
    """
    session = DefaultSession(autoflush=True)

    # Add a user
    user = User("test_user_attack_unit", "Test_password1")
    session.add(user)
    session.commit()

    planet = Planet(user.user_id, 1, 1, "test_planet_attack_unit")
    session.add(planet)
    session.commit()

    settlement = Settlement(1, planet.planet_id)
    session.add(settlement)
    session.commit()

    # We start by constructing a barrack
    barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3, level=3)
    session.commit()
    assert barrack.grid_pos_x == 2
    assert barrack.grid_pos_y == 3
    assert barrack.level == 3
    assert not barrack.in_construction()
    assert len(barrack.get_units_in_training()) == 0

    # For each instance of attack-unit, we check if the getters work
    space_drone = SpaceDrone(barrack_id=barrack.building_id)
    space_marine = SpaceMarine(barrack_id=barrack.building_id)
    space_commando = SpaceCommando(barrack_id=barrack.building_id)
    session.add_all([space_drone, space_marine, space_commando])
    session.commit()

    # We put the units in a list
    unit_list = [space_marine, space_drone, space_commando]
    assert (unit.level == 1 for unit in unit_list)

    # Return the values
    return user, planet, settlement, barrack, [space_drone, space_marine, space_commando], session
