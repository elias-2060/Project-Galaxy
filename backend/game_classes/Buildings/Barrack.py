from uuid import UUID, uuid1

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from backend.game_classes.Buildings.Building import Building
from backend.game_classes.properties import get_building_property, get_unit_property
from backend.game_classes.Units.AttackUnits import AttackUnit, SpaceCommando, SpaceDrone, SpaceMarine
from database.database_access import auto_session, default_factory


class Barrack(Building):
    __tablename__ = "barracks"

    building_id: Mapped[UUID] = mapped_column(
        ForeignKey("buildings.building_id", ondelete="CASCADE"),
        primary_key=True,
    )
    "Id of the building"

    # List of units that are in this barrack, this is private because adding and removing needs to happen through
    # functions
    attack_units: Mapped[list[AttackUnit]] = relationship()
    "List of units that are in this barrack"

    # The levels of all the units the barrack can train
    space_marine_level: Mapped[int]
    "Level of the space marines"
    space_commando_level: Mapped[int]
    "Level of the space commandos"
    space_drone_level: Mapped[int]
    "Level of the space drones"

    __mapper_args__ = {"polymorphic_identity": "barracks"}

    __property_name__ = "barrack"

    @property
    def max_capacity(self):
        return get_building_property(self.__property_name__, "level", str(self.level), "max_capacity")

    @default_factory(building_id=uuid1)
    def __init__(
        self,
        settlement_id: UUID,
        grid_pos_x: int,
        grid_pos_y: int,
        *,
        level: int = 0,
        building_id: UUID = None,
        space_marine_level: int = 1,
        space_commando_level: int = 1,
        space_drone_level: int = 1
    ):

        assert isinstance(building_id, UUID), "building_id must be of type 'UUID'"

        super().__init__(
            settlement_id=settlement_id,
            grid_pos_x=grid_pos_x,
            grid_pos_y=grid_pos_y,
            building_id=building_id,
            level=level,
        )

        # Set the levels of the units
        self.space_marine_level: int = space_marine_level
        self.space_commando_level: int = space_commando_level
        self.space_drone_level: int = space_drone_level

    def get_space_taken(self) -> int:
        """
        Returns the current total amount of storage taken by the units inside the barrack
        """
        return sum(attack_unit.size for attack_unit in self.attack_units)

    def get_available_units(self) -> list[AttackUnit]:
        """
        Return the list of available units in the barrack
        """
        return [unit for unit in self.attack_units if not unit.in_training()]

    @auto_session
    def update(self, seconds: float, session: Session = None) -> None:
        """
        Updates the barrack, checks all the units whether they have enough food
        """
        # First call the parent function:
        super().update(seconds)

        # Check all the units for food consumption
        attack_units: list[AttackUnit] = self.attack_units

        # We go per list over each unit
        for unit in attack_units:
            # We update the unit, and if it returns False (food shortage), we remove it
            if unit.update(seconds) is False:
                session.delete(unit)

        # If there are no units in training, the function stops here
        units_in_training: list[AttackUnit] = self.get_units_in_training()
        if len(units_in_training) == 0:
            return

        # We take the currently trained unit
        unit: AttackUnit = units_in_training[0]
        trained_unit_list: list[AttackUnit] = units_in_training
        assert unit.training_time_left > 0, "Unit is not actually in training"

        # If the seconds since last updates are more than the remaining training time:
        while unit.training_time_left <= seconds and len(trained_unit_list) > 0:
            # Remove the remaining training time from the total time
            seconds -= unit.training_time_left

            # Now we remove the unit from training
            unit.training_time_left = 0
            unit.training_pos = None
            assert not unit.in_training()

            # After this, we adjust all the priorities of the units that are left in training:
            trained_unit_list = trained_unit_list[1:]
            for unit in trained_unit_list:
                assert unit.in_training(), "Unit not in training"
                unit.training_pos -= 1

            # We set the next unit equal to the next unit in priority
            if len(trained_unit_list) > 0:
                unit = trained_unit_list[0]

        # If the training time left is larger than the number of seconds left
        if unit.training_time_left > seconds:
            unit.training_time_left -= seconds

    @auto_session
    def train_unit(self, unit: AttackUnit) -> str | None:
        """
        This function trains a unit if it is possible, otherwise will return the error message.
        """
        # We do all checks, and return the result if it fails
        check_result: str | None = self.can_train_unit(unit)
        if check_result:
            return check_result

        # Now we start training the unit, we start by subtracting the food cost from the planet
        self.settlement.planet.rations -= unit.training_cost

        # Now we add it to the training queue
        unit.building_id = self.building_id

        # We set the training time to the training value of the unit:
        unit.training_time_left = unit.training_time
        assert unit.training_time_left > 0

        # We set the training position of the unit:
        unit.training_pos = len(self.get_units_in_training()) + 1

    def get_units_in_training(self):
        """
        Returns the units that are in training in correct order of training priority
        """
        # We make a list of None with the max size of the training queue (5)
        ordered_list: list[AttackUnit | None] = [None, None, None, None, None]

        # Now we put all items in the right spot (ordered by training priority, i.e., priority 1 -> position 0).
        for unit in self.attack_units:
            if unit.in_training():
                ordered_list[unit.training_pos - 1] = unit

        # We remove excessive Nones
        while len(ordered_list) > 0 and ordered_list[-1] is None:
            ordered_list = ordered_list[:-1]

        # We check whether there are no empty spots in between the queue
        assert None not in ordered_list

        return ordered_list

    @auto_session
    def can_train_unit(self, unit: AttackUnit) -> str | None:
        """
        Checks whether a unit can be trained. If this is not the case, return an error message.
        """
        # Check whether the unit is the correct level
        if isinstance(unit, SpaceMarine) and unit.level != self.space_marine_level:
            return "Unit level doesn't match barrack's unit level"
        elif isinstance(unit, SpaceCommando) and unit.level != self.space_commando_level:
            return "Unit level doesn't match barrack's unit level"
        elif isinstance(unit, SpaceDrone) and unit.level != self.space_drone_level:
            return "Unit level doesn't match barrack's unit level"

        # Check whether the building is under construction:
        if self.in_construction():
            return "Barrack is under construction"

        # Check whether the unit can be stored
        if self.get_space_taken() > self.max_capacity:
            return "Barrack does not have enough space"

        # Check the food cost of training the unit
        train_cost: int = unit.training_cost
        if train_cost > self.settlement.planet.rations:
            return "Planet does not have enough food"

        # We check whether the training queue is full
        if len(self.get_units_in_training()) >= 5:
            return "Barrack has a full queue already"

        # Check whether the unit can be trained by the barrack:
        if isinstance(unit, SpaceMarine):
            if self.level < 1:
                return "Barrack hasn't unlocked unit"
        elif isinstance(unit, SpaceCommando):
            if self.level < 2:
                return "Barrack hasn't unlocked unit"
        elif isinstance(unit, SpaceDrone):
            if self.level < 3:
                return "Barrack hasn't unlocked unit"
        else:
            raise NotImplementedError(type(unit).__name__)

    def upgrade_unit_type(self, unit_type: type[AttackUnit]) -> bool:
        """
        Upgrades a unit type in the barrack.
        This makes it so all units that are trained of this type now have the
        new level.
        """
        building_materials: int = self.settlement.planet.building_materials
        if unit_type == SpaceCommando:
            upgrade_cost = get_unit_property(unit_type.__property_name__,
                                             "level",
                                             str(self.space_commando_level + 1),
                                             "upgrade_cost"
                                             )
            if upgrade_cost > building_materials:
                return False
            self.settlement.planet.building_materials -= upgrade_cost
            self.space_commando_level += 1
        elif unit_type == SpaceMarine:
            upgrade_cost = get_unit_property(
                unit_type.__property_name__,
                "level", str(self.space_marine_level + 1),
                "upgrade_cost"
            )
            if upgrade_cost > building_materials:
                return False
            self.settlement.planet.building_materials -= upgrade_cost
            self.space_marine_level += 1
        elif unit_type == SpaceDrone:
            upgrade_cost = get_unit_property(
                unit_type.__property_name__,
                "level",
                str(self.space_drone_level + 1),
                "upgrade_cost"
            )
            if upgrade_cost > building_materials:
                return False
            self.settlement.planet.building_materials -= upgrade_cost
            self.space_drone_level += 1
        else:
            raise NotImplementedError(unit_type.__name__)

        return True

    @auto_session
    def get_disabled_units(self) -> dict[str, bool]:
        """
        Gets all the disabled units for the barrack
        """
        result = {
            "SpaceMarine": False,
            "SpaceCommando": False,
            "SpaceDrone": False
        }
        # If the building is under construction, you can't adjust anything
        if self.in_construction():
            result["SpaceMarine"] = True
            result["SpaceCommando"] = True
            result["SpaceDrone"] = True

        # Check for capacity shortcomings
        if self.max_capacity - self.get_space_taken() < 3:
            result["SpaceMarine"] = True
        if self.max_capacity - self.get_space_taken() < 6:
            result["SpaceCommando"] = True
        if self.max_capacity - self.get_space_taken() < 20:
            result["SpaceDrone"] = True

        # Check for rations shortcomings
        rations: int = self.settlement.planet.rations
        if rations - AttackUnit.get_training_cost_static("space_marine", self.space_marine_level) < 0:
            result["SpaceMarine"] = True
        if rations - AttackUnit.get_training_cost_static("space_commando", self.space_commando_level) < 0:
            result["SpaceCommando"] = True
        if rations - AttackUnit.get_training_cost_static("space_drone", self.space_drone_level) < 0:
            result["SpaceDrone"] = True

        # For the unlocked levels
        if self.level < 1:
            result["SpaceMarine"] = True
        if self.level < 2:
            result["SpaceCommando"] = True
        if self.level < 3:
            result["SpaceDrone"] = True

        return result
