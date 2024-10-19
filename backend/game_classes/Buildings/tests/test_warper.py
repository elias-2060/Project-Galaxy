import pytest
from backend.game_classes import User, Planet, Settlement
from backend.game_classes.Buildings.TownHall import TownHall
from backend.game_classes.Buildings.Warper import Warper
from database.database_access import DefaultSession


@pytest.mark.usefixtures("clear-db")
def test_create_and_remove_link():
    with DefaultSession(autoflush=True) as session:
        # Create users
        user1 = User("user1", "Test_password1")
        user2 = User("user2", "Test_password2")
        session.add_all([user1, user2])
        session.commit()

        # Create planets for each user
        planet1 = Planet(user1.user_id, 1, 1, "planet1")
        planet2 = Planet(user2.user_id, 2, 2, "planet2")
        planet3 = Planet(user2.user_id, 3, 3, "planet3")
        session.add_all([planet1, planet2, planet3])
        session.commit()

        # Create settlements for each planet
        settlement1 = Settlement(1, planet1.planet_id)
        settlement2 = Settlement(1, planet2.planet_id)
        settlement3 = Settlement(1, planet3.planet_id)
        session.add_all([settlement1, settlement2, settlement3])
        session.commit()

        townHall1 = TownHall(settlement_id=settlement1.settlement_id, grid_pos_x=1, grid_pos_y=1)
        townHall2 = TownHall(settlement_id=settlement2.settlement_id, grid_pos_x=1, grid_pos_y=1)
        townHall3 = TownHall(settlement_id=settlement3.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add_all([townHall1, townHall2, townHall3])
        session.commit()

        # Create link between Planet1 and Planet2
        warper = Warper(settlement_id=settlement1.settlement_id,grid_pos_x=2,grid_pos_y=3)
        session.add(warper)
        session.commit()

        link = warper.create_link(planet1, planet2, session)

        # Check if the link is correctly created
        assert warper.check_existing_link(planet1, planet2, session)
        assert warper.check_existing_link(planet2, planet1, session)
        assert not warper.check_existing_link(planet1, planet3, session)

        assert link.warper_id == warper.building_id
        assert link.speed_factor() == 3.0

        # Delete the link
        warper.delete_link(session)

        # Check if the link is deleted
        assert not warper.check_existing_link(planet1, planet2, session)

        assert not warper.has_link()

        warper.create_link(planet1, planet2)
        warper.create_link(planet2, planet1)

        with pytest.raises(ValueError):
            warper.create_link(planet1, planet3, session)