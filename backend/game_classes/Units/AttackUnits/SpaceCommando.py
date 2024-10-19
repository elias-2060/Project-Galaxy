from backend.game_classes.Units.AttackUnits.AttackUnit import AttackUnit
from database.database_access import default_factory, auto_session
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy import ForeignKey
from uuid import uuid1, UUID
from typing import TYPE_CHECKING
from random import randint

if TYPE_CHECKING:
    from backend.game_classes.Buildings.Barrack import Barrack


class SpaceCommando(AttackUnit):
    __tablename__ = "space_commandos"

    unit_id: Mapped[UUID] = mapped_column(ForeignKey("attack_units.unit_id", ondelete="CASCADE"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "space_commandos",
    }

    __property_name__ = "space_commando"

    @default_factory(unit_id=uuid1)
    def __init__(self, barrack_id: UUID, *, unit_id: UUID = None, level: int = 1) -> None:
        """
        Initialize a SpaceMarine object.
        """
        assert isinstance(unit_id, UUID), "unit_id must be of type 'UUID'"

        super().__init__(level=level, building_id=barrack_id, unit_id=unit_id)

    def get_round_result(self, roll_unit, roll_enemy) -> tuple[bool, bool, bool]:
        """
        Returns the round result for space commandos

        Passive: They always have a 5% of winning, thus turning the result into (True, False)
        """
        # Get the roll result and the result string
        unit_val, enemy_val, passive = super().get_round_result(roll_unit, roll_enemy)

        # If the result is already a win, no need to calculate the passive
        if unit_val and not enemy_val:
            return unit_val, enemy_val, passive

        # If that is not the case, we roll a 5% chance
        roll_result: bool = randint(0, 100) <= 5

        # If it hits, adjust the result
        if roll_result:
            passive = True
            unit_val = True
            enemy_val = False

        return unit_val, enemy_val, passive
