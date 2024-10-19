import pytest
from backend.game_classes import (
    User,
    Planet,
    TownHall,
    Settlement,
    Barrack,
    SpaceMarine,
    SpaceCommando,
    SpaceDrone,
)
from database.database_access import DefaultSession


@pytest.mark.usefixtures("clear-db")
def test_training_a_space_marine():
    with DefaultSession(autoflush=True) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "test_planet")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        townHall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(townHall)
        session.commit()

        # We start by constructing a barrack
        barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3)
        session.commit()
        assert barrack.grid_pos_x == 2
        assert barrack.grid_pos_y == 3
        assert barrack.level == 0
        assert not barrack.in_construction()
        assert len(barrack.get_units_in_training()) == 0

        # We add some building resources
        planet.building_materials = 1000
        planet.rations = 1000
        session.commit()
        assert planet.building_materials == 1000

        # Now build the barrack
        assert settlement.build(barrack)
        assert barrack.in_construction()
        assert barrack.level == 1
        assert barrack.get_space_taken() == 0
        assert len(barrack.get_units_in_training()) == 0
        assert planet.building_materials == 900

        # We update 10 seconds (until construction is finished)
        barrack.update(10)
        assert not barrack.in_construction()

        # We make a space marine
        space_marine = SpaceMarine(level=1, barrack_id=barrack.building_id)
        session.add(space_marine)
        session.commit()
        assert not space_marine.in_training()

        # We train the space marine in the barrack
        assert barrack.train_unit(space_marine) is None
        session.commit()
        assert space_marine.attack_power == 10
        assert barrack.get_space_taken() == 3
        assert barrack.max_capacity == 10
        assert space_marine.training_time_left == 60
        assert planet.rations == 990
        assert len(barrack.get_units_in_training()) == 1
        assert space_marine.in_training()
        assert space_marine.size == 3
        assert planet.get_attack_power() == 0
        assert space_marine.training_pos == 1

        # We finish the training:
        barrack.update(60)
        assert not space_marine.in_training()
        assert space_marine.training_pos is None
        assert space_marine.training_time_left == 0
        assert planet.get_attack_power() == 10


@pytest.mark.usefixtures("clear-db")
def test_training_multiple_units():
    with DefaultSession(autoflush=False) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "test_planet")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        townHall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(townHall)
        session.commit()

        # We start by constructing a barrack
        barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3, level=1)
        session.add(barrack)
        session.commit()

        planet.rations = 1000

        space_marine1 = SpaceMarine(barrack_id=barrack.building_id)
        space_marine2 = SpaceMarine(barrack_id=barrack.building_id)
        assert not space_marine1.in_training()
        assert not space_marine2.in_training()

        # We train both units
        barrack.train_unit(space_marine1)
        session.commit()
        barrack.train_unit(space_marine2)
        session.commit()
        assert space_marine1.in_training()
        assert space_marine2.in_training()
        assert space_marine1.training_pos == 1
        assert space_marine2.training_pos == 2
        assert space_marine1.training_time_left == 60
        assert space_marine2.training_time_left == 60

        # We wait 60 seconds (time for the first unit to train)
        barrack.update(60)
        session.commit()
        assert not space_marine1.in_training()
        assert space_marine2.in_training()
        assert planet.get_attack_power() == 10

        # We wait 60 seconds (time for the second unit to train)
        barrack.update(60)
        session.commit()
        assert not space_marine1.in_training()
        assert not space_marine2.in_training()
        assert planet.get_attack_power() == 20


@pytest.mark.usefixtures("clear-db")
def test_food_consumption():
    with DefaultSession(autoflush=False) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "test_planet")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        townHall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(townHall)
        session.commit()

        # We start by constructing a barrack
        barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3, level=1)
        session.add(barrack)
        session.commit()

        planet.rations = 1000

        # We make 2 units
        space_marine_1 = SpaceMarine(level=1, barrack_id=barrack.building_id)
        space_marine_2 = SpaceMarine(level=1, barrack_id=barrack.building_id)
        session.add(space_marine_1)
        session.add(space_marine_2)
        session.commit()

        # We wait 1 hour, so food starts getting consumed
        barrack.update(3600)
        assert planet.rations == 994


@pytest.mark.usefixtures("clear-db")
def test_starvation():
    with DefaultSession(autoflush=False) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "test_planet")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        townHall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(townHall)
        session.commit()

        # We start by constructing a barrack
        barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3, level=1)
        session.add(barrack)
        session.commit()

        planet.rations = 10

        # We make 2 units
        space_marine_1 = SpaceMarine(level=1, barrack_id=barrack.building_id)
        space_marine_2 = SpaceMarine(level=1, barrack_id=barrack.building_id)
        session.add(space_marine_1)
        session.add(space_marine_2)
        session.commit()

        # We wait 10 hours, this should be enough food for the units to starve
        barrack.update(3600 * 10)
        session.commit()
        assert len(barrack.attack_units) == 0
        assert planet.rations == 0


