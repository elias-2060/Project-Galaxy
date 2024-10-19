from functools import wraps
import tomllib as toml
from typing import Any


class PropertyError(Exception):
    pass


properties: dict[str, dict[str, Any]] = {}

configs = {
    "building": "backend/game_classes/Buildings/building-properties.toml",
    "unit": "backend/game_classes/Units/unit-properties.toml",
    "spaceship": "backend/game_classes/Ships/spaceship-properties.toml",
}


def load_properties() -> None:
    """
    Load building properties from file.
    """
    for type, file in configs.items():
        with open(file, "rb") as f:
            global properties
            properties[type] = toml.load(f)


load_properties()


def get_property(type: str, *args, properties=properties) -> Any:
    """
    Get a property from the properties' config.

    Example
    >>> # get attribute farm.level.1.build_cost
    >>> get_property("farm", "level", 1, "build_cost")
    """

    res: Any = properties.get(type)
    if res is None:
        raise PropertyError(f"Property '{type}' not found")

    args_done: list[str | int] = [type]
    for arg in args:
        if isinstance(res, (list | tuple)):
            try:
                res = res[arg]
            except KeyError:
                raise PropertyError(f"Element '{arg}' not found in building '{'.'.join(args_done)}'")
        elif isinstance(res, dict):
            res = res.get(arg)
            if res is None:
                raise PropertyError(f"Property '{arg}' not found in building '{'.'.join(args_done)}'")
        else:
            raise PropertyError(f"Property '{'.'.join(args_done)}' is final and does not have sub-property '{arg}'")

        args_done.append(arg)

    return res


def gets_property(*props):
    def wrapper(func) -> Any:
        @wraps(func)
        def inner(*args, **kwargs):
            prop = get_property(*props)
            if prop is None:
                raise PropertyError(f"No '{type}' properties loaded")
            return func(*args, **kwargs, properties=prop)

        return inner

    return wrapper


@gets_property("building")
def get_building_property(building: str, *args, properties) -> Any:
    """Get building properties"""
    return get_property(building, *args, properties=properties)


@gets_property("unit")
def get_unit_property(unit: str, *args, properties) -> Any:
    """Get unit properties"""
    return get_property(unit, *args, properties=properties)

@gets_property("spaceship")
def get_spaceship_property(spaceship: str, *args, properties) -> Any:
    """Get spaceship properties"""
    return get_property(spaceship, *args, properties=properties)