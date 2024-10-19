from http import HTTPStatus
from backend.api.building import api
from backend.api.building.building import building_parser
from backend.game_classes import Planet, User, Settlement, Warper, Building
from database.database_access import DefaultSession
from flask import request, session as flask_session, Response
from flask_restx import Resource

change_link_parser = (building_parser.copy()
                      .add_argument("planet_to_x", type=int, required=True)
                      .add_argument("planet_to_y", type=int, required=True)
                      )


@api.route("/warper/change_warp_link")
class WarperLinkRes(Resource):
    @api.expect(change_link_parser)
    def post(self):
        """
        Changes the current warp link
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            return api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = request.get_json()["params"]

        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            user.update()

            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            warper: Building = settlement_grid[data["pos_x"]][data["pos_y"]]

            if not isinstance(warper, Warper):
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building is not a warper")

            warper.change_warp_link(planet_to_x=data["planet_to_x"], planet_to_y=data["planet_to_y"], session=session)

            return Response("Link successfully created")
