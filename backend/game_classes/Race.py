from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from database.database_access import Base, auto_session, default_factory

if TYPE_CHECKING:
    from backend.game_classes.Message import Message
    from backend.game_classes.User import User


class Race(Base):
    __tablename__ = "races"

    race_id: Mapped[UUID] = mapped_column(primary_key=True)
    race_name: Mapped[str] = mapped_column(unique=True)

    leader_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE", use_alter=True, name="races_leader_id_fkey"), unique=True)
    leader: Mapped["User"] = relationship(foreign_keys=[leader_id])
    members: Mapped[list["User"]] = relationship(back_populates="race", primaryjoin="users.c.race_id==races.c.race_id")

    messages: Mapped[list["Message"]] = relationship(back_populates="race")

    @default_factory(race_id=uuid1)
    def __init__(self, race_name: str, leader_id: UUID, race_id: UUID = None):
        """
        Initialize a Race object with an id, a name, a player id and an empty list of participants.
        """
        assert isinstance(race_id, UUID), "race_id must be of type 'UUID'"

        self.race_id: UUID = race_id
        self.race_name: str = race_name
        self.leader_id: UUID = leader_id

    @auto_session
    def store(self, session: Session = None) -> str | None:
        try:
            session.commit()
        except IntegrityError as DuplicateErr:
            print(type(DuplicateErr))  # the exception type
            print("Cannot Store Race. Race already exist. id :" + self.race_id.__str__() + " , ( race name :  " + self.race_name + " )" )
            return "Cannot Store Race. Race already exist. id :" + self.race_id.__str__() + " , ( race name :  " + self.race_name + " )"
        except Exception as err:
            print(type(err))  # the exception type
    @auto_session
    def add_participant(self, user: "User") -> None:
        """
        Add a user as a participant in the race.
        """
        self.members.append(user)

    @staticmethod
    @auto_session
    def load(race_name: str, session: Session = None) -> Race | None:
        return session.query(Race).filter_by(race_name=race_name).first()

    @auto_session
    def get_messages(self, session: Session = None) -> list["Message"]:
        return self.messages
