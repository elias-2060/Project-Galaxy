from uuid import UUID, uuid1
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.game_classes.Ships.ship import Ship
from database.database_access import default_factory


class ColonyShip(Ship):
    __tablename__ = "colony_ships"

    ship_id: Mapped[UUID] = mapped_column(ForeignKey("ships.ship_id"), primary_key=True)
    "Id of the ship"

    __mapper_args__ = {"polymorphic_identity": "colony_ship"}

    @default_factory(ship_id=uuid1)
    def __init__(self, owner_id: UUID, ship_id: UUID = None):
        super().__init__(owner_id, ship_id=ship_id)
