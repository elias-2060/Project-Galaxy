from http import HTTPStatus

from backend.api.planet import api
from backend.api.settlement.settlement import settlement_model
from backend.game_classes import Planet, Settlement, TownHall, User, Settlement
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource, fields, inputs, marshal

forward = lambda o: o
"Return the provided object. When used in nested marshaling this results in forwarding the object to the nested model"


planet_coordinate_model = api.model(
    "PlanetCoordinates",
    {
        "planet_x": fields.Integer(description="X coordinate of the planet", required=True),
        "planet_y": fields.Integer(description="Y coordinate of the planet", required=True),
    },
)

planet_resource_model = api.model(
    "PlanetResources",
    {
        "building_materials": fields.Integer(description="Amount of building materials the planet has", required=True),
        "rations": fields.Integer(description="Amount of rations the planet has", required=True),
        "attack_power": fields.Integer(
            description="Amount of attack power the planet has",
            required=True,
            attribute=lambda p: p.get_attack_power(),
        ),
    },
)

planet_model = api.model(
    "PlanetInfo",
    {
        "planet_id": fields.String(description="ID of the planet", required=True),
        "coordinates": fields.Nested(
            planet_coordinate_model,
            description="Coordinates of the planet",
            required=True,
            attribute=forward,
        ),
        "user_id": fields.String(description="ID of the user who owns the planet", required=True),
        "planet_name": fields.String(description="Name of the planet", required=True),
        "resources": fields.Nested(
            planet_resource_model,
            description="Resources of the planet",
            required=True,
            attribute=forward,
        ),
    },
)
planet_model_with_settlements = api.clone(
    "PlanetInfoWithSettlements",
    planet_model,
    {
        "settlements": fields.List(
            fields.Nested(
                settlement_model,
                description="List of settlements",
                required=True,
            ),
            attribute=lambda p: p.settlements,
        ),
    },
)

get_planet_parser = (
    api.parser()
    .add_argument("planet_number", type=int, default=None)
    .add_argument("include_settlements", type=inputs.boolean)
)
post_planet_parser = (
    api.parser()
    .add_argument("pos_x", type=int, required=True)
    .add_argument("pos_y", type=int, required=True)
    .add_argument("planet_name", type=str, required=True)
)


@api.route("")
class PlanetRes(Resource):
    @api.expect(post_planet_parser)
    def post(self):
        """
        Add a planet to the database.
        """
        data = post_planet_parser.parse_args(request)
        with DefaultSession(autoflush=False) as session:
            user_name = flask_session.get("user_name", None)
            user = User.load_by_name(user_name, session=session)

            # Remove 10k from the first planet that can afford it
            for planet in user.planets:
                if planet.building_materials >= 10000:
                    planet.building_materials -= 10000
                    session.commit()
                    break

            planet: Planet = Planet(
                user_id=user.user_id,
                planet_x=data["pos_x"],
                planet_y=data["pos_y"],
                name=data["planet_name"],
            )

            user.add_planet(planet, session=session)
            session.commit()

            settlement: Settlement = Settlement(0, planet.planet_id)
            planet.add_settlement(settlement, session=session)

            building: TownHall = TownHall(settlement.settlement_id, 2, 2)

            settlement.build(building, session=session)

            session.commit()

        return Response("Planet added")

    @api.response(HTTPStatus.OK, "Planet information", planet_model_with_settlements)
    @api.response(HTTPStatus.BAD_REQUEST, "Invalid argument combination")
    @api.response(HTTPStatus.NOT_FOUND, "Requested planet doesn't exist")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def get(self):
        """
        Gets the resources of the user.
        """
        data = get_planet_parser.parse_args(request)
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        planet_number = data["planet_number"]
        if planet_number is None:
            planet_number = 0

        with DefaultSession() as session:
            user = User.load_by_name(flask_session.get("user_name", None), session=session)
            if planet_number is not None:
                try:
                    planet: Planet = user.planets[planet_number]
                except IndexError:
                    planet = None
            else:
                api.abort(HTTPStatus.BAD_REQUEST, "Invalid argument combination")

            if planet is None:
                api.abort(HTTPStatus.NOT_FOUND, "Requested planet doesn't exist")

            if data["include_settlements"]:
                return marshal(planet, planet_model_with_settlements)
            return marshal(planet, planet_model)
