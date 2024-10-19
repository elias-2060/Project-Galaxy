from __future__ import annotations

import json
from datetime import datetime, timedelta
from json.encoder import JSONEncoder
from typing import TYPE_CHECKING
from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from backend.game_classes.Achievement import Achievement
from backend.game_classes.Planet import Planet
from backend.game_classes.Race import Race
from database.database_access import Base, auto_session, default_factory

if TYPE_CHECKING:
    from backend.game_classes.Message import Message
    from backend.game_classes.Units.Unit import Unit


class UserEncoder(JSONEncoder):
    def default(self, user: User):
        if not isinstance(user, User):
            return super().default(user)
        return {
            "user_id": str(user.user_id),
            "user_name": user.user_name,
            # "race_id": None if user.race is None else str(user.race.race_id),
            # "race_name": None if user.race is None else user.race.race_name,
        }


class User(Base):
    """
    Class that is used to store users in the database and retrieve them
    """

    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    last_update: Mapped[datetime]

    # All the planets the user owns
    planets: Mapped[list[Planet]] = relationship()

    # All achievements the user has
    achievements: Mapped[list[Achievement]] = relationship(secondary="has_achievement", back_populates="users")

    # The race the user is in:

    race_id: Mapped[UUID | None] = mapped_column(ForeignKey("races.race_id", ondelete="SET NULL", use_alter=True, name="users_race_id_fkey"))
    race: Mapped[Race | None] = relationship(back_populates="members", foreign_keys=[race_id])

    messages: Mapped[list["Message"]] = relationship(back_populates="user")

    @default_factory(user_id=uuid1)
    def __init__(self, user_name: str, user_password: str, user_id: UUID = None):
        assert isinstance(user_id, UUID), "user_id must be of type 'UUID'"

        self.user_id: UUID = user_id
        self.user_name: str = user_name
        self.password: str = user_password
        assert self.check_password(), "Password has to have a capital letter, a number and a length greater than 5"

        self.race_id: UUID | None = None
        self.achievements: list[Achievement] = []
        self.units: list[Unit] = []
        self.last_update: datetime = datetime.now()

    def __repr__(self):
        return f"{self.user_id}, {self.user_name}, {self.password}"
    
    @property
    def sorted_planets(self) -> list[Planet]:
        return sorted(self.planets, key=lambda planet: planet.planet_name)

    def check_password(self):
        """
        Checks if the password is strong enough.
        """
        capital_in_password: bool = any(char.isupper() for char in self.password)
        number_in_password: bool = any(char.isdigit() for char in self.password)
        len_greater_than_5: bool = bool(len(self.password) > 5)
        return capital_in_password and number_in_password and len_greater_than_5

    @auto_session
    def store(self, session: Session = None) -> str | None:
        try:
            session.commit()
        except IntegrityError as DuplicateErr:
            print(type(DuplicateErr))  # the exception type
            print("Cannot Store User. User already exist. id :" + self.user_id.__str__() + " , ( user name :  " + self.user_name + " )" )
            return "Cannot Store User. User already exist. id :" + self.user_id.__str__() + " , ( user name :  " + self.user_name + " )"
        except Exception as err:
            print(type(err))  # the exception type
            #print(err.args)  # arguments stored in .args
            #print(err)


    @auto_session
    def add_planet(self, planet: Planet) -> None:
        self.planets.append(planet)

    @auto_session
    def leave_race(self, session: Session = None) -> None:
        """
        Leave the current race.
        """
        if self.race.leader_id == self.user_id:
            session.query(Race).filter(Race.leader_id == self.user_id).delete()
        self.race = None

    @auto_session
    def join_race(self, race: Race) -> None:
        """
        Join an existing race.
        """
        self.race = race

    @auto_session
    def add_achievement(self, achievement: Achievement) -> None:
        """
        Add an achievement to the player's list of achievements.
        """
        self.achievements.append(achievement)

    @auto_session
    def update(self, session=Session) -> None:
        """
        Update all planets owned by the player.
        """
        update_time_delta: timedelta = datetime.now() - self.last_update
        update_time: float = update_time_delta.total_seconds()

        for planet in self.planets:
            planet.update(update_time)

        self.last_update = datetime.now()

        session.commit()

    @staticmethod
    @auto_session
    def load_by_name(user_name: str, session: Session = None) -> User | None:
        """
        Load a user with the given name from the database.


        :param str user_name: Name of the user to load
        :param session: Session to use to fetch the user (optional)
        """
        assert isinstance(session, Session), "session must be of type 'Session'"

        return session.query(User).filter_by(user_name=user_name).first()

    @auto_session
    def json(self) -> str:
        """
        Serialize the user into a dictionary.
        """
        return json.dumps(self, cls=UserEncoder)

    @auto_session
    def load_by_id(user_id: UUID, session: Session = None) -> User | None:
        """
        Load a user with the given id from the database.

        :param str user_id: Id of the user to load
        :param session: Session to use to fetch the user (optional)
        """
        assert isinstance(session, Session), "session must be of type 'Session'"

        return session.query(User).filter_by(user_id=user_id).first()
