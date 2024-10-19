from http import HTTPStatus

from backend.api.building import api
from backend.api.building.building import building_model, building_parser
from backend.game_classes import Barrack, Planet, Settlement, User, AttackUnit
from database.database_access import DefaultSession
from flask import request, session
from flask_restx import Resource, fields, inputs, marshal

unit_model = api.model(
    "UnitInfo",
    {
        "unit_id": fields.String(description="ID of the unit", required=True),
        "type": fields.String(description="Type of the unit", required=True),
        "level": fields.Integer(description="Level of the unit", required=True),
    },
)

disabled_units = api.model(
    "DisabledUnits",
    {
        "space_marine_disabled": fields.Boolean(
            description="Whether SpaceMarines are disabled",
            required=True,
            attribute=lambda b: b.get_disabled_units()["SpaceMarine"],
        ),
        "space_commando_disabled": fields.Boolean(
            description="Whether SpaceCommandos are disabled",
            required=True,
            attribute=lambda b: b.get_disabled_units()["SpaceCommando"],
        ),
        "space_drone_disabled": fields.Boolean(
            description="Whether SpaceDrones are disabled",
            required=True,
            attribute=lambda b: b.get_disabled_units()["SpaceDrone"],
        ),
    }
)

unit_costs = api.model(
    "UnitCosts",
    {
        "space_marine_cost": fields.Integer(
            description="Training cost of a SpaceMarine",
            required=True,
            attribute=lambda b: AttackUnit.get_training_cost_static("space_marine", b.space_marine_level),
        ),
        "space_commando_cost": fields.Integer(
            description="Training cost of a SpaceCommando",
            required=True,
            attribute=lambda b: AttackUnit.get_training_cost_static("space_commando", b.space_commando_level),
        ),
        "space_drone_cost": fields.Integer(
            description="Training cost of a SpaceDrone",
            required=True,
            attribute=lambda b: AttackUnit.get_training_cost_static("space_drone", b.space_drone_level),
        ),
    }
)


attack_unit_model = api.clone(
    "AttackUnitInfo",
    unit_model,
    {
        "building_id": fields.String(description="ID of the barrack", required=True),
        "seconds_since_last_feed": fields.Integer(description="Seconds since the unit was last fed", required=True),
        "training_pos": fields.Integer(description="Current position in the training queue", required=True),
        "training_time_left": fields.Float(
            description="Time left before the unit is trained. Only goes down when at the front of the queue",
            required=True,
        ),
    },
)

barrack_model = api.clone(
    "BarrackInfo",
    building_model, disabled_units, unit_costs,
    {
        "space_marine_level": fields.Integer(description="Space Marine level", required=True),
        "space_commando_level": fields.Integer(description="Space Commando level", required=True),
        "space_drone_level": fields.Integer(description="Space Drone level", required=True),
        "space_taken": fields.Integer(
            description="Space taken up", required=True, attribute=lambda b: b.get_space_taken()
        ),
        "space_capacity": fields.Integer(
            description="Space capacity", required=True, attribute=lambda b: b.max_capacity
        ),
    },
)

barrack_model_with_units = api.clone(
    "BarrackInfoWithUnits",
    barrack_model,
    {
        "training_units": fields.List(
            fields.Nested(attack_unit_model),
            description="List of units in training",
            attribute=lambda b: b.get_units_in_training(),
        ),
    },
)

barrack_parser = building_parser.copy().add_argument("include_training_units", type=inputs.boolean)


@api.route("/barrack")
class BarrackRes(Resource):
    @api.expect(barrack_parser)
    @api.response(HTTPStatus.OK, "Barrack info with units", barrack_model_with_units)
    @api.response(HTTPStatus.BAD_REQUEST, "Requested building is not a barrack")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def get(self):
        """
        Gets the units in training.
        """
        user_name = session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")
        data = barrack_parser.parse_args(request)
        with DefaultSession() as BaseSession:
            user = User.load_by_name(session.get("user_name", None), session=BaseSession)
            user.update()
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            barrack: Barrack = settlement_grid[data["pos_y"]][data["pos_x"]]

            if not isinstance(barrack, Barrack):
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building is not a barrack")

            if data["include_training_units"]:
                return marshal(barrack, barrack_model_with_units)
            return marshal(barrack, barrack_model)
