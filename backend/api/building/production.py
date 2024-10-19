import json
from http import HTTPStatus

from backend.api.building import api
from backend.game_classes import Building, Farm, Mine, Planet, Settlement, User
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource

production_parser = (
    api.parser()
    .add_argument("planet_number", type=int, required=True)
    .add_argument("settlement_number", type=int, required=True)
    .add_argument("pos_x", type=int, required=True)
    .add_argument("pos_y", type=int, required=True)
)


@api.route("/production")
class StartProduction(Resource):
    @api.expect(production_parser)
    @api.response(HTTPStatus.OK, "Start production")
    @api.response(HTTPStatus.BAD_REQUEST, "Requested building is not a farm or mine")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def post(self):
        """
        Start production.
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = production_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            building: Building = settlement_grid[data["pos_y"]][data["pos_x"]]

            if not isinstance(building, (Farm, Mine)):
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building is not a farm or mine")

            building.start_gathering()

            session.commit()

            return Response(json.dumps(building.gathering_time_left))

    @api.expect(production_parser)
    @api.response(HTTPStatus.OK, "Collected resources")
    @api.response(HTTPStatus.BAD_REQUEST, "Requested building is not a farm or mine")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def get(self):
        """
        Collect resources.
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = production_parser.parse_args(request)
        with DefaultSession() as BaseSession:
            user = User.load_by_name(flask_session.get("user_name", None), session=BaseSession)
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            building: Building = settlement_grid[data["pos_y"]][data["pos_x"]]
            if not isinstance(building, (Farm, Mine)):
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building is not a farm or mine")

            success: bool = building.collect_resources(session=BaseSession)

            BaseSession.commit()

            return Response(str(success))
