from http import HTTPStatus

from backend.api.planet import api
from backend.api.planet.planet import planet_coordinate_model
from backend.game_classes import Planet, User
from database.database_access import DefaultSession
from flask import request, session as flask_session
from flask_restx import Resource, inputs, marshal, fields

all_planets_parser = api.parser().add_argument("own_only", type=inputs.boolean)

planet_name_model = api.model('PlanetName', {
    "planet_name": fields.String(required=True, attribute=lambda p: p.planet_name),
})


@api.route("/all")
class AllPlanets(Resource):
    @api.response(HTTPStatus.OK, "List of all planets", [planet_coordinate_model])
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def get(self):
        """
        Get a list of all planets.
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = all_planets_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            if data["own_only"]:
                planets = user.planets
                return marshal(planets, planet_name_model)
            else:
                planets = Planet.get_all_planets(session=session)
                return marshal(planets, planet_coordinate_model)
