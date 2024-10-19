from typing import TYPE_CHECKING
from uuid import UUID, uuid1

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from database.database_access import Base, auto_session, default_factory

if TYPE_CHECKING:
    from backend.game_classes.Race import Race
    from backend.game_classes.User import User

MAX_MESSAGE_COUNT = 100
MAX_MESSAGE_LENGTH = 300


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[UUID] = mapped_column(primary_key=True)
    "Id of the message"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    "Id of the user that posted the message"

    race_id: Mapped[UUID] = mapped_column(ForeignKey("races.race_id", ondelete="CASCADE"))
    "Id of the race the message is posted in"

    position: Mapped[int]
    "Order of the message in the chat. Can contain gaps"

    message: Mapped[str]
    "The message"

    user: Mapped["User"] = relationship(back_populates="messages", foreign_keys=[user_id])
    "User that posted the message"

    race: Mapped["Race"] = relationship(back_populates="messages", foreign_keys=[race_id])
    "Race the message is posted in"

    __table_args__ = (UniqueConstraint("user_id", "race_id", "position"),)

    @default_factory(message_id=uuid1)
    def __init__(self, message: str, user_id: UUID, race_id: UUID, position: int, message_id: UUID = None):
        assert len(message) <= MAX_MESSAGE_LENGTH, f"Message cannot be longer than {MAX_MESSAGE_LENGTH} characters"

        self.message_id = message_id
        self.user_id = user_id
        self.race_id = race_id
        self.position = position
        self.message = message

    @staticmethod
    @auto_session
    def last_position(race_id: UUID, session: Session = None) -> int:
        """
        Get the position of the last message in the given race chat

        :race_id: Id of the race to get the last message from
        """
        last_message = session.query(Message).filter_by(race_id=race_id).order_by(Message.position.desc()).first()
        return last_message.position if last_message else 0
        

    @staticmethod
    @auto_session
    def load_by_id(message_id: UUID, session: Session = None) -> "Message":
        """
        Get a message fron the database based on it's id.

        :message_id: Id of the message to load
        """
        return session.query(Message).filter_by(message_id=message_id).one_or_none()

    @staticmethod
    @auto_session
    def load_range(race_id: UUID, start: int, end: int, session: Session = None) -> list["Message"]:
        """
        Get all messages between ``start`` and ``end`` in the chat of race ``race_id``.

        :race_id: Id of the race to get the messages from
        :start: Start position of the range
        :end: End position of the range
        """
        assert start <= end
        return (
            session.query(Message)
            .filter_by(race_id=race_id)
            .filter(Message.position.between(start, end))
            .limit(MAX_MESSAGE_COUNT)
            .all()
        )

    @staticmethod
    @auto_session
    def load_all(race_id: UUID, session: Session = None) -> list["Message"]:
        """
        Get a message from the database based on it's id.

        :race_id: Id of the race to get the messages from
        """
        return (
            session.query(Message)
            .filter_by(race_id=race_id)
            .order_by(Message.position.desc())
            .limit(MAX_MESSAGE_COUNT)
            .all()
        )

    @staticmethod
    @auto_session
    def load_last_messages(race_id: UUID, count: int = 50, session: Session = None) -> list["Message"]:
        """
        Get the last ``count`` messages from the chat of race ``race_id``.

        :race_id: Id of the race to get the messages from
        :count: Number of messages to get
        """
        return (
            session.query(Message)
            .filter_by(race_id=race_id)
            .order_by(Message.position.desc())
            .limit(min(count, MAX_MESSAGE_COUNT))
            .all()
        )

    @staticmethod
    @auto_session
    def count_range(race_id: UUID, start: int, end: int, session: Session = None) -> int:
        """
        Count the number of messages between ``start`` and ``end`` in the chat of race ``race_id``.

        :race_id: Id of the race to count the messages from
        :start: Start position of the range
        :end: End position of the range
        """
        assert start <= end
        return session.query(Message).filter_by(race_id=race_id).filter(Message.position.between(start, end)).count()

    @staticmethod
    @auto_session
    def count_all(race_id: UUID, session: Session = None) -> int:
        """
        Count the number of messages in the chat of race ``race_id``.

        :race_id: Id of the race to count the messages from
        """
        return session.query(Message).filter_by(race_id=race_id).count()
