from backend.api.building import api
from backend.game_classes import Planet, Settlement, User
from backend.game_classes.Buildings.Building import Building
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource

building_parser = (
    api.parser()
    .add_argument("planet_number", type=int, required=True)
    .add_argument("settlement_number", type=int, required=True)
    .add_argument("pos_x", type=int, required=True)
    .add_argument("pos_y", type=int, required=True)
)


@api.route("/upgrade")
class Upgrade(Resource):
    @api.expect(building_parser)
    def post(self):
        """
        Upgrades a building.
        """
        data = building_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(flask_session.get("user_name", None), session=session)
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            building: Building = settlement_grid[data["pos_y"]][data["pos_x"]]

            building.upgrade()

            session.commit()

            return Response(str(building.level))
