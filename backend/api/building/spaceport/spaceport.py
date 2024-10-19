from http import HTTPStatus

from backend.api.building import api
from backend.api.building.building import building_parser
from backend.api.planet.all import planet_name_model
from backend.game_classes import Planet, Settlement, User, Spaceport, Barrack, SpaceMarine, SpaceDrone, SpaceCommando
from database.database_access import DefaultSession
from flask import request, session, Response
from flask_restx import Resource, fields, marshal

spaceport_model = api.model(
    "Spaceport",
    {
        "ship_present": fields.Boolean(
            required=True,
            attribute=lambda port: port.space_ship.destination is None
        ),
        "planet_names": fields.List(
            fields.Nested(planet_name_model),
            required=True,
            attribute=lambda port: port.settlement.planet.get_all_other_planets()
        ),
        "rations": fields.Integer(
            required=True,
            attribute=lambda port: port.settlement.planet.rations
        ),
        "building_materials": fields.Integer(
            required=True,
            attribute=lambda port: port.settlement.planet.building_materials
        ),
        "unit_capacity": fields.Integer(
            required=True,
            attribute=lambda port: port.space_ship.unit_capacity
        ),
        "resource_capacity": fields.Integer(
            required=True,
            attribute=lambda port: port.space_ship.resource_capacity
        ),
        "space_marine_nr": fields.Integer(
            required=True,
            attribute=lambda port: port.get_transportable_unit_counts()["space_marine_nr"]
        ),
        "space_commando_nr": fields.Integer(
            required=True,
            attribute=lambda port: port.get_transportable_unit_counts()["space_commando_nr"]
        ),
        "space_drone_nr": fields.Integer(
            required=True,
            attribute=lambda port: port.get_transportable_unit_counts()["space_drone_nr"]
        )
    }
)


@api.route("/spaceport")
class BarrackRes(Resource):
    @api.expect(building_parser)
    @api.response(HTTPStatus.OK, "Barrack info with units", [planet_name_model])
    @api.response(HTTPStatus.BAD_REQUEST, "Requested building is not a barrack")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def get(self):
        """
        Get all the spaceport attributes it needs
        """
        user_name = session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")
        data = building_parser.parse_args(request)
        with DefaultSession() as BaseSession:
            user = User.load_by_name(session.get("user_name", None), session=BaseSession)
            user.update()
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            spaceport: Spaceport = settlement_grid[data["pos_x"]][data["pos_y"]]

            if not isinstance(spaceport, Spaceport):
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building is not a spaceport")

            return marshal(spaceport, spaceport_model)

    @api.response(HTTPStatus.OK, "Barrack info with units", [planet_name_model])
    @api.response(HTTPStatus.BAD_REQUEST, "Requested building is not a barrack")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def post(self):
        """
        Launch a spaceship
        """
        user_name = session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")
        data = request.get_json()["params"]
        with DefaultSession() as BaseSession:
            user = User.load_by_name(session.get("user_name", None), session=BaseSession)
            user.update()
            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            spaceport: Spaceport = settlement_grid[data["pos_x"]][data["pos_y"]]

            to_planet: Planet = BaseSession.query(Planet).filter_by(planet_name=data["planet_name"]).first()

            if not isinstance(spaceport, Spaceport):
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building is not a spaceport")

            # Get the attack units
            barracks = [building for building in settlement.buildings if isinstance(building, Barrack)]
            units = []
            for barrack in barracks:
                for unit in barrack.attack_units:
                    if not unit.in_training():
                        units.append(unit)

            spaceship = spaceport.space_ship

            # Board the requested units
            if data["transport_type"] == "soldiers":
                if data["unit_type"] == "Space-Marine":
                    space_marines = [unit for unit in units if isinstance(unit, SpaceMarine)]
                    for i in range(data["amount"]):
                        spaceship.board_attack_unit(space_marines[0])
                elif data["unit_type"] == "Space-Commando":
                    space_commandos = [unit for unit in units if isinstance(unit, SpaceCommando)]
                    for i in range(data["amount"]):
                        spaceship.board_attack_unit(space_commandos[0])
                elif data["unit_type"] == "Space-Drone":
                    space_drones = [unit for unit in units if isinstance(unit, SpaceDrone)]
                    for i in range(data["amount"]):
                        spaceship.board_attack_unit(space_drones[0])

            # Board the requested resources
            elif data["transport_type"] == "rations":
                spaceship.board_rations(planet, data["amount"])
            elif data["transport_type"] == "materials":
                spaceship.board_building_materials(planet, data["amount"])
            else:
                raise ValueError(data["transport_type"])

            # Move the ship
            spaceport.space_ship.move_from_to_planet(planet, to_planet)
            return Response("Spaceship successfully sent")
