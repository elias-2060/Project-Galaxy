from http import HTTPStatus

from backend.api.combat import api
from backend.game_classes import Planet, User, Attack, AttackUnit
from backend.api.planet.planet import planet_model
from database.database_access import DefaultSession
from flask import Response, request, session as flask_session
from flask_restx import Resource, marshal, fields


@api.route("/end_attack", methods=["POST"])
class EndAttack(Resource):
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    @api.response(HTTPStatus.OK, "Success")
    def post(self):
        """
        Plays a round

        planet_name: attacking planet name
        selected_attack_type: type of selected attack unit
        """
        # Get the data items
        data = request.get_json()["params"]
        planet_from_name = data["planet_name"]
        user_name = flask_session.get("user_name", None)
        opponent_won = data["opponent_won"]

        with DefaultSession() as BaseSession:
            # Update the user
            curr_user = User.load_by_name(user_name, session=BaseSession)
            curr_user.update()

            # Load the planet and attack
            planet_from: Planet = BaseSession.query(Planet).filter(Planet.planet_name == planet_from_name).first()
            attack: Attack = planet_from.current_offence_attack
            assert attack is not None

            if opponent_won:
                attack.lose()
            else:
                attack.win()

            return Response("Successfully ended combat")
