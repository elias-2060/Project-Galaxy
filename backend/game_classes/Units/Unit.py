from uuid import UUID, uuid1

from sqlalchemy.orm import Mapped, Session, mapped_column

from database.database_access import Base, auto_session, default_factory


class Unit(Base):
    __tablename__ = "units"

    unit_id: Mapped[UUID] = mapped_column(primary_key=True)

    level: Mapped[int]

    # For polymorphism
    type: Mapped[str]

    __mapper_args__ = {"polymorphic_identity": "units",
                       "polymorphic_on": "type", }

    @default_factory(unit_id=uuid1)
    def __init__(self, level: int, unit_id: UUID = None) -> None:
        """
        Initialize a Unit object with a name.
        """
        assert isinstance(unit_id, UUID), "unit_id must be of type 'UUID'"

        self.unit_id: UUID = unit_id
        self.level: int = level

    @auto_session
    def store(self, session: Session = None) -> None:
        session.commit()

    @property
    def type_string(self) -> str:
        res = self.type
        parts = res.split("_")
        res = ""
        for part in parts:
            res += part.capitalize() + "-"
        res = res[:-1]
        return res
