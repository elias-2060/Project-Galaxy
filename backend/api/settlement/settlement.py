from http import HTTPStatus
import json

from backend.api.building.building import building_model
from backend.api.settlement import api
from backend.game_classes import Planet, Settlement, User
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource, fields, inputs

settlement_model = api.model(
    "SettlementInfo",
    {
        "settlement_id": fields.String(description="ID of the settlement", required=True),
        "settlement_number": fields.Integer(description="Number of the settlement", required=True),
        "planet_id": fields.String(description="ID of the planet the settlement is on", required=True),
    },
)

settlement_model_with_grid = api.clone(
    "SettlementInfoWithGrid",
    settlement_model,
    {
        "grid": fields.List(
            fields.List(fields.Nested(building_model, description="Building", nullable=True), description="Grid row"),
            description="Grid",
            attribute=lambda s: s.get_grid(False),
        ),
    },
)

get_settlement_parser = (
    api.parser()
    .add_argument("planet_number", type=int, required=True)
    .add_argument("settlement_number", type=int, required=True)
    .add_argument("include_grid", type=inputs.boolean)
)
post_settlement_parser = (
    api.parser()
    .add_argument("planet_number", type=int, required=True)
)


@api.route("")
class SettlementRes(Resource):
    @api.expect(get_settlement_parser)
    @api.response(HTTPStatus.OK, "Settlement information", settlement_model_with_grid)
    @api.response(HTTPStatus.BAD_REQUEST, "Requested planet or settlement does not exist")
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    def get(self):
        """
        Gets settlement from the database
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = get_settlement_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)

            try:
                planet: Planet = user.planets[data["planet_number"]]
            except IndexError:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested planet does not exist")

            try:
                settlement: Settlement = planet.settlements[data["settlement_number"]]
            except IndexError:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested settlement does not exist")

            settlement_grid = settlement.get_grid(True)

            return Response(json.dumps(settlement_grid), mimetype="application/json")

    @api.expect(post_settlement_parser)
    @api.response(HTTPStatus.CREATED, "Settlement added")
    @api.response(HTTPStatus.BAD_REQUEST, "Requested planet does not exist")
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    def post(self):
        """
        Adds a settlement to the database
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = get_settlement_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)

            selected_planet = data["planet_number"]

            try:
                planet: Planet = user.planets[selected_planet]
            except IndexError:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested planet does not exist")

            settlement: Settlement = Settlement(planet.settlements[-1].settlement_nr + 1, planet.planet_id)

            planet.add_settlement(settlement, session=session)

            return Response("Settlement added", HTTPStatus.CREATED)
