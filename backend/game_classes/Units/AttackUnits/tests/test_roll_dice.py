import pytest
from backend.game_classes.Units.AttackUnits.tests import attack_unit_default_setup
from backend.game_classes import AttackUnit


@pytest.mark.usefixtures("clear-db")
def test_roll_dice(attack_unit_default_setup):
    """
    Test function for the roll dice function for attack units
    """
    # We get the items from the default setup
    user, planet, settlement, barrack, unit_list, session = attack_unit_default_setup

    # We roll each unit from level 1 to 3
    for i in range(1, 4):
        unit: AttackUnit

        # We loop over each of the units from the unit list
        for unit in unit_list:
            unit.level = i
            session.commit()

            # Roll 20 times per unit, per level
            for j in range(20):
                result = unit.roll_dice()
                assert result >= 0
                assert result <= unit.attack_power
