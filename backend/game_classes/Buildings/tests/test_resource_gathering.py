import pytest
from backend.game_classes import User, Planet, TownHall, Settlement, Farm, Mine
from database.database_access import DefaultSession


@pytest.mark.usefixtures("clear-db")
def test_farm_resource_gathering():
    with DefaultSession(autoflush=False) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "Mercury")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        town_hall = TownHall(level=1, settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(town_hall)
        session.commit()

        # We add some building materials
        planet.building_materials = 10000
        assert planet.building_materials
        session.commit()

        # You can choose either here:
        # farm_or_mine = Mine(settlement_id=settlement.settlement_id, grid_pos_x=3, grid_pos_y=2)
        farm = Farm(settlement_id=settlement.settlement_id, grid_pos_x=3, grid_pos_y=3)
        session.add(farm)
        session.commit()

        # We build a farm
        built: bool = settlement.build(farm)
        session.commit()
        assert built
        assert farm.gathering_time_left == 0
        assert farm.level == 1
        assert farm.construction_time_left == 10
        assert farm.gathering_time_left == 0
        assert not farm.is_gathering()
        assert farm.stored_resources == 0
        assert farm.capacity == 1000, "Change in default resource capacity"
        assert farm.production_rate == 200, "Change in default resource rate"

        # We wait 10 seconds until the building is over
        farm.update(10)
        session.commit()
        assert not farm.is_gathering()
        assert not farm.in_construction()
        assert farm.gathering_time_left == 0
        assert farm.construction_time_left == 0

        # We start gathering
        farm.start_gathering()
        session.commit()
        assert farm.is_gathering()
        assert farm.gathering_time_left > 0
        assert farm.stored_resources == 0

        # We gather for an hour
        farm.update(3600)
        session.commit()
        assert farm.is_gathering()
        assert farm.gathering_time_left > 0
        assert farm.stored_resources == 200
        assert not farm.collect_resources()

        # We wait another 4 hours (until the farm is full)
        farm.update(4 * 3600)
        session.commit()
        assert not farm.is_gathering()
        assert not farm.in_construction()
        assert farm.stored_resources == 1000
        assert farm.gathering_time_left == 0

        # We collect the farm
        farm.collect_resources()
        session.commit()
        assert not farm.is_gathering()
        assert farm.stored_resources == 0
        assert farm.gathering_time_left == 0
        assert planet.rations == 51000

        # We upgrade the farm
        farm.upgrade()
        session.commit()
        assert farm.level == 2
        assert farm.in_construction()
        assert farm.construction_time_left > 0
        assert planet.building_materials == 9550

        # We wait 60 seconds until it is built
        farm.update(60)
        session.commit()
        assert farm.level == 2
        assert not farm.in_construction()
        assert farm.construction_time_left == 0
        assert farm.production_rate == 400
        assert not farm.is_gathering()


@pytest.mark.usefixtures("clear-db")
def test_mine_resource_gathering():
    with DefaultSession(autoflush=False) as session:
        # Add a user
        user = User("test_user", "Test_password1")
        session.add(user)
        session.commit()

        planet = Planet(user.user_id, 1, 1, "Mercury")
        session.add(planet)
        session.commit()

        settlement = Settlement(1, planet.planet_id)
        session.add(settlement)
        session.commit()

        town_hall = TownHall(level=1, settlement_id=settlement.settlement_id, grid_pos_x=1, grid_pos_y=1)
        session.add(town_hall)
        session.commit()

        # We add some building materials
        planet.building_materials = 10000
        assert planet.building_materials
        session.commit()

        # You can choose either here:
        # farm_or_mine = Mine(settlement_id=settlement.settlement_id, grid_pos_x=3, grid_pos_y=2)
        mine = Mine(settlement_id=settlement.settlement_id, grid_pos_x=4, grid_pos_y=4)
        session.add(mine)
        session.commit()

        # We build a farm
        settlement.build(mine)
        session.commit()
        assert mine.gathering_time_left == 0
        assert mine.level == 1
        print(mine.construction_time_left)
        assert mine.construction_time_left == 10
        assert mine.gathering_time_left == 0
        assert not mine.is_gathering()
        assert not mine.is_gathering()
        assert mine.stored_resources == 0
        assert mine.capacity == 1000, "Change in default resource capacity"
        assert mine.production_rate == 200, "Change in default resource rate"

        # We wait 10 seconds until the building is over
        mine.update(10)
        session.commit()
        assert not mine.is_gathering()
        assert not mine.in_construction()
        assert mine.gathering_time_left == 0
        assert mine.construction_time_left == 0

        # We start gathering
        mine.start_gathering()
        session.commit()
        assert mine.is_gathering()
        assert mine.gathering_time_left > 0
        assert mine.stored_resources == 0

        # We gather for an hour
        mine.update(3600)
        session.commit()
        assert mine.is_gathering()
        assert mine.gathering_time_left > 0
        assert mine.stored_resources == 200
        assert not mine.collect_resources()

        # We wait another 4 hours (until the farm is full)
        mine.update(4 * 3600)
        session.commit()
        assert not mine.is_gathering()
        assert not mine.in_construction()
        assert mine.stored_resources == 1000
        assert mine.gathering_time_left == 0

        # We collect the mine
        mine.collect_resources()
        session.commit()
        assert not mine.is_gathering()
        assert mine.stored_resources == 0
        assert mine.gathering_time_left == 0
        assert planet.building_materials == 10850

        # We upgrade the farm
        mine.upgrade()
        session.commit()
        assert mine.level == 2
        assert mine.in_construction()
        assert mine.construction_time_left > 0
        assert planet.building_materials == 10550

        # We wait 60 seconds until it is built
        mine.update(60)
        session.commit()
        assert mine.level == 2
        assert not mine.in_construction()
        assert mine.construction_time_left == 0
        assert mine.production_rate == 400
        assert not mine.is_gathering()
