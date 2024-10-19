import pytest
from backend.game_classes.Units.AttackUnits.tests import attack_unit_default_setup
from backend.game_classes import AttackUnit
from backend.game_classes.properties import get_unit_property


@pytest.mark.usefixtures("clear-db")
def test_attack_unit_getters(attack_unit_default_setup):
    """
    Test function for the getters from the attack units
    """
    # We get the items from the default setup
    user, planet, settlement, barrack, unit_list, session = attack_unit_default_setup

    # We check all the values from levels 1 to 3
    for i in range(1, 4):
        unit: AttackUnit
        for unit in unit_list:
            unit.level = i
            session.commit()
            assert unit.attack_power == get_unit_property(unit.__property_name__, "level", str(i), "attack_power")
            assert unit.training_time == get_unit_property(unit.__property_name__, "level", str(i), "training_time")
            assert unit.rations_per_hour == get_unit_property(unit.__property_name__, "level", str(i), "rations_per_hour")
            assert unit.training_cost == get_unit_property(unit.__property_name__, "level", str(i), "training_cost")
            assert unit.upgrade_cost == get_unit_property(unit.__property_name__, "level", str(i), "upgrade_cost")