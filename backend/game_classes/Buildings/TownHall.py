from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid1
from backend.game_classes.Buildings import Building
from database.database_access import default_factory


class TownHall(Building):
    __tablename__ = "town_halls"

    building_id: Mapped[UUID] = mapped_column(
        ForeignKey("buildings.building_id", ondelete="CASCADE"),
        primary_key=True,
    )
    "Id of the building"

    __mapper_args__ = {"polymorphic_identity": "town_halls", }

    __property_name__ = "town_hall"

    @default_factory(building_id=uuid1)
    def __init__(
            self,
            settlement_id: UUID,
            grid_pos_x: int,
            grid_pos_y: int,
            *,
            level: int = 0,
            building_id: UUID = None
    ):

        assert isinstance(building_id, UUID), "building_id must be of type 'UUID'"
        super().__init__(settlement_id=settlement_id, grid_pos_x=grid_pos_x, grid_pos_y=grid_pos_y,
                         building_id=building_id, level=level)