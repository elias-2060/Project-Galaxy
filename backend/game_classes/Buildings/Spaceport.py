from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from backend.game_classes.Buildings import Building, Barrack
from backend.game_classes.Ships.Spaceship import Spaceship
from backend.game_classes.Units import SpaceMarine, SpaceDrone, SpaceCommando
from backend.game_classes.properties import properties
from database.database_access import auto_session, default_factory

if TYPE_CHECKING:
    from backend.game_classes.Ships import LandedLocation, LandingLocation


class Spaceport(Building):
    __tablename__ = "spaceports"

    building_id: Mapped[UUID] = mapped_column(
        ForeignKey("buildings.building_id", ondelete="CASCADE"),
        primary_key=True,
    )
    "Id of the parent building"

    space_ship_id: Mapped[UUID] = mapped_column(
        ForeignKey("spaceships.ship_id", ondelete="CASCADE"), unique=True, nullable=True
    )
    "Ships connected to port"

    space_ship: Mapped[Spaceship] = relationship(back_populates="space_port")

    __mapper_args__ = {
        "polymorphic_identity": "spaceport",
    }

    __property_name__ = "spaceport"

    @property
    def max_ships(self) -> int:
        return properties["spaceport"]["level"][str(self.level)]["max_ships"]

    @property
    def production_time(self) -> int:
        return properties["spaceport"]["level"][str(self.level)]["production_time"]

    @default_factory(building_id=uuid1)
    def __init__(
        self,
        settlement_id: UUID,
        grid_pos_x: int,
        grid_pos_y: int,
        level: int = 1,
        building_id: UUID = None,
    ) -> None:
        assert isinstance(
            building_id, UUID
        ), f"building_id must be of type 'UUID' but is of type {type(building_id).__name__}"

        super().__init__(settlement_id, grid_pos_x, grid_pos_y, level=level, building_id=building_id)

    @auto_session
    def upgrade(self) -> bool:
        return super().upgrade()

    @auto_session
    def update(self, seconds: float) -> None:
        if self.space_ship is not None:
            self.space_ship.update(seconds)
        return super().update(seconds)

    def get_transportable_unit_counts(self):
        """
        Gets the transportable units count for this building
        """
        buildings = self.settlement.buildings
        barracks: list[Barrack] = [building for building in buildings if isinstance(building, Barrack)]

        # The results dictionary with the unit counts
        result: dict[str, int] = {
            "space_marine_nr": 0,
            "space_commando_nr": 0,
            "space_drone_nr": 0
        }

        # Get the number of units
        for barrack in barracks:
            for unit in barrack.get_available_units():
                if isinstance(unit, SpaceMarine):
                    result["space_marine_nr"] += 1
                elif isinstance(unit, SpaceCommando):
                    result["space_command_nr"] += 1
                elif isinstance(unit, SpaceDrone):
                    result["space_drone_nr"] += 1
                else:
                    raise ValueError(f"Unknown unit type {type(unit).__name__}")

        return result
