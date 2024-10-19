from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from database.database_access import Base, default_factory, auto_session

if TYPE_CHECKING:
    from backend.game_classes.Buildings.Warper import Warper, Planet


class PlanetLink(Base):
    __tablename__ = "planet_links"

    link_id: Mapped[UUID] = mapped_column(primary_key=True)

    planet_from_id: Mapped[UUID] = mapped_column(
        ForeignKey("planets.planet_id", ondelete="CASCADE", onupdate="CASCADE"))
    planet_to_id: Mapped[UUID] = mapped_column(ForeignKey("planets.planet_id", ondelete="CASCADE", onupdate="CASCADE"))

    warper_id: Mapped[UUID] = mapped_column(ForeignKey("warpers.building_id", ondelete="CASCADE", onupdate="CASCADE"),
                                            nullable=False)
    warper: Mapped["Warper"] = relationship(back_populates="planet_link")

    __table_args__ = (UniqueConstraint("planet_from_id", "planet_to_id"),)

    @default_factory(link_id=uuid1)
    def __init__(self, planet_from_id: UUID, planet_to_id: UUID, warper_id: UUID, link_id: UUID = None):
        self.link_id = link_id

        self.planet_from_id = planet_from_id
        self.planet_to_id = planet_to_id
        self.warper_id = warper_id

    def speed_factor(self) -> float:
        return 3.0 * self.warper.level

    @auto_session
    def get_planet_to(self) -> "Planet":
        """
        Gets the planet to
        """
        planet = self.warper.settlement.planet
        planet_to = planet.get_by_uuid(self.planet_to_id)
        return planet_to
