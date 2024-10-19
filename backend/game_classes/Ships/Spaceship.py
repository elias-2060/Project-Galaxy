from uuid import UUID, uuid1
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.game_classes.Ships.ship import Ship
from database.database_access import auto_session, Session, default_factory
from backend.game_classes.properties import get_spaceship_property
from backend.game_classes.Buildings.Barrack import Barrack
from typing import Optional, TYPE_CHECKING
from backend.game_classes.PlanetLink import PlanetLink
from math import sqrt

if TYPE_CHECKING:
    from backend.game_classes.Units.AttackUnits.AttackUnit import AttackUnit
    from backend.game_classes.Buildings import Spaceport
    from backend.game_classes.Planet import Planet


class Spaceship(Ship):
    __tablename__ = "spaceships"

    ship_id: Mapped[UUID] = mapped_column(ForeignKey("ships.ship_id", ondelete="CASCADE"), primary_key=True)
    "Id of the ship"

    building_materials: Mapped[int]
    rations: Mapped[int]
    attack_units: Mapped[Optional[list["AttackUnit"]]] = relationship()

    space_port: Mapped["Spaceport"] = relationship(back_populates="space_ship")

    current_destination_id: Mapped[UUID] = mapped_column(ForeignKey("planets.planet_id"), nullable=True)

    destination: Mapped["Planet"] = relationship(back_populates="incoming_spaceships")

    moving_time_left: Mapped[float]
    "Remaining travel time of the spaceship"

    __mapper_args__ = {"polymorphic_identity": "spaceship"}
    __property_name__ = "spaceship"

    @property
    def travel_speed_factor(self) -> float:
        """
        Get the travel speed amplifying factor based on spaceship level.
        """
        return get_spaceship_property(self.__property_name__, "level", str(self.level), "travel_speed_factor")

    @property
    def unit_capacity(self) -> int:
        return get_spaceship_property(self.__property_name__, "level", str(self.level), "unit_capacity")

    @property
    def resource_capacity(self) -> int:
        return get_spaceship_property(self.__property_name__, "level", str(self.level), "resource_capacity")

    @property
    def level(self) -> int:
        return self.space_port.level

    @default_factory(ship_id=uuid1)
    def __init__(self, owner_id: UUID, ship_id: UUID = None):

        super().__init__(owner_id=owner_id, ship_id=ship_id)

        self.rations: int = 0
        self.building_materials: int = 0

        self.moving_time_left: float = 0
        self.moving_time: float = 0

    @auto_session
    def board_building_materials(self, from_planet: "Planet", building_materials_amount: int, session: Session) -> None:
        """
        Board building materials from the given planet onto the spaceship.
        """
        if self.is_moving():
            raise ValueError("Can not board materials while the spaceship is moving.")
        if from_planet.building_materials < building_materials_amount:
            raise ValueError("The planet (" + from_planet.planet_name + ") does not have " +
                             str(building_materials_amount) + " building materials.")

        from_planet.building_materials -= building_materials_amount
        self.building_materials += building_materials_amount
        session.commit()

    @auto_session
    def board_rations(self, from_planet: "Planet", amount: int, session: Session) -> None:
        """
        Board rations from the given planet onto the spaceship.
        """
        if self.is_moving():
            raise ValueError("Can not board rations while the spaceship is moving.")
        if from_planet.rations < amount:
            raise ValueError("The planet (" + from_planet.planet_name + ") does not have " + str(amount) + " rations.")

        from_planet.rations -= amount
        self.rations += amount
        session.commit()

    @auto_session
    def unload_resources(self, planet_to: "Planet", session: Session) -> None:
        """
        Unload resources onto the destination planet.
        """
        planet_to.add_rations(self.rations)
        self.rations = 0
        planet_to.add_building_materials(self.building_materials)
        self.building_materials = 0
        session.commit()

    @auto_session
    def board_attack_unit(self, attack_unit: "AttackUnit",
                          session: Session) -> None:
        """
        Board attack units from the given planet onto the spaceship.
        """
        if self.is_moving():
            raise ValueError("Cannot board units while the spaceship is moving.")

        attack_unit.building_id = None
        attack_unit.spaceship_id = self.ship_id
        self.attack_units.append(attack_unit)
        session.commit()

    @auto_session
    def check_space_in_barracks(self, planet: "Planet", attack_unit: "AttackUnit") -> bool:
        """
        Check if there is enough space in the barracks on the destination planet for all units.
        """
        barracks = self.find_available_barracks(planet)
        total_space_needed = sum(unit.size for unit in self.attack_units) + attack_unit.size
        total_space_available = sum(barrack.max_capacity - barrack.get_space_taken() for barrack in barracks)
        return total_space_available >= total_space_needed

    @staticmethod
    def find_available_barracks(planet: "Planet") -> list[Barrack]:
        """
        Find available barracks on the planet for units.
        """
        return [
            building for settlement in planet.settlements
            for building in settlement.buildings
            if isinstance(building, Barrack) and building.get_space_taken() < building.max_capacity
        ]

    @auto_session
    def unload_units(self, planet_to: "Planet", session: Session) -> None:
        """
        Unload units onto the destination planet.
        """
        barracks = self.find_available_barracks(planet_to)
        for barrack in barracks:
            for attack_unit in self.attack_units:
                if (barrack.get_space_taken() + attack_unit.size) < barrack.max_capacity:
                    self.move_attack_unit_to_barrack(attack_unit, barrack, session)
                else:
                    break

    @auto_session
    def move_attack_unit_to_barrack(self, attack_unit: "AttackUnit", barrack: Barrack, session: Session) -> None:
        """
        Move the attack unit to the barrack.
        """
        attack_unit.building_id = barrack.building_id
        attack_unit.spaceship_id = None
        barrack.attack_units.append(attack_unit)
        self.attack_units.remove(attack_unit)
        session.commit()

    @staticmethod
    def find_planet_link(planet_from: "Planet", planet_to: "Planet", session: Session) -> Optional[PlanetLink]:
        """
        Find the link between two planets.
        """
        return (
            session.query(PlanetLink)
            .filter(
                (PlanetLink.planet_from_id == planet_from.planet_id) &
                (PlanetLink.planet_to_id == planet_to.planet_id) |
                (PlanetLink.planet_from_id == planet_from.planet_id) &
                (PlanetLink.planet_to_id == planet_to.planet_id)
            )
            .first()
        )

    @auto_session
    def validate_movement(self, from_planet: "Planet", to_planet: "Planet", session: Session) -> None:
        """
        Validate if the spaceship can move from one planet to another.
        """
        existing_link = self.find_planet_link(from_planet, to_planet, session)
        if existing_link is None:
            raise ValueError("Destination planet is not reachable. There is no link between " +
                             from_planet.planet_name + " and " + to_planet.planet_name + ".")
        if self.is_moving():
            raise ValueError("Spaceship is already moving.")

    @auto_session
    def is_moving(self, session: Session = None) -> bool:
        """
        Check if the spaceship is currently moving.
        """
        return self.moving_time_left > 0

    @staticmethod
    def distance_between_planets(planet_from: "Planet", planet_to: "Planet") -> float:
        """
        Calculate the distance between two planets.
        """
        delta_x = planet_from.planet_x - planet_to.planet_x
        delta_y = planet_from.planet_y - planet_to.planet_y
        return sqrt(delta_x ** 2 + delta_y ** 2)

    @auto_session(auto_commit=True)
    def update(self, seconds: float, session: Session) -> None:
        """
        Update the spaceship status.
        """
        super().update(False)
        if self.is_moving():
            self.moving_time_left -= seconds
            if self.moving_time_left <= 0:
                # Get the remaining time moving
                time_left = -self.moving_time_left
                self.moving_time_left = 0

                # If it arrived back:
                if self.destination.planet_id == self.space_port.settlement.planet_id:
                    self.destination = None

                # If it reached the destination, turn back
                else:
                    self.unload_resources(self.destination)
                    self.unload_units(self.destination, session)
                    self.move_from_to_planet(self.destination, self.space_port.settlement.planet)
                    self.update(time_left)

        session.commit()

    @auto_session
    def move_from_to_planet(self, from_planet: "Planet", to_planet: "Planet", session: Session) -> None:
        """
        Move the spaceship from one planet to another.
        """
        link = self.find_planet_link(from_planet, to_planet, session)

        # Get the warp speed factor if present
        warp_factor = 1
        if link is not None:
            warp_factor = link.warper.speed_factor

        # Calculate the distance
        distance = self.distance_between_planets(from_planet, to_planet)
        self.moving_time = distance / (self.travel_speed_factor * warp_factor)
        self.destination = to_planet

        self.moving_time_left = self.moving_time
        self.space_port.settlement.planet.user.update()
        session.commit()

    def get_description(self) -> str:
        """
        Get the description of the spaceship
        """
        if len(self.attack_units) > 0:
            return f"Moving {len(self.attack_units)} attack units of type {self.attack_units[0].type}"
        elif self.rations > 0:
            return f"Moving {len(self.rations)} rations"
        elif self.building_materials > 0:
            return f"Moving {len(self.building_materials)} building materials"
        else:
            return "Moving empty handed"

    def get_return_time(self) -> float:
        """
        Gets the time left until return in seconds
        """
        if self.destination.planet_id == self.space_port.settlement.planet_id:
            return self.moving_time_left
        else:
            travel_distance = self.distance_between_planets(self.destination, self.space_port.settlement.planet)
            return self.moving_time + travel_distance / self.travel_speed_factor
