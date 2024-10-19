from http import HTTPStatus

from backend.api.building import api
from backend.game_classes import Barrack, Building, Planet, Settlement, SpaceCommando, SpaceDrone, SpaceMarine, User
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource

unit_parser = (
    api.parser()
    .add_argument("unit", type=str, required=True)
    .add_argument("planet_number", type=int, required=True)
    .add_argument("settlement_number", type=int, required=True)
    .add_argument("pos_x", type=int, required=True)
    .add_argument("pos_y", type=int, required=True)
)


@api.route("/barrack/unit")
class Unit(Resource):
    @api.expect(unit_parser)
    @api.response(HTTPStatus.OK, "Unit added")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    @api.response(
        HTTPStatus.BAD_REQUEST, "Requested planet/settlement/building/unit doesn't exist or barrack doesn't have space"
    )
    def post(self):
        """
        Add a unit.
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = unit_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)

            planet: Planet = user.planets[data["planet_number"]]
            if planet is None:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested planet doesn't exist")

            settlement: Settlement = planet.settlements[data["settlement_number"]]
            if settlement is None:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested settlement doesn't exist")

            settlement_grid = settlement.get_grid(False)

            building: Building = settlement_grid[data["pos_y"]][data["pos_x"]]
            if building is None:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building doesn't exist")

            if data["unit"] == "Space Marine":
                unit = SpaceMarine(building.building_id)
            elif data["unit"] == "Space Commando":
                unit = SpaceCommando(building.building_id)
            elif data["unit"] == "Space Drone":
                unit = SpaceDrone(building.building_id)
            else:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested unit doesn't exist")

            building: Barrack
            result = building.train_unit(unit, session=session)
            session.commit()
            if result is not None:
                session.delete(unit)
                session.commit()
                api.abort(HTTPStatus.BAD_REQUEST, result)

            return Response("Unit added", HTTPStatus.OK)
