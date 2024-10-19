from http import HTTPStatus
import json

from backend.api.building.building import building_model
from backend.api.ship import api
from backend.game_classes import Planet, Settlement, User, Spaceship, Spaceport
from database.database_access import DefaultSession
from flask import request, Response
from flask import session as flask_session
from flask_restx import Resource, fields, marshal

ship_model = api.model(
    'Ship',
    {
        "ship_type": fields.String(
            required=True,
            attribute=lambda ship: ship.type,
        ),
        "ship_description": fields.String(
            required=True,
            attribute=lambda ship: ship.get_description(),
        ),
        "ship_return_time": fields.Float(
            required=True,
            attribute=lambda ship: ship.get_return_time(),
        )
    }
)

ship_model_list_item = api.model(
    'Ship',
    {
        "ship_type": fields.String(
            required=True,
            attribute=lambda ship: ship.type,
        ),
        "ship_description": fields.String(
            required=True,
            attribute=lambda ship: ship.get_description(),
        ),
        "ship_return_time": fields.Float(
            required=True,
            attribute=lambda ship: ship.moving_time_left,
        )
    }
)

ships_model = api.model(
    'Ships',
    {
        "incoming_ships": fields.List(
            fields.Nested(
                ship_model_list_item,
                required=True,
                attribute=lambda d: d["incoming_ships"],
            )
        ),
        "outgoing_ships": fields.List(
            fields.Nested(
                ship_model_list_item,
                required=True,
                attribute=lambda d: d["outgoing_ships"],
            )
        )
    }
)

get_ships_parser = (
    api.parser()
    .add_argument("planet_number", type=int, required=True)
)


@api.route("/spaceship/get_ships")
class GetShipsRes(Resource):
    @api.expect(get_ships_parser)
    @api.response(HTTPStatus.OK, "Settlement information", ships_model)
    @api.response(HTTPStatus.BAD_REQUEST, "Requested planet or settlement does not exist")
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    def get(self):
        """
        Gets the ships from the planet
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = get_ships_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)

            try:
                planet: Planet = user.planets[data["planet_number"]]
            except IndexError:
                api.abort(HTTPStatus.BAD_REQUEST, "Requested planet does not exist")

            # Get the outgoing spaceships
            settlements = planet.settlements
            outgoing_ships = []
            for settlement in settlements:
                for building in settlement.buildings:
                    if (
                            isinstance(building, Spaceport) and
                            building.space_ship.moving_time_left > 0 and
                            building.space_ship.destination != planet
                    ):
                        outgoing_ships.append(building.space_ship)

            # Get all incoming spaceships
            incoming_ships: list[Spaceship] = planet.incoming_spaceships

            # Make the result
            result = {
                "outgoing_ships": [],
                "incoming_ships": []
            }
            for ship in outgoing_ships:
                result["outgoing_ships"].append(
                    {"type": ship.type,
                     "ship_return_time": ship.moving_time_left,
                     "ship_description": ship.get_description(),
                     })
            for ship in incoming_ships:
                result["incoming_ships"].append(
                    {"type": ship.type,
                     "ship_return_time": ship.moving_time_left,
                     "ship_description": ship.get_description(),
                     })
            return Response(json.dumps(result))


@api.route("/spaceship/get_ship")
class GetShipRes(Resource):
    @api.expect(building_model)
    @api.response(HTTPStatus.OK, "Settlement information", building_model)
    @api.response(HTTPStatus.BAD_REQUEST, "Requested planet or settlement does not exist")
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    def get(self):
        """
        Gets the ships from the planet
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = building_model.parse_args(request)
        with DefaultSession() as BaseSession:
            user = User.load_by_name(flask_session.get("user_name", None), session=BaseSession)
            user.update()
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            spaceport: Spaceport = settlement_grid[data["pos_x"]][data["pos_y"]]
            ship = spaceport.space_ship
            return marshal(ship, ship_model)
