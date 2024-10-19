from http import HTTPStatus

from backend.api.building import api
from backend.game_classes import Building, Farm, Mine, Planet, Settlement, User, Warper
from database.database_access import DefaultSession
from flask import request
from flask import session as flask_session
from flask_restx import Resource, fields, marshal


grid_pos_model = api.model(
    "BuildingGridPos",
    {
        "grid_pos_x": fields.Integer(description="X position of the building on the grid"),
        "grid_pos_y": fields.Integer(description="Y position of the building on the grid"),
    },
)

building_model = api.model(
    "BuildingInfo",
    {
        "building_id": fields.String(description="ID of the building", required=True),
        "settlement_id": fields.String(description="ID of the settlement the building is in", required=True),
        "grid_pos": fields.Nested(
            grid_pos_model,
            description="Grid position of the building",
            required=True,
            attribute=lambda b: b,
        ),
        "level": fields.Integer(description="Level of the building", required=True),
        "construction_time_left": fields.Integer(description="Construction time remaining", required=True),
        "type": fields.String(description="Type of building", required=True),
        "gathering_time_left": fields.Integer(
            description="Gathering time remaining",
            attribute=lambda b: b.gathering_time_left if isinstance(b, (Farm, Mine)) else None,
        ),
        "stored_resources": fields.Integer(
            description="Amount of resources stored",
            attribute=lambda b: b.gathering_time_left if isinstance(b, (Farm, Mine)) else None,
        ),
    },
)
building_parser = (
    api.parser()
    .add_argument("planet_number", type=int, required=True)
    .add_argument("settlement_number", type=int, required=True)
    .add_argument("pos_x", type=int, required=True)
    .add_argument("pos_y", type=int, required=True)
)

used_warper_model = api.clone(
    "BuildingWarper",
    building_model,
    {
        "warped_to": fields.String(
            required=True,
            attribute=lambda warper: warper.planet_link.get_planet_to().planet_name
        )
    }
)


@api.route("")
class BuildingRes(Resource):
    @api.expect(building_parser)
    @api.response(HTTPStatus.OK, "Get building information", building_model)
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    def get(self):
        """
        Gets building information.
        """
        if flask_session.get("user_name") is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = building_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(flask_session.get("user_name", None), session=session)
            user.update(session=session)
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            building: Building = settlement_grid[data["pos_y"]][data["pos_x"]]

            # For warpers
            if isinstance(building, Warper) and building.planet_link is not None:
                return marshal(building, used_warper_model)

            return marshal(building, building_model)
