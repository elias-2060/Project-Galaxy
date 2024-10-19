import pytest
from backend.game_classes import (
    User,
    Planet,
    Settlement,
    Barrack,
    TownHall,
    SpaceMarine,
)

from backend.game_classes.Ships.Spaceship import Spaceship
from backend.game_classes.Ships.ship import Ship
from database.database_access import DefaultSession
from backend.game_classes.Buildings.Warper import Warper


@pytest.mark.usefixtures("clear-db")
def test_transfer_resources():
    with DefaultSession(autoflush=True) as session:
        # Add users
        user1 = User("user1","Test_password1")
        user2 = User("user2", "Test_password2")
        session.add_all([user1, user2])
        session.commit()

        planet1 = Planet(user1.user_id, 1, 1, "planet1")
        planet2 = Planet(user2.user_id, 2, 2, "planet2")
        session.add_all([planet1, planet2])
        session.commit()

        # Settlements on the planets
        settlement1 = Settlement(1, planet1.planet_id)
        settlement2 = Settlement(1, planet2.planet_id)

        session.add_all([settlement1, settlement2])
        session.commit()

        townHall1 = TownHall(settlement_id=settlement1.settlement_id, grid_pos_x=1, grid_pos_y=1)
        townHall2 = TownHall(settlement_id=settlement2.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add_all([townHall1, townHall2])
        session.commit()

        # Create link between planet1 and planet2
        warper = Warper(settlement_id=settlement1.settlement_id, grid_pos_x=3, grid_pos_y=2)
        session.add(warper)
        session.commit()
        warper.create_link(planet1, planet2, session)

        # Add spaceship
        ship = Ship(user1.user_id)
        spaceship = Spaceship(user1.user_id, ship.ship_id)
        session.add(spaceship)
        session.commit()

        planet1.building_materials, planet1.rations = 1000, 1000
        planet2.building_materials, planet2.rations = 0, 0
        session.commit()

        # Transfer resources from planet1 to planet2
        with pytest.raises(ValueError):
            spaceship.board_building_materials(planet1, 5000, session)
        assert spaceship.building_materials == 0

        spaceship.board_building_materials(planet1, 500, session)
        spaceship.board_rations(planet1, 500, session)

        spaceship.move_from_to_planet(planet1, planet2, session)
        session.commit()

        assert spaceship.moving_time_left == 0
        assert planet1.building_materials == 500
        assert planet1.rations == 500
        assert planet2.building_materials == 500
        assert planet2.rations == 500
        assert spaceship.building_materials == 0
        assert spaceship.rations == 0


@pytest.mark.usefixtures("clear-db")
def test_transfer_attack_units():
    with DefaultSession(autoflush=True) as session:
        # Add users
        user1 = User("user1", "Test_password1")
        user2 = User("user2", "Test_password2")
        session.add_all([user1, user2])
        session.commit()

        planet1 = Planet(user1.user_id, 1, 1, "planet1")
        planet2 = Planet(user2.user_id, 2, 2, "planet2")
        session.add_all([planet1, planet2])
        session.commit()

        # Settlements on the planets
        settlement1 = Settlement(1, planet1.planet_id)
        settlement2 = Settlement(1, planet2.planet_id)
        session.add_all([settlement1, settlement2])
        session.commit()

        townHall1 = TownHall(settlement_id=settlement1.settlement_id, grid_pos_x=1, grid_pos_y=1)
        townHall2 = TownHall(settlement_id=settlement2.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add_all([townHall1, townHall2])
        session.commit()

        # Create link between planet1 and planet2
        warper = Warper(settlement_id=settlement1.settlement_id, grid_pos_x=3, grid_pos_y=2)
        session.add(warper)
        session.commit()
        warper.create_link(planet1, planet2, session)

        # Add spaceship
        ship = Ship(user1.user_id)
        spaceship = Spaceship(user1.user_id, ship.ship_id)
        session.add(spaceship)
        session.commit()

        # Add barracks
        barrack1 = Barrack(settlement_id=settlement1.settlement_id, grid_pos_x=2, grid_pos_y=3)
        barrack2 = Barrack(settlement_id=settlement2.settlement_id, grid_pos_x=2, grid_pos_y=3)
        session.add_all([barrack1, barrack2])
        session.commit()

        planet1.building_materials, planet1.rations = 1000, 1000
        # build barrack1
        assert settlement1.build(barrack1)
        barrack1.update(10)
        session.commit()

        planet1.building_materials, planet1.rations = 1000, 1000
        # build barrack2
        assert settlement2.build(barrack2)
        barrack2.update(10)
        session.commit()

        for barrack in [barrack1, barrack2]:
            for _ in range(2):
                space_marine = SpaceMarine(level=1, barrack_id=barrack.building_id)
                session.add(space_marine)
                session.commit()
                assert barrack.train_unit(space_marine) is None
                barrack.update(60)
                session.commit()

        assert len(barrack1.attack_units) == 2
        assert barrack1.get_space_taken() == 6

        assert len(barrack2.attack_units) == 2
        assert barrack2.get_space_taken() == 6

        assert len(spaceship.attack_units) == 0

        attack_unit1 = barrack1.attack_units[0]
        attack_unit2 = barrack1.attack_units[1]

        spaceship.board_attack_unit(planet2, attack_unit1, session)

        with pytest.raises(ValueError):
            spaceship.board_attack_unit(planet2, attack_unit2, session)

        assert len(barrack1.attack_units) == 1
        assert barrack1.get_space_taken() == 3

        assert len(barrack2.attack_units) == 2
        assert barrack2.get_space_taken() == 6

        assert len(spaceship.attack_units) == 1

        spaceship.move_from_to_planet(planet1, planet2, session)
        session.commit()

        assert spaceship.moving_time_left == 0

        assert len(barrack1.attack_units) == 1
        assert barrack1.get_space_taken() == 3

        assert len(barrack2.attack_units) == 3
        assert barrack2.get_space_taken() == 9

        assert len(spaceship.attack_units) == 0
