from uuid import UUID, uuid1

from typing import TYPE_CHECKING

from backend.game_classes.properties import get_building_property

if TYPE_CHECKING:
    from backend.game_classes.Settlement import Settlement
    from backend.game_classes.Planet import Planet

from sqlalchemy import ForeignKey, UniqueConstraint

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from database.database_access import Base, auto_session, default_factory


class Building(Base):
    __tablename__ = "buildings"
    building_id: Mapped[UUID] = mapped_column(primary_key=True)
    "Id of the building"

    settlement_id: Mapped[UUID] = mapped_column(ForeignKey("settlements.settlement_id", ondelete="CASCADE"))
    "Id of the settlement the building is in"

    settlement: Mapped["Settlement"] = relationship(back_populates="buildings")
    "Settlement the building is in"

    grid_pos_x: Mapped[int]
    "Y position on the settlement grid"

    grid_pos_y: Mapped[int]
    "X position on the settlement grid"

    level: Mapped[int]
    "Level of the building"

    construction_time_left: Mapped[float]
    "Time left until the building is constructed"

    # Type is automatically stored here for polymorphisms
    type: Mapped[str]
    "Type of the building. Needed for inheritance mapping"

    __table_args__ = (UniqueConstraint("settlement_id", "grid_pos_x", "grid_pos_y"),)
    __mapper_args__ = {
        "polymorphic_identity": "buildings",
        "polymorphic_on": "type",
    }

    __property_name__ = None
    "Name of the top level building property in the config"

    @property
    def max_level(self) -> int:
        """Get the max level"""
        return get_building_property(self.__property_name__, "max_level")

    @property
    def build_cost(self) -> int | None:
        """Get the cost of the next level. Is None if max level is reached"""
        if self.level >= self.max_level:
            return None
        return get_building_property(self.__property_name__, "level", str(self.level + 1), "build_cost")

    @property
    def upgrade_time(self) -> int | None:
        """Get the upgrade time of the next level. Is None if max level is reached"""
        if self.level >= self.max_level:
            return None
        return get_building_property(self.__property_name__, "level", str(self.level + 1), "upgrade_time")

    @property
    def display_name(self) -> str:
        """Get the display name"""
        return get_building_property(self.__property_name__, "display_name")

    @default_factory(building_id=uuid1)
    def __init__(
        self,
        settlement_id: UUID,
        grid_pos_x: int,
        grid_pos_y: int,
        *,
        level: int = 1,
        building_id: UUID = None,
    ) -> None:
        """
        Initialize a Building object.
        """
        assert isinstance(building_id, UUID), "building_id must be of type 'UUID'"

        self.settlement_id: UUID = settlement_id
        self.grid_pos_x: int = grid_pos_x
        self.grid_pos_y: int = grid_pos_y
        self.level: int = level
        self.building_id: UUID = building_id
        self.construction_time_left: float = 0

    @auto_session
    def store(self, session: Session = None) -> None:
        try:
            session.commit()
        except IntegrityError as DuplicateErr:
            print(type(DuplicateErr))  # the exception type
            print("Cannot Store Building. Building already exist. id :" + self.building_id.__str__() + " )")

        except Exception as err:
            print(type(err))  # the exception type

    def update(self, seconds: float) -> None:
        """
        Virtual function, so when the derived function doesn't get called, it's not a problem.
        """
        # If the building is being built, update the built time left:
        if self.construction_time_left > 0:
            self.construction_time_left -= seconds
            if self.construction_time_left < 0:
                self.construction_time_left: float = 0

    @auto_session(auto_commit=True)
    def upgrade(self) -> bool:
        """
        Virtual function to upgrade the building, returns boolean value of whether it is possible
        """
        # If the building is already being upgraded, return False:
        if self.construction_time_left > 0 or self.level >= self.max_level:
            return False

        # Get the amount of building materials on the planet
        settlement: "Settlement" = self.settlement
        planet: "Planet" = settlement.planet
        building_materials: int = planet.building_materials

        # If it is not enough, return False
        if building_materials - self.build_cost < 0:
            return False

        # Else we just take the planet and extract the resources
        planet.building_materials -= self.build_cost
        planet.store()

        # Adjust the upgrade time
        self.construction_time_left: float = float(self.upgrade_time)

        # Increase the level of the building
        self.level += 1
        return True

    def in_construction(self) -> bool:
        """
        Function that returns whether the building is in construction
        """
        return self.construction_time_left > 0
