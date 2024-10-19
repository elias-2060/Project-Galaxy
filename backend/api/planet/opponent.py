from http import HTTPStatus
from flask import request, session as flask_session
from flask_restx import Resource, fields, marshal
from backend.api.planet.planet import planet_resource_model, forward
from backend.api.planet import api
from backend.game_classes import Planet
from database.database_access import DefaultSession

planet_opponent_model = api.model(
    "PlanetOpponentInfo",
    {
        "planet_id": fields.String(description="ID of the planet", required=True),
        "planet_name": fields.String(description="Name of the planet", required=True),
        "user_id": fields.String(description="ID of the user who owns the planet", required=True),
        "user_name": fields.String(
            description="Name of the user who owns the planet", required=True, attribute=lambda p: p.user.user_name
        ),
        "race_id": fields.String(
            description="ID of the race of the user is part of",
            required=True,
            attribute=lambda p: p.user.race_id if p.user.race_id is not None else None,
        ),
        "race_name": fields.String(
            description="Name of the race of the user is part of",
            required=True,
            attribute=lambda p: p.user.race.race_name if p.user.race_id is not None else None,
        ),
        "resources": fields.Nested(
            planet_resource_model,
            description="Resources of the planet",
            required=True,
            attribute=forward,
        ),
        "attack_power": fields.Integer(
            description="AttackPower of the enemy",
            required=True,
            attribute=lambda p: p.get_attack_power()
        )
    },
)

planet_opponent_parser = api.parser().add_argument("pos_x", type=int).add_argument("pos_y", type=int)


@api.route("/opponent")
class Opponent(Resource):
    @api.expect(planet_opponent_parser)
    @api.response(HTTPStatus.OK, "Oppenent info")
    @api.response(HTTPStatus.BAD_REQUEST, "Requested planet does not exist")
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    def get(self):
        """
        Get the opponent for the planet at the given coordinates
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = planet_opponent_parser.parse_args(request)
        with DefaultSession() as session:
            planet = Planet.get_by_pos(data["pos_x"], data["pos_y"], session=session)
            planet.user.update()
            if planet is None:
                api.abort(HTTPStatus.BAD_REQUEST, "Planet does not exist")

            return marshal(planet, planet_opponent_model)
