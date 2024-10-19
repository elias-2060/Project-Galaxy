from backend.game_classes.Units.AttackUnits.AttackUnit import AttackUnit
from database.database_access import default_factory, auto_session
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy import ForeignKey
from uuid import uuid1, UUID
from typing import TYPE_CHECKING
from random import randint

if TYPE_CHECKING:
    from backend.game_classes.Buildings.Barrack import Barrack


class SpaceDrone(AttackUnit):
    __tablename__ = "space_drones"

    unit_id: Mapped[UUID] = mapped_column(ForeignKey("attack_units.unit_id", ondelete="CASCADE"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "space_drones"}

    __property_name__ = "space_drone"

    @default_factory(unit_id=uuid1)
    def __init__(self, barrack_id: UUID, *, unit_id: UUID = None, level: int = 1) -> None:
        """
        Initialize a SpaceMarine object.
        """
        assert isinstance(unit_id, UUID), "unit_id must be of type 'UUID'"
        super().__init__(level=level, building_id=barrack_id, unit_id=unit_id)

    def get_round_result(self, roll_unit, roll_enemy) -> tuple[bool, bool, bool]:
        """
        Returns the round result for space drones

        Passive 1: Even if it wins, it can die 5% of the time due to engine failure
        Passive 2: If it dies, it has a 25% chance to take the enemy with it due to explosion
        """
        # Get the roll result and the result string
        unit_val, enemy_val, passive = super().get_round_result(roll_unit, roll_enemy)

        # Passive 1:
        if unit_val:
            # We roll a 5% chance
            roll_result: bool = randint(0, 100) <= 5

            # 5% chance for the unit to die
            if roll_result:
                unit_val = False
                passive = True

        # Passive 2:
        if not unit_val and enemy_val:
            # We roll a 25% chance
            roll_result: bool = randint(0, 100) <= 25

            # If it hits, the enemy unit dies too
            if roll_result:
                enemy_val = False
                passive = True

        # Return the result
        return unit_val, enemy_val, passive
