from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID
from enum import Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from backend.game_classes.Units.AttackUnits import AttackUnit
from backend.game_classes.Buildings.Barrack import Barrack
from database.database_access import Base, auto_session

if TYPE_CHECKING:
    from backend.game_classes.Planet import Planet


class GameResult(Enum):
    WIN = "Win"
    LOSE = "Lose"
    DRAW = "Draw"


class Attack(Base):
    __tablename__ = "attacks"

    attacking_planet_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "planets.planet_id",
            ondelete="CASCADE"
        ),
        primary_key=True,
        unique=True
    )
    defending_planet_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "planets.planet_id",
            ondelete="CASCADE"
        ),
        primary_key=True,
        unique=True
    )

    # noinspection PyTypeChecker
    attacking_planet: Mapped["Planet"] = relationship("Planet", foreign_keys=attacking_planet_id,
                                                      back_populates="current_offence_attack")
    # noinspection PyTypeChecker
    defending_planet: Mapped["Planet"] = relationship("Planet", foreign_keys=defending_planet_id,
                                                      back_populates="current_defence_attack")

    _selected_attack_unit_id: Mapped[UUID] = mapped_column(ForeignKey("attack_units.unit_id",
                                                                      ), nullable=True)
    _selected_defence_unit_id: Mapped[UUID] = mapped_column(ForeignKey("attack_units.unit_id",
                                                                       ), nullable=True)

    @auto_session
    def __init__(self, attacking_planet_id: UUID, defending_planet_id: UUID) -> None:
        """
        Initialize an attack, with the 2 planet-id's as primary keys.
        """
        super().__init__()
        self.attacking_planet_id: UUID = attacking_planet_id
        self.defending_planet_id: UUID = defending_planet_id

        self._selected_attack_unit_id: UUID | None = None
        self._selected_defence_unit_id: UUID | None = None

    @auto_session
    def get_attacking_units(self) -> list[AttackUnit]:
        """
        Gets the attacking units
        """
        attack_units = [
            unit
            for settlement in self.attacking_planet.settlements
            for building in settlement.buildings
            if isinstance(building, Barrack)
            for unit in building.attack_units
            if not unit.in_training()
        ]
        attack_units = sorted(attack_units, key=lambda x: x.attack_power, reverse=True)
        return attack_units

    @auto_session
    def get_defending_units(self) -> list[AttackUnit]:
        """
        Gets the defending units
        """
        defending_units = [
            unit
            for settlement in self.defending_planet.settlements
            for building in settlement.buildings
            if isinstance(building, Barrack)
            for unit in building.attack_units
            if not unit.in_training()
        ]
        defending_units = sorted(defending_units, key=lambda x: x.attack_power, reverse=True)
        return defending_units

    @auto_session
    def select_unit_attacking(self, unit_id: UUID | None) -> None:
        """
        Selects the unit the attacker is going to use.

        Use None as input to deselect.
        """
        self._selected_attack_unit_id: UUID = unit_id

    @auto_session
    def select_unit_defending(self, unit_id: UUID | None) -> None:
        """
        Selects the unit the attacker is going to use.

        Use None as input to deselect.
        """
        self._selected_defence_unit_id: UUID = unit_id

    @auto_session
    def play_round(
            self,
            auto_select_attack: bool = False,
            auto_select_defence: bool = True,
            auto_delete: bool = True,
            session: Session = None
    ) -> dict:
        """
        Plays one round of the game.

        auto_select_attack: automatically selects an attack_unit
        auto_select_defence: automatically selects a defence_unit
        auto_delete: automatically deletes the attack when the battle is won, lost or drawn

        """
        attack_units = self.get_attacking_units()
        defence_units = self.get_defending_units()

        # If auto selecting attack is True, automatically select an attack unit (first of the list)
        if auto_select_attack:
            self.select_unit_attacking(attack_units[0].unit_id)
            session.commit()

        # If auto selecting defense is True, automatically select a defense unit (first of the list)
        if auto_select_defence:
            self.select_unit_defending(defence_units[0].unit_id)
            session.commit()

        assert self._selected_attack_unit_id is not None, "No attack unit selected"
        assert self._selected_defence_unit_id is not None, "No defence unit selected"

        # Get the attacking unit and defending unit
        attacking_unit: AttackUnit | None = None
        defending_unit: AttackUnit | None = None
        for unit in attack_units:
            if unit.unit_id == self._selected_attack_unit_id:
                attacking_unit = unit
                break
        for unit in defence_units:
            if unit.unit_id == self._selected_defence_unit_id:
                defending_unit = unit
                break
        assert attacking_unit is not None, "Attacking unit not in unit list of attacker"
        assert defending_unit is not None, "Defence unit not in unit list of defender"

        # Get the dice roll result of both
        attack_roll: int = attacking_unit.roll_dice()
        defence_roll: int = defending_unit.roll_dice()

        # Get the result of who wins / loses:
        attack_survive, defence_survive, passive_attack, passive_defense = self.get_win(
            attack_roll=attack_roll,
            defence_roll=defence_roll,
            attacking_unit=attacking_unit,
            defending_unit=defending_unit
        )

        # If a unit dies, we remove it
        if not attack_survive:
            self._selected_attack_unit_id: None = None
            session.delete(attacking_unit)
            session.commit()
        if not defence_survive:
            self._selected_defence_unit_id: None = None
            session.delete(defending_unit)
            session.commit()

        # Check if someone has won the game
        attack_units = self.get_attacking_units()
        defence_units = self.get_defending_units()
        combat_result = ""
        if len(attack_units) == 0 and len(defence_units) == 0:
            if auto_delete:
                self.lose()
            combat_result = "Lose"
        elif len(attack_units) == 0:
            if auto_delete:
                self.lose()
            combat_result = "Lose"
        elif len(defence_units) == 0:
            if auto_delete:
                self.win()
            combat_result = "Win"
        return {
            "attack_roll": attack_roll,
            "defence_roll": defence_roll,
            "attack_survive": attack_survive,
            "defence_survive": defence_survive,
            "passive_attack": passive_attack,
            "passive_defense": passive_defense,
            "combat_result": combat_result
        }

    @auto_session
    def get_win(self, attack_roll: int, defence_roll: int, attacking_unit: AttackUnit, defending_unit: AttackUnit) -> (
            tuple[bool, bool, bool, bool]):
        """
        Calculates which units die, and which win

        Return value 1: bool whether the attack unit lives
        Return value 2: bool whether the defense unit lives
        Return value 3: whether the user passive was used
        Return value 4: whether the defending unit passive was used
        """
        # Get the roll result from the unit with passives included
        result_attack1, result_defense1, passive_attack = attacking_unit.get_round_result(attack_roll, defence_roll)
        result_defense2, result_attack2, passive_defence = defending_unit.get_round_result(defence_roll, attack_roll)

        # Calculate the new win values
        result_attack = result_attack1 and result_attack2
        result_defense = result_defense1 and result_defense2

        return result_attack, result_defense, passive_attack, passive_defence

    @auto_session
    def lose(self, session: Session) -> None:
        """
        When losing, you lose 10% of your resources and the attack is deleted
        """
        # Delete 10% of the resources
        self.attacking_planet.rations = int(self.attacking_planet.rations * 9 / 10)
        self.attacking_planet.building_materials = int(self.attacking_planet.building_materials * 9 / 10)
        session.commit()

        # Delete the attack
        session.delete(self)

    @auto_session
    def win(self, session: Session = None) -> None:
        """
        When winning, 25% of the resources from the defending planet are moved to the attacking planet
        """
        # Get the resources
        rations_gained: int = int(self.defending_planet.rations * 1 / 4)
        building_mats_gained: int = int(self.defending_planet.building_materials * 1 / 4)

        # Add them to the attacking planet
        self.attacking_planet.rations += rations_gained
        self.attacking_planet.building_materials += building_mats_gained

        # Remove them from the defending planet
        self.defending_planet.rations -= rations_gained
        self.defending_planet.building_materials -= building_mats_gained

        # Delete the attack
        session.delete(self)

    @auto_session
    def get_selected_attack_unit(self, session: Session = None) -> AttackUnit | None:
        """
        Getter for the selected attack unit
        """
        # If it is None, just return None
        if self._selected_attack_unit_id is None:
            return None

        # Else, get it from the database
        return session.query(AttackUnit).filter_by(unit_id=self._selected_attack_unit_id).first()

    @auto_session
    def get_selected_defence_unit(self, session: Session = None) -> AttackUnit | None:
        """
        Getter for the selected attack unit
        """
        # If it is None, just return None
        if self._selected_defence_unit_id is None:
            return None

        # Else, get it from the database
        return session.query(AttackUnit).filter_by(unit_id=self._selected_defence_unit_id).first()

    @auto_session
    def set_selected_attack_unit(self, unit_id: UUID, session: Session = None) -> None:
        """
        Setter for the selected attack
        """
        # Get the unit
        unit: Any = session.query(AttackUnit).filter_by(unit_id=unit_id).first()

        # Some checks
        assert unit.barrack.settlement.planet.planet_id == self.attacking_planet_id, ("Attack unit not from attacking "
                                                                                      "planet")
        assert not unit.in_training(), "Unit is still in training"

        # Change the value
        self._selected_attack_unit_id: UUID = unit.unit_id
        assert self.get_selected_attack_unit() == unit

    @auto_session
    def set_selected_defence_unit(self, unit_id: UUID, session: Session = None) -> None:
        """
        Setter for the selected defense unit
        """
        # Get the unit
        unit: Any = session.query(AttackUnit).filter_by(unit_id=unit_id).first()

        # Some checks
        assert unit.barrack.settlement.planet.planet_id == self.defending_planet_id, ("Attack unit not from attacking "
                                                                                      "planet")
        assert not unit.in_training(), "Unit is still in training"

        # Change the value
        self._selected_defence_unit_id: UUID = unit.unit_id
        assert self.get_selected_defence_unit() == unit
