from backend.game_classes.Units.Unit import Unit
from backend.game_classes.properties import get_unit_property
from database.database_access import default_factory, auto_session
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from sqlalchemy import ForeignKey
from uuid import uuid1, UUID
from typing import TYPE_CHECKING, Optional
from random import randint

if TYPE_CHECKING:
    from backend.game_classes.Buildings.Barrack import Barrack
    from backend.game_classes.Ships.Spaceship import Spaceship


class AttackUnit(Unit):
    __tablename__ = "attack_units"

    unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("units.unit_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )

    building_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("barracks.building_id", ondelete="CASCADE"))

    barrack: Mapped[Optional["Barrack"]] = relationship(back_populates="attack_units")

    spaceship_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("spaceships.ship_id", ondelete="CASCADE"))

    spaceship: Mapped[Optional["Spaceship"]] = relationship(back_populates="attack_units")

    # Is time since last time the unit consumed rations
    seconds_since_last_feed: Mapped[float]  # Every hour the attack unit consumes food

    # When a unit is being trained, this is the position in the training queue of the item
    training_pos: Mapped[int | None]

    # The remaining training time (seconds), this is set by the Barrack, and gotten from a getter function in this
    # class.
    training_time_left: Mapped[float]

    __mapper_args__ = {
        "polymorphic_identity": "attack_units",
    }

    __property_name__ = None
    "Name of the top level unit property in the config"

    @property
    def max_level(self) -> int:
        """Get the max level"""
        return get_unit_property(self.__property_name__, "max_level")

    @property
    def size(self) -> int:
        """Get the size of the unit"""
        return get_unit_property(self.__property_name__, "size")

    @property
    def attack_power(self) -> int:
        """Get the attack power of the unit"""
        return get_unit_property(self.__property_name__, "level", str(self.level), "attack_power")

    @property
    def rations_per_hour(self) -> int:
        """Get the rations per hour the unit consumes"""
        return get_unit_property(self.__property_name__, "level", str(self.level), "rations_per_hour")
    
    @property
    def training_time(self) -> int:
        """Get the training time of the unit """
        return get_unit_property(self.__property_name__, "level", str(self.level), "training_time")

    @property
    def training_cost(self) -> int:
        """Get the training cost of the unit"""
        return get_unit_property(self.__property_name__, "level", str(self.level), "training_cost")

    @property
    def upgrade_cost(self) -> int | None:
        """Get the upgrade cost of the unit"""
        if self.level >= self.max_level:
            return None
        return get_unit_property(self.__property_name__, "level", str(self.level), "upgrade_cost")

    @default_factory(unit_id=uuid1)
    def __init__(self, building_id: UUID, *, level: int = 1, unit_id: UUID = None):
        # Assertion check for the type of the unit ID (UUID)
        assert isinstance(unit_id, UUID)

        super().__init__(level=level, unit_id=unit_id)
        self.building_id: UUID = building_id
        self.seconds_since_last_feed: float = 0
        self.training_pos: int | None = None
        self.training_time_left: float = 0

    @auto_session
    def update(self, seconds) -> bool:
        """
        Updates the unit, it calculates the amount of food it used up.
        """
        # When a unit is in training, we don't do anything
        if self.in_training():
            return True

        # If the unit is not in training, it consumes food every hour, so we've added up extra seconds to the last
        # time since the unit got fed.
        self.seconds_since_last_feed += seconds

        # If the time is more than an hour, we remove the used food
        while self.seconds_since_last_feed >= 3600:
            # If there's not enough food, give false, and the barrack will remove the unit
            if self.barrack.settlement.planet.rations - self.rations_per_hour < 0:
                self.barrack.settlement.planet.rations = 0
                return False

            # Else we Remove the food
            self.barrack.settlement.planet.rations -= self.rations_per_hour

            # Take an hour of the last fed time
            self.seconds_since_last_feed -= 3600

        return True

    @staticmethod
    def get_training_cost_static(class_name: str, level: int) -> int:
        return get_unit_property(class_name, "level", str(level), "training_cost")

    def in_training(self) -> bool:
        """
        Returns whether the unit is in training.
        """
        return self.training_pos is not None

    def is_traveling(self) -> bool:
        """
        Returns whether the unit is on spaceship.
        """
        return self.spaceship_id is not None

    def roll_dice(self) -> int:
        """
        Function that generates an integer that shows the chance of winning.
        """
        # Generates a random number between 0 and the attack power
        dice_result = randint(0, self.attack_power)
        return dice_result

    def get_round_result(self, roll_unit, roll_enemy) -> tuple[bool, bool, str]:
        """
        Virtual function for the round result

        The first item of the result is a bool that indicates whether the unit lives.
        The second item of the result is a bool that indicates whether the opponent lives.
        The third item is a string that indicates whether there were any passives used.
        """
        if roll_unit > roll_enemy:
            return True, False, False
        elif roll_unit < roll_enemy:
            return False, True, False
        else:
            return False, False, False
