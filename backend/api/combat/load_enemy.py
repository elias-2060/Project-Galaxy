from http import HTTPStatus

from backend.api.combat import api
from backend.game_classes import Planet, User
from backend.api.planet.planet import planet_model
from database.database_access import DefaultSession
from flask import Response, request, session as flask_session
from flask_restx import Resource, marshal


@api.route("/load_enemy", methods=["POST"])
class LoadEnemy(Resource):
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    @api.response(HTTPStatus.OK, "Success")
    def post(self):
        """
        Attacks another planet
        """
        # Get the data items
        data = request.get_json()["params"]
        user_name = flask_session.get("user_name", None)
        planet_from_name = data["planet_name"]

        # Make the attack
        with DefaultSession() as BaseSession:
            curr_user: User = User.load_by_name(user_name, session=BaseSession)
            curr_user.update()
            planet_from: Planet = BaseSession.query(Planet).filter(
                Planet.planet_name == planet_from_name,
                Planet.user_id == curr_user.user_id,
            ).first()
            planet_to: Planet = BaseSession.query(Planet).filter(
                Planet.planet_x == data["planet_x"],
                Planet.planet_y == data["planet_y"],
            ).first()

            # Can't attack its own planet ofcourse
            if planet_from.user_id == planet_to.user_id:
                print("User can't attack its own planet")
                return Response("User can't attack its own planet")

            # If there is a left behind attack, remove it
            if planet_from.current_offence_attack is not None:
                BaseSession.delete(planet_from.current_offence_attack)
                BaseSession.commit()

            BaseSession.commit()
            return marshal(planet_to, planet_model)
