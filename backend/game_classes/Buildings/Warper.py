from sqlalchemy import ForeignKey

from uuid import UUID, uuid1

from database.database_access import default_factory, auto_session
from backend.game_classes.Buildings.Building import Building
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from backend.game_classes.properties import get_building_property

from backend.game_classes.PlanetLink import PlanetLink

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from backend.game_classes.Planet import Planet


class Warper(Building):
    __tablename__ = "warpers"

    building_id: Mapped[UUID] = mapped_column(
        ForeignKey("buildings.building_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    )

    planet_link: Mapped["PlanetLink"] = relationship(back_populates="warper")

    __mapper_args__ = {"polymorphic_identity": "warpers"}

    __property_name__ = "warper"

    @default_factory(building_id=uuid1)
    def __init__(
            self,
            settlement_id: UUID,
            grid_pos_x: int,
            grid_pos_y: int,
            *,
            level: int = 1,
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
    def has_link(self):
        """Checks if a link is associated with this Warper instance"""
        return self.planet_link

    @property
    def speed_factor(self):
        """
        Gets the speed-factor the warper instantiates
        """
        return get_building_property(self.__property_name__, "level", str(self.level + 1), "travel_factor")

    @auto_session
    def create_link(self, planet1: "Planet", planet2: "Planet", session: Session) -> PlanetLink:
        if self.settlement.planet.building_materials < 2000:
            raise ValueError("Building materials are too low")

        """Create a link between two planets"""
        if self.check_existing_link(planet1, planet2, session):
            return self.planet_link
        elif self.has_link:
            raise ValueError("This Warper instance already has a link associated with it.")
        new_link = PlanetLink(planet_from_id=planet1.planet_id, planet_to_id=planet2.planet_id,
                              warper_id=self.building_id)
        session.add(new_link)
        session.commit()
        self.planet_link: PlanetLink = new_link
        self.settlement.planet.building_materials -= 2000
        session.commit()
        return new_link

    @auto_session
    def get_warp_to(self) -> Optional["Planet"]:
        # Get the planet it is warped to
        if self.planet_link is not None:
            planet = self.settlement.planet.get_by_uuid(self.planet_link.planet_from_id)
            return planet
        else:
            return None

    def delete_link(self, session: Session):
        """Delete the link associated with this Warper instance"""
        if self.planet_link:
            session.delete(self.planet_link)
            session.commit()

    @auto_session
    def check_existing_link(self, planet1: "Planet", planet2: "Planet", session: Session) -> bool:
        """Check if there is an existing link between two planets"""
        existing_link = (
            session.query(PlanetLink)
            .filter_by(
                planet_from_id=planet1.planet_id,
                planet_to_id=planet2.planet_id
            )
            .first()
        )
        if existing_link is not None:
            print(f"Link already exists from {planet1.planet_name} to {planet2.planet_name}")
        return existing_link is not None

    @auto_session
    def get_possible_warp_locations(self, session: Session = None) -> list["Planet"]:
        """
        Gets the warp locations the planet can set up a warp to.
        """
        current_planet: "Planet" = self.settlement.planet

        # Get the possible warp locations
        user = self.settlement.planet.user
        other_planets = [planet for planet in current_planet.get_all_other_planets() if
                         (planet.planet_id != current_planet.planet_id)]

        def existing_link(planet_to: "Planet"):
            """
            Returns whether an existing link exists
            """
            link = session.query(PlanetLink).filter_by(
                planet_from_id=current_planet.planet_id,
                planet_to_id=planet_to.planet_id
            ).first()

            return link is not None

        # Remove planets where the link already exists
        other_planets = list(filter(lambda curr_planet: not existing_link(curr_planet), other_planets))

        return other_planets

    @auto_session
    def change_warp_link(self, planet_to_x: int, planet_to_y: int, session: Session) -> Optional["PlanetLink"]:
        """
        Changes the current warp link of the warper.
        """
        curr_user = self.settlement.planet.user
        curr_user.update()

        planet: "Planet" = self.settlement.planet

        # If the coordinates are none, remove the link
        if planet_to_y is None or planet_to_x is None:
            session.delete(self.planet_link)
            session.commit()
            return None

        # Get the other planet
        # noinspection PyTypeChecker
        planet_to: "Planet" = planet.get_by_pos(planet_to_x, planet_to_y, session=session)
        planet_to.user.update()

        # Make the planet link
        self.create_link(planet, planet_to, session=session)
        session.commit()

        return self.planet_link
