from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid1
from backend.game_classes.properties import get_building_property
from database.database_access import default_factory, auto_session
from backend.game_classes.Buildings.Building import Building

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.game_classes.Planet import Planet


class Farm(Building):
    __tablename__ = "farms"

    building_id: Mapped[UUID] = mapped_column(ForeignKey("buildings.building_id", ondelete="CASCADE"), primary_key=True)
    "Id of the building"

    stored_resources: Mapped[int]
    "Amount of resources stored"

    gathering_time_left: Mapped[float]
    "Time left until the resource is gathered"

    __mapper_args__ = {"polymorphic_identity": "farms"}

    __property_name__ = "farm"

    @property
    def production_rate(self) -> int:
        """Amount of resources produced per hour"""
        return get_building_property(self.__property_name__, "level", str(self.level), "production_rate")

    @property
    def capacity(self) -> int:
        """Maximum amount of resources that can be stored"""
        return get_building_property(self.__property_name__, "level", str(self.level), "capacity")

    @default_factory(building_id=uuid1)
    def __init__(
        self,
        settlement_id: UUID,
        grid_pos_x: int,
        grid_pos_y: int,
        *,
        level: int = 0,
        building_id: UUID = None,
    ):
        assert isinstance(building_id, UUID), "building_id must be of type 'UUID'"

        super().__init__(
            settlement_id=settlement_id,
            grid_pos_x=grid_pos_x,
            grid_pos_y=grid_pos_y,
            building_id=building_id,
            level=level,
        )

        self.gathering_time_left: float = 0
        self.stored_resources: int = 0

    def upgrade(self) -> bool:
        """
        Virtual function that does an extra check whether it is gathering resources
        """
        # Extra check for whether it is gathering resources
        return (not self.is_gathering()) and super().upgrade()

    @auto_session(auto_commit=True)
    def update(self, seconds: float) -> None:
        """
        Returns the amount of resources that have been collected since the last update
        """
        # First, we call the function from the superclass
        super().update(seconds)

        # If it's gathering, remove the time from the gathering time and store the resources in the farm
        if self.is_gathering():
            self.gathering_time_left -= seconds
            self.stored_resources += int(seconds * self.production_rate / 3600)
            if self.gathering_time_left <= 0:
                self.gathering_time_left: float = 0
                self.stored_resources: int = self.capacity

    def is_gathering(self) -> bool:
        """
        Returns whether the farm is gathering rations
        """
        return self.gathering_time_left > 0

    @auto_session
    def collect_resources(self) -> bool:
        """
        Function that collects the gained resources
        """
        # It is only possible to collect when it is done gathering resources
        if self.is_gathering():
            return False

        # Add the collected rations to the planet
        planet: "Planet" = self.settlement.planet
        planet.rations += self.stored_resources

        # Reset the gathering values
        self.stored_resources: int = 0
        self.gathering_time_left: float = 0
        return True

    @auto_session
    def start_gathering(self) -> bool:
        """
        This function starts gathering the resources
        """
        # If the farm is in construction or still gathering, we don't start gathering
        if self.in_construction() or self.is_gathering():
            return False

        # We calculate the number of seconds it takes to fill up the farm, and set the gathering time equal to this
        fill_up_time: float = (
            self.capacity / self.production_rate * 3600
        )
        self.gathering_time_left: float = fill_up_time
