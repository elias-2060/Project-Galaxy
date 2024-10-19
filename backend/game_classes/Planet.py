from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid1

from sqlalchemy import CheckConstraint, Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from backend.game_classes.Settlement import Settlement
from backend.game_classes.Buildings import Barrack
from backend.game_classes.Combat.Attack import Attack
from database.database_access import Base, auto_session, default_factory
from backend.game_classes.Ships import Spaceship

from sqlalchemy.exc import IntegrityError

import random
import math

if TYPE_CHECKING:
    from backend.game_classes.User import User


class Planet(Base):
    __tablename__ = "planets"

    planet_id: Mapped[UUID] = mapped_column(primary_key=True)
    planet_x: Mapped[int]
    planet_y: Mapped[int]
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.user_id"))
    planet_name: Mapped[str] = mapped_column(unique=True)
    building_materials: Mapped[int]
    rations: Mapped[int]

    __table_args__ = (UniqueConstraint("planet_x", "planet_y"),)

    current_offence_attack: Mapped["Attack"] = relationship("Attack", foreign_keys=[Attack.attacking_planet_id],
                                                            back_populates="attacking_planet")
    current_defence_attack: Mapped["Attack"] = relationship("Attack", foreign_keys=[Attack.defending_planet_id],
                                                            back_populates="defending_planet")

    incoming_spaceships: Mapped[list[Spaceship]] = relationship(back_populates="destination")

    # All the settlements on the planet
    settlements: Mapped[list[Settlement]] = relationship()

    # The user that owns the planet:
    user: Mapped[Optional["User"]] = relationship(back_populates="planets")

    @default_factory(planet_id=uuid1)
    def __init__(
            self,
            user_id: UUID | None,
            planet_x: int,
            planet_y: int,
            name: str,
            building_materials: int = 800,
            rations: int = 800,
            *,
            planet_id: UUID = None,
    ):
        """
        Initialize a Planet object with an id, a list of settlements and resources.
        """
        super().__init__()
        assert isinstance(planet_id, UUID), "planet_id must be of type 'UUID'"

        self.user_id: UUID = user_id
        self.planet_x: int = planet_x
        self.planet_y: int = planet_y
        self.planet_name: str = name
        self.planet_id: UUID = planet_id
        self.building_materials: int = building_materials
        self.rations: int = rations

    @auto_session
    def store(self, session: Session = None) -> None:
        try:
            session.commit()
        except IntegrityError as DuplicateErr:
            print(type(DuplicateErr))  # the exception type
            print("Cannot Store Planet. Planet already exist. id :" + self.planet_id.__str__() + " , ( planet name :  "
                  + self.planet_name + " )")

        except Exception as err:
            print(type(err))  # the exception type

    @auto_session
    def add_settlement(self, settlement: Settlement) -> None:
        """
        Add a new settlement to the planet.
        """
        self.settlements.append(settlement)
        settlement.store()

    def add_building_materials(self, amount: int) -> None:
        self.building_materials += amount

    def add_rations(self, amount):
        self.rations += amount

    def update(self, update_time: float) -> None:
        """
        Log in to the world, this will call all functions to restore all the resources that have been made.
        """
        for settlement in self.settlements:
            settlement.update(update_time)

    @staticmethod
    @auto_session
    def get_by_pos(planet_x: int, planet_y: int, session: Session = None) -> Optional[Planet]:
        """
        Get the planet at the given position.

        :param int planet_x: The x position of the planet
        :param int planet_y: The y position of the planet
        :param Session session: The session to use
        :return: The planet at the given position or None if no planet exists at the given position
        """
        return session.query(Planet).filter_by(planet_x=planet_x, planet_y=planet_y).first()

    @staticmethod
    @auto_session
    def get_by_uuid(uuid: UUID, session: Session = None) -> Optional[Planet]:
        """
        Get the planet with the given UUID.

        :param UUID uuid: The UUID of the planet
        :param Session session: The session to use
        :return: The planet with the given UUID or None if no planet exists with the given UUID
        """
        return session.query(Planet).filter_by(planet_id=uuid).first()

    def get_attack_power(self):
        """
        Calculates the total attack power of the user
        """
        attack_power = sum(
            unit.attack_power
            for settlement in self.settlements
            for building in settlement.buildings
            if isinstance(building, Barrack)
            for unit in building.attack_units
            if not unit.in_training()
        )

        return attack_power

    @auto_session(auto_commit=True)
    def delete(self, session: Session = None):
        session.delete(self)

    @staticmethod
    def generateNewPlanetCoordinates(existing_planet_coordinates: list[tuple[int, int]]) -> tuple[int, int]:
        if len(existing_planet_coordinates) == 0:
            return 5000, 5000

        largest_x = 0
        largest_y = 0
        for coordinate in existing_planet_coordinates:
            if coordinate[0] > largest_x:
                largest_x = coordinate[0]
            if coordinate[1] > largest_y:
                largest_y = coordinate[1]

        largest_x = int(largest_x * 1.5)
        largest_y = int(largest_y * 1.5)

        while True:
            x = random.randint(0, largest_x)
            y = random.randint(0, largest_y)

            far_enough_away = False
            close_enough = False
            for coord in existing_planet_coordinates:
                distance = math.sqrt((coord[0] - x) ** 2 + (coord[1] - y) ** 2)
                if distance > 500:
                    far_enough_away = True
                if distance < 3000:
                    close_enough = True

            if far_enough_away and close_enough:
                return x, y

    @auto_session
    def active_settlements(self, session: Session = None) -> list[bool]:
        """
        Gets a list of all active settlements
        """
        # Make a list of size 3 (max 3 settlements per planet)
        active: list[bool] = [False, False, False]

        # Now loop over the settlements and put the bool on its index as True if it is active:

        settlement: Settlement
        for settlement in self.settlements:
            assert settlement.settlement_nr < 3, "Settlement nr too high"
            active[settlement.settlement_nr] = True

        # Return the result
        return active

    @staticmethod
    @auto_session
    def get_all_planets(session: Session = None) -> list:
        """
        Get all the planet coordinates
        """
        return session.query(Planet).all()

    @auto_session
    def get_all_other_planets(self, session: Session = None) -> list:
        return session.query(Planet).filter(Planet.planet_id != self.planet_id)

    @staticmethod
    def get_all_planets_coordinates(session: Session) -> list[tuple[int, int]]:
        """
        Get all the planet coordinates
        """
        planets: list[type[Planet]] = session.query(Planet).all()
        coordinates: list[tuple[int, int]] = []
        planets: list[Planet]
        for planet in planets:
            x: int = planet.planet_x
            y: int = planet.planet_y
            coordinates.append((x, y))
        return coordinates

    @auto_session(auto_commit=True)
    def attack(self, planet_to_attack_id: UUID, session: Session = None) -> Attack:
        """

        Makes an attack on another planet
        """
        assert self.current_offence_attack is None, "Attacking planet is already attacking someone else"
        assert self.current_defence_attack is None, "Attacking planet is already defending against someone else"

        # Get the planet
        planet = session.query(Planet).filter_by(planet_id=planet_to_attack_id).first()
        assert planet.user.user_id != self.user.user_id, "Planet is owned by the same user"
        assert planet.current_defence_attack is None, "Defending planet is already defending against someone else"
        assert planet.current_offence_attack is None, "Defending planet is already attacking someone else"

        # Make the attack
        attack = Attack(attacking_planet_id=self.planet_id, defending_planet_id=planet_to_attack_id)
        session.add(attack)

        return attack
