from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import ForeignKey, UUID as sqlUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship


from database.database_access import Base, auto_session, default_factory

if TYPE_CHECKING:
    from backend.game_classes import User
    from backend.game_classes.Planet import Planet
    from backend.game_classes.Buildings.Spaceport import Spaceport


class ShipLocation(Base):
    """
    Location of a ship.
    """

    __tablename__ = "ship_locations"

    ship_id: Mapped[UUID] = mapped_column(
        sqlUUID,
        ForeignKey("ships.ship_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    "Id of the ship the location belongs to"

    type: Mapped[str]
    "Type of location"

    ship: Mapped["Ship"] = relationship(
        back_populates="location",
        foreign_keys=ship_id,
        lazy="selectin",
    )
    "Ship the location belongs to"

    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_abstract": True}

    def __init__(self, ship_id: UUID):
        self.ship_id = ship_id

    @property
    def is_moving(self) -> bool:
        """Whether the ship is moving or not."""
        return False


class OrbitLocation(ShipLocation):
    """
    Location for ships at a planet.
    """

    planet_id: Mapped[UUID] = mapped_column(
        ForeignKey("planets.planet_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
        use_existing_column=True,
    )
    "Id of the planet the ship is orbiting"

    planet: Mapped["Planet"] = relationship(foreign_keys=planet_id)
    "Planet the ship is orbiting"

    __mapper_args__ = {"polymorphic_identity": "orbit"}

    def __init__(self, ship_id: UUID, planet_id: UUID):
        assert isinstance(ship_id, UUID), f"building_id must be of type 'UUID' but is of type {type(ship_id).__name__}"

        super().__init__(ship_id)
        self.planet_id = planet_id


class WarpLocation(ShipLocation):
    """
    Location for ships in warp.
    """

    planet_id: Mapped[UUID] = mapped_column(
        ForeignKey("planets.planet_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
        use_existing_column=True,
    )
    "Id of the planet the ship coming from"

    planet_to_id: Mapped[UUID] = mapped_column(
        ForeignKey("planets.planet_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    "Id of the planet the ship is going to"

    departure_time: Mapped[datetime] = mapped_column(use_existing_column=True, nullable=True)
    "Time the ship departed"

    planet_from: Mapped["Planet"] = relationship(foreign_keys=planet_id)
    "Planet the ship is coming from"

    planet_to: Mapped["Planet"] = relationship(foreign_keys=planet_to_id)
    "Planet the ship is going to"

    __mapper_args__ = {"polymorphic_identity": "warp"}

    @default_factory(departure_time=datetime.now)
    def __init__(self, ship_id: UUID, planet_id: UUID, planet_to_id: UUID, departure_time: datetime = None):
        assert isinstance(ship_id, UUID), f"building_id must be of type 'UUID' but is of type {type(ship_id).__name__}"

        super().__init__(ship_id)
        self.planet_id = planet_id
        self.planet_to_id = planet_to_id
        self.departure_time = departure_time

    @property
    def is_moving(self) -> bool:
        return True

class LandedLocation(ShipLocation):
    """
    Location for ships that are landed.
    """

    __mapper_args__ = {"polymorphic_identity": "landed"}

    spaceport_id: Mapped[UUID] = mapped_column(
        ForeignKey("spaceports.building_id"),
        nullable=True,
        use_existing_column=True,
    )
    "Id of the spaceport the ship is landed at"

    spaceport: Mapped["Spaceport"] = relationship()
    "Spaceport the ship is landed at"

    __mapper_args__ = {"polymorphic_identity": "landed"}

    def __init__(self, ship_id: UUID, spaceport_id: UUID):
        assert isinstance(ship_id, UUID), f"building_id must be of type 'UUID' but is of type {type(ship_id).__name__}"

        super().__init__(ship_id)
        self.spaceport_id = spaceport_id


class LandingLocation(ShipLocation):
    """
    Location for ships landing.
    """

    spaceport_id: Mapped[UUID] = mapped_column(
        ForeignKey("spaceports.building_id"),
        nullable=True,
        use_existing_column=True,
    )
    "Id of the spaceport the ship is landing at"

    spaceport: Mapped["Spaceport"] = relationship()
    "Spaceport the ship is landing at"

    departure_time: Mapped[datetime] = mapped_column(use_existing_column=True, nullable=True)
    "Time the ship left orbit"

    __mapper_args__ = {"polymorphic_identity": "landing"}

    @default_factory(departure_time=datetime.now)
    def __init__(self, ship_id: UUID, spaceport_id: UUID, departure_time: datetime = None):
        assert isinstance(ship_id, UUID), f"building_id must be of type 'UUID' but is of type {type(ship_id).__name__}"

        super().__init__(ship_id)
        self.spaceport_id = spaceport_id
        self.departure_time = departure_time

    @property
    def is_moving(self) -> bool:
        return True


class TakeoffLocation(ShipLocation):
    """
    Location for ships taking off.
    """

    spaceport_id: Mapped[UUID] = mapped_column(
        ForeignKey("spaceports.building_id"),
        nullable=True,
        use_existing_column=True,
    )
    "Id of the spaceport the ship is taking off at"

    spaceport: Mapped["Spaceport"] = relationship()
    "Spaceport the ship is taking off at"

    departure_time: Mapped[datetime] = mapped_column(use_existing_column=True, nullable=True)
    "Time the ship left the spaceport"

    __mapper_args__ = {"polymorphic_identity": "takeoff"}

    @default_factory(departure_time=datetime.now)
    def __init__(self, ship_id: UUID, spaceport_id: UUID, departure_time: datetime = None):
        assert isinstance(ship_id, UUID), f"building_id must be of type 'UUID' but is of type {type(ship_id).__name__}"

        super().__init__(ship_id)
        self.spaceport_id = spaceport_id
        self.departure_time = departure_time

    @property
    def is_moving(self) -> bool:
        return True


class Ship(Base):
    """
    Base interstellar ship.
    All ships have an owner and a location.
    """

    __tablename__ = "ships"

    ship_id: Mapped[UUID] = mapped_column(primary_key=True)
    "Id of the ship."
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id", onupdate="CASCADE", ondelete="CASCADE"))
    "Id of the player owning the ship."

    owner: Mapped["User"] = relationship()
    "User owning the ship."

    location: Mapped[ShipLocation] = relationship(
        primaryjoin=ship_id == ShipLocation.ship_id,
        foreign_keys=ship_id,
        lazy="selectin",
    )
    "Location the ship is at."

    type: Mapped[str]  # column to store building type in, for ORM inheritance
    "Type of ship. Needed for polymorphism."

    __mapper_args__ = {
        "polymorphic_identity": "ship",
        "polymorphic_on": "type",
    }

    @default_factory(ship_id=uuid1)
    def __init__(self, owner_id: UUID, ship_id: UUID = None):
        assert isinstance(ship_id, UUID), f"building_id must be of type 'UUID' but is of type {type(ship_id).__name__}"

        self.ship_id = ship_id
        self.owner_id = owner_id

    @auto_session
    def update(self, force_arrival: bool = None, session: Session = None):
        """
        Update the ship.
        Checks if the movement is done.

        :param force_finish: If true forces arrival to trigger without checking the duration.
        """
        # if arrived, set update location
        # only updates are for moving, so non-moving locations are skipped
        match self.location:
            case WarpLocation():  # handle movement for in warp
                # TODO remove placeholder time
                if datetime.now() - self.location.departure_time < timedelta(seconds=5) or force_arrival:
                    self.swap_location(OrbitLocation(self.ship_id, self.location.planet_to_id))
            case TakeoffLocation():  # handle movement for taking of
                # TODO remove placeholder time
                if datetime.now() - self.location.departure_time < timedelta(seconds=5) or force_arrival:
                    self.swap_location(OrbitLocation(self.ship_id, self.location.spaceport.settlement.planet_id))
            case LandingLocation():  # handle movement for landing
                # TODO remove placeholder time
                if datetime.now() - self.location.departure_time < timedelta(seconds=5) or force_arrival:
                    self.swap_location(LandedLocation(self.ship_id, self.location.spaceport_id))

    @auto_session
    def move_to(self, destination: "Planet") -> str | None:
        """
        Move the ship towards the destination.

        :param destination: Planet to move towards.
        :return: None if the move was successful or an error message.
        """
        if self.is_moving():
            return "Ship is already moving."

        if not isinstance(self.location, OrbitLocation):
            return "Ship must be in orbit to warp to another planet."

        self.swap_location(WarpLocation(self.ship_id, self.location.planet_id, destination.planet_id))

    @auto_session
    def take_off(self, session: Session = None) -> str | None:
        """
        Take off from the spaceport the ship is landed at and return to orbit.

        :return: None if the takeoff was sucessful or an error message.
        """
        assert self.location is not None, "TODO"  # TODO

        if self.is_moving():
            return "Ship is already moving."

        if not isinstance(self.location, LandedLocation):
            return "Ship isn't landed."

        self.swap_location(TakeoffLocation(self.ship_id, self.location.spaceport_id))

    @auto_session
    def land(self, spaceport: "Spaceport", session: Session = None) -> str | None:
        """
        Land at the specified spaceport.

        :param spaceport: The spaceport to land at.
        :return: None if the landing was sucessful or an error message.
        """
        # TODO check spaceport has enough space
        assert self.location is not None, "TODO"  # TODO

        if self.is_moving():
            return "Ship is already moving."

        if not isinstance(self.location, OrbitLocation) or self.location.planet_id != spaceport.settlement.planet_id:
            return f"Ship can only land at settlment '{spaceport.settlement_id}' of planet '{spaceport.settlement.planet.planet_name}' while in orbit around the planet."

        self.swap_location(LandingLocation(self.ship_id, spaceport.building_id))

    @auto_session
    def is_moving(self, session: Session = None) -> bool:
        """Check if the ship is moving."""
        assert self.location is not None, "TODO"  # TODO

        return self.location.is_moving

    @auto_session
    def swap_location(self, loc: ShipLocation, session: Session = None):
        """
        Swap the current location for the one provided.

        :param loc: The new location.
        """
        session.delete(self.location)
        session.flush()
        self.location = loc
        session.flush()