@pytest.mark.usefixtures("clear-db")
def test_training_a_space_commando():
    with DefaultSession(autoflush=True) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "test_planet")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        townHall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(townHall)
        session.commit()

        # We start by constructing a barrack
        barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3, level=0)
        session.add(barrack)
        session.commit()
        assert barrack.grid_pos_x == 2
        assert barrack.grid_pos_y == 3
        assert barrack.level == 0
        assert not barrack.in_construction()
        assert len(barrack.get_units_in_training()) == 0

        # We add some building resources
        planet.building_materials = 1000
        planet.rations = 1000
        session.commit()
        assert planet.building_materials == 1000
        session.commit()

        # Now build the barrack
        assert settlement.build(barrack)
        assert barrack.in_construction()
        assert barrack.level == 1
        assert barrack.get_space_taken() == 0
        assert len(barrack.get_units_in_training()) == 0
        assert planet.building_materials == 900

        # We update 10 seconds (until construction is finished)
        barrack.update(10)
        assert not barrack.in_construction()
        assert barrack.level == 1
        session.commit()

        # We make a space commando
        space_commando = SpaceCommando(barrack_id=barrack.building_id)
        session.add(space_commando)
        session.commit()
        assert not space_commando.in_training()
        assert barrack.level == 1
        assert barrack.space_commando_level == 1

        # We train the space marine in the barrack, this fails because the barrack is level 1
        assert barrack.train_unit(space_commando)[0] is not None
        session.commit()
        session.delete(space_commando)
        session.commit()

        # Now we upgrade the barrack
        barrack.upgrade()
        assert barrack.in_construction()
        barrack.update(60)
        assert not barrack.in_construction()
        assert barrack.level == 2
        assert barrack.space_commando_level == 1

        # Now we make a new space_commando, and train it
        space_commando = SpaceCommando(level=1, barrack_id=barrack.building_id)
        session.add(space_commando)
        session.commit()
        assert barrack.train_unit(space_commando) is None
        assert space_commando.in_training()
        assert space_commando.attack_power == 20
        assert barrack.get_space_taken() == 6
        assert barrack.max_capacity == 15
        assert space_commando.training_time_left == 240
        assert planet.rations == 960
        assert len(barrack.get_units_in_training()) == 1
        assert space_commando.in_training()
        assert space_commando.size == 6
        assert planet.get_attack_power() == 0
        assert space_commando.training_pos == 1

        # We finish the training:
        barrack.update(240)
        assert not space_commando.in_training()
        assert space_commando.training_pos is None
        assert space_commando.training_time_left == 0
        assert planet.get_attack_power() == 20


@pytest.mark.usefixtures("clear-db")
def test_training_a_space_drone():
    with DefaultSession(autoflush=False) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "test_planet")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        townHall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(townHall)
        session.commit()

        # We start by constructing a barrack
        barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3, level=2)
        session.add(barrack)
        session.commit()
        assert barrack.grid_pos_x == 2
        assert barrack.grid_pos_y == 3
        assert barrack.level == 2
        assert not barrack.in_construction()
        assert len(barrack.get_units_in_training()) == 0

        # We add some building resources
        planet.building_materials = 1000
        planet.rations = 2000
        session.commit()
        assert planet.building_materials == 1000
        assert planet.rations == 2000

        # We make a space marine
        space_drone = SpaceDrone(level=1, barrack_id=barrack.building_id)
        session.add(space_drone)
        session.commit()
        assert not space_drone.in_training()

        # Check whether we can train the drone (cannot, barrack too low level):
        assert barrack.train_unit(space_drone) is not None
        assert barrack.space_drone_level == 1
        session.delete(space_drone)
        session.commit()

        # Nw we change the level of the barrack to 3:
        barrack.level = 3
        session.commit()

        # We train the space marine in the barrack
        space_drone = SpaceDrone(level=1, barrack_id=barrack.building_id)
        session.add(space_drone)
        session.commit()
        assert barrack.train_unit(space_drone) is None
        assert space_drone.in_training()
        session.commit()

        # Now we wait until training is done:
        barrack.update(1800)
        session.commit()
        assert not space_drone.in_training()
        assert space_drone.attack_power == 200
        assert barrack.get_space_taken() == 20
        assert barrack.max_capacity == 20
        assert space_drone.training_time_left == 0
        assert planet.rations == 1000
        assert len(barrack.get_units_in_training()) == 0
        assert not space_drone.in_training()
        assert space_drone.size == 20
        assert planet.get_attack_power() == 200
        assert space_drone.training_pos is None

        # We check food consumption:
        barrack.update(1800)
        session.commit()
        assert space_drone.seconds_since_last_feed == 1800
        assert planet.rations == 1000

        # We check food consumption:
        barrack.update(1800)
        session.commit()
        assert space_drone.seconds_since_last_feed == 0
        assert planet.rations == 950


@pytest.mark.usefixtures("clear-db")
def test_upgrade_units():
    with DefaultSession(autoflush=False) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "test_planet")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        townHall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(townHall)
        session.commit()

        # We start by constructing a barrack
        barrack = Barrack(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=3, level=1)
        session.add(barrack)
        session.commit()
        assert barrack.space_marine_level == 1

        # Set building materials to less than required
        planet.building_materials = 100

        # We upgrade the space marine level, fails due to lack of resources
        assert not barrack.upgrade_unit_type(SpaceMarine)
        assert barrack.space_marine_level == 1

        # We add some building materials
        planet.rations = 1000
        planet.building_materials = 1000

        # Now we upgrade the marines
        assert barrack.upgrade_unit_type(SpaceMarine)
        assert planet.building_materials == 750
        assert barrack.space_marine_level == 2

        # Now we upgrade the space commanders
        assert barrack.upgrade_unit_type(SpaceCommando)
        assert planet.building_materials == 250
        assert barrack.space_commando_level == 2

        # Now the drones:
        assert not barrack.upgrade_unit_type(SpaceDrone)
        assert barrack.space_drone_level == 1
        planet.building_materials = 2000
        session.commit()
        assert barrack.upgrade_unit_type(SpaceDrone)
        assert planet.building_materials == 0
        assert barrack.space_drone_level == 2
