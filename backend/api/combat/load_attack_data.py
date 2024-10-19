from http import HTTPStatus

from backend.api.combat import api
from backend.game_classes import Planet, User, Attack, AttackUnit
from backend.api.planet.planet import planet_model
from database.database_access import DefaultSession
from flask import Response, request, session as flask_session
from flask_restx import Resource, marshal, fields


unit_model = api.model('Unit', {
    "type": fields.String(required=True, attribute=lambda unit: unit.type_string),
    "attack_power": fields.Integer(required=True, attribute=lambda unit: unit.attack_power)
})

attack_model = api.model(
    "OpponentModel",
    {
        "opponent": fields.Nested(
            planet_model,
            required=True,
            attribute=lambda attack: attack.defending_planet
        ),
        "attacking_units": fields.List(
            fields.Nested(unit_model),
            required=True,
            attribute=lambda attack: attack.get_attacking_units()
        ),
        "defending_units": fields.List(
            fields.Nested(unit_model),
            required=True,
            attribute=lambda attack: attack.get_defending_units()
        )
    }
)


@api.route("/load_attack_data", methods=["POST"])
class LoadAttackData(Resource):
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    @api.response(HTTPStatus.OK, "Success")
    def post(self):
        """
        Gets the attack data
        """
        # Get the data items
        data = request.get_json()["params"]
        user_name = flask_session.get("user_name", None)
        planet_from_name = data["planet_name"]
        planet_xy_to = data["planet_xy_to"]
        create_attack: bool = data["create_attack"]

        # Make the attack
        with DefaultSession() as BaseSession:
            curr_user: User = User.load_by_name(user_name, session=BaseSession)
            planet_from: Planet = BaseSession.query(Planet).filter(
                Planet.planet_name == planet_from_name,
                Planet.user_id == curr_user.user_id,
            ).first()
            planet_to: Planet = BaseSession.query(Planet).filter(
                Planet.planet_x == planet_xy_to[0],
                Planet.planet_y == planet_xy_to[1],
            ).first()

            # Get the current attack
            if (
                    create_attack and
                    planet_from.current_defence_attack is None and
                    planet_to.current_defence_attack is None
            ):
                attack: Attack = planet_from.attack(planet_to.planet_id)
                BaseSession.add(attack)
                BaseSession.commit()

            attack: Attack = planet_from.current_offence_attack
            assert attack is not None, "Other planet is already defending against someone"

            BaseSession.commit()
            return marshal(attack, attack_model)
