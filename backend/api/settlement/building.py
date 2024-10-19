from backend.api.settlement import api
from backend.game_classes import Barrack, Farm, Mine, Planet, Settlement, User, Warper, Spaceport, Spaceship
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
add_building_parser = building_parser.copy().add_argument("building", type=int, required=True)


@api.route("/building")
class AddBuilding(Resource):
    @api.expect(add_building_parser)
    def post(self):
        """
        Add a building to the settlement.
        """
        data = add_building_parser.parse_args(request)

        with DefaultSession(autoflush=False) as session:
            user = User.load_by_name(flask_session.get("user_name", None), session=session)
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            if data["building"] == 1:
                return Response("can't add another townhall")
            elif data["building"] == 2:
                building = Barrack(settlement.settlement_id, data["pos_x"], data["pos_y"])
                settlement.build(building, session=session)
            elif data["building"] == 3:
                building = Mine(settlement.settlement_id, data["pos_x"], data["pos_y"])
                settlement.build(building, session=session)
            elif data["building"] == 4:
                building = Farm(settlement.settlement_id, data["pos_x"], data["pos_y"])
                settlement.build(building, session=session)
            elif data["building"] == 5:
                building = Spaceport(settlement.settlement_id, data["pos_x"], data["pos_y"])
                settlement.build(building, session=session)
                session.commit()
                spaceship = Spaceship(building.settlement.planet.user.user_id)
                session.add(spaceship)
                session.commit()
                building.space_ship_id = spaceship.ship_id
                building.spaceship = spaceship
                session.commit()
                pass
            elif data["building"] == 6:
                building = Warper(settlement.settlement_id, data["pos_x"], data["pos_y"])
                settlement.build(building, session=session)
            else:
                raise NotImplementedError("type: ", data["building"])

            session.commit()

        return Response("Building added")

    @api.expect(building_parser)
    def delete(self):
        """
        Remove a building from the settlement.
        """
        data = building_parser.parse_args(request)

        with DefaultSession() as BaseSession:
            user = User.load_by_name(flask_session.get("user_name", None), session=BaseSession)
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            building: Building = settlement_grid[data["pos_y"]][data["pos_x"]]

            settlement.remove_building(building, session=BaseSession)

            BaseSession.commit()

        return Response("Building removed")
