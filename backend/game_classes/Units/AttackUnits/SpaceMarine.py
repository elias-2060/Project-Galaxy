from backend.game_classes.Units.AttackUnits.AttackUnit import AttackUnit
from database.database_access import default_factory, auto_session
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from uuid import uuid1, UUID
from typing import TYPE_CHECKING


class SpaceMarine(AttackUnit):
    __tablename__ = "space_marines"

    unit_id: Mapped[UUID] = mapped_column(ForeignKey("attack_units.unit_id", ondelete="CASCADE"), primary_key=True)

    combats_survived: Mapped[int]

    __mapper_args__ = {"polymorphic_identity": "space_marines"}

    __property_name__ = "space_marine"

    @property
    def attack_power(self) -> int:
        """
        Returns the attack_power of a unit, per 2 combats survived there will be added 10 points
        """
        return super().attack_power + (int(self.combats_survived / 2) * 10)  # Always rounds down

    @default_factory(unit_id=uuid1)
    def __init__(self, barrack_id: UUID, *, unit_id: UUID = None, level: int = 1) -> None:
        """
        Initialize a SpaceMarine object.
        """
        assert isinstance(unit_id, UUID), "unit_id must be of type 'UUID'"
        super().__init__(level=level, building_id=barrack_id, unit_id=unit_id)
        self.combats_survived: int = 0

    def get_round_result(self, roll_unit, roll_enemy) -> tuple[bool, bool, bool]:
        """
        Returns the round result space marines

        Passive: Per 2 combats survived, the unit gets 10 Attack Power
        """
        # We can add a combat round, because the unit will get deleted if it loses
        self.combats_survived += 1
        x, y, passive = super().get_round_result(roll_unit, roll_enemy)
        return x, y, x

