from backend.api.planet import api
from backend.game_classes import Planet, Settlement, User
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource


@api.route("/settlement")
class Settlements(Resource):
    def post(self):
        """
        Adds a settlement to the planet.
        """
        user_name = flask_session.get("user_name", None)

        data = request.get_json()
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)

            selected_planet = data["planet_number"]
            planet: Planet = user.planets[selected_planet]

            # Remove the resources
            planet.building_materials -= 5000
            session.commit()

            settlement: Settlement = Settlement(planet.settlements[-1].settlement_nr + 1, planet.planet_id)

            planet.add_settlement(settlement, session=session)

            return Response("Settlement added")
