from __future__ import annotations

from sqlalchemy import Sequence
from sqlalchemy.orm import Session, Mapped, mapped_column

from backend.game_classes.User import User
from backend.game_classes.Race import Race
from backend.game_classes.Planet import Planet
from backend.game_classes.PlanetLink import PlanetLink
from backend.game_classes.Combat.Attack import Attack
from backend.game_classes.Settlement import Settlement
from backend.game_classes.Ships.Spaceship import Spaceship
from backend.game_classes.Buildings import Building, Farm, Mine, Barrack, TownHall, Warper, Spaceport
from backend.game_classes.Ships.ship import Ship
from backend.game_classes.Ships.colony_ship import ColonyShip
from backend.game_classes.Units import Unit, SpaceMarine, AttackUnit, SpaceCommando, SpaceDrone
from backend.game_classes.Achievement import Achievement
from database.database_access import Base, auto_session


class SetupState(Base):
    __tablename__ = "setup_state"

    _key: Mapped[int] = mapped_column(Sequence("setup_state_id_seq"), primary_key=True)
    "Primary key. Unused."

    achievements_created: Mapped[bool]
    "If true, all achievements have been created."

    def __init__(self, achievements_created: bool = False) -> None:
        self.achievements_created = achievements_created

    @auto_session
    def load(session: Session = None) -> SetupState | None:
        return session.query(SetupState).first()
