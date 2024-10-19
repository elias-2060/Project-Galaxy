from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import Column, ForeignKey, Table, delete
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
import tomllib

from sqlalchemy.exc import IntegrityError

from database.database_access import Base, auto_session, default_factory

if TYPE_CHECKING:
    from backend.game_classes.User import User

# Table for has_achievement relationship between achievement and user
has_achievement = Table(
    "has_achievement",
    Base.metadata,
    Column("user_id", ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True),
    Column("achievement_id", ForeignKey("achievements.achievement_id", ondelete="CASCADE"), primary_key=True),
)


class Achievement(Base):
    __tablename__ = "achievements"

    achievement_id: Mapped[UUID] = mapped_column(primary_key=True)
    "ID of the achievement"

    achievement_name: Mapped[str] = mapped_column(unique=True)
    "Name of the achievement"

    achievement_description: Mapped[str]
    "Description of the achievement"

    reward: Mapped[int]
    "Reward for the achievement"

    requirement: Mapped[str]
    "Requirement for the achievement"

    # All the users that have the achievement:
    users: Mapped[list["User"]] = relationship(secondary="has_achievement", back_populates="achievements")
    "All the users that have the achievement"

    @default_factory(achievement_id=uuid1)
    def __init__(self, achievement_name: str, achievement_description: str, reward: int, requirement: str, achievement_id: UUID = None):
        """
        Initialize an Achievement object with a name and description.
        """
        super().__init__()
        assert isinstance(achievement_id, UUID), "achievement_id must be of type 'UUID'"

        self.achievement_name: str = achievement_name
        self.achievement_id: UUID = achievement_id
        self.achievement_description = achievement_description
        self.reward = reward
        self.requirement = requirement

    @auto_session
    def store(self, session: Session = None) -> None:
        try:
            session.commit()
        except IntegrityError as DuplicateErr:
            print(type(DuplicateErr))  # the exception type
            print(
                "Cannot Store Achievement. Achievement already exist. id :"
                + self.achievement_id.__str__()
                + " , ( achievement name :  "
                + self.achievement_name
                + " )"
            )

        except Exception as err:
            print(type(err))  # the exception type

    @staticmethod
    @auto_session
    def populate(session: Session = None) -> None:
        with open("backend/game_classes/achievements.toml", "rb") as f:
            achievements: list = tomllib.load(f)["achievement"]
            existing: list[Achievement] = session.query(Achievement).all()

            # delete all existing achievements
            [session.delete(a) for a in existing]
            session.flush()

            # create new achievements
            for achievement in achievements:
                session.add(
                    Achievement(
                        achievement["name"],
                        achievement["description"],
                        achievement["reward"],
                        achievement["requirement"],
                    )
                )
    
    @staticmethod
    @auto_session
    def load(achievement_id: UUID, session: Session = None) -> Achievement | None:
        return session.query(Achievement).filter(Achievement.achievement_id == achievement_id).one_or_none()
