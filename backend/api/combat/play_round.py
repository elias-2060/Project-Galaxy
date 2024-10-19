import json
from http import HTTPStatus

from backend.api.combat import api
from backend.game_classes import Planet, User, SpaceDrone, SpaceMarine, SpaceCommando, Attack, AttackUnit
from database.database_access import DefaultSession
from flask import Response, request, session as flask_session
from flask_restx import Resource


@api.route("/play_round", methods=["POST"])
class LoadEnemy(Resource):
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
        selected_attack_type = data["selected_attack_type"]
        user_name = flask_session.get("user_name", None)

        # Get the item class
        if selected_attack_type == "Space-Marines":
            itemClass = SpaceMarine
        elif selected_attack_type == "Space-Commandos":
            itemClass = SpaceCommando
        elif selected_attack_type == "Space-Drones":
            itemClass = SpaceDrone
        else:
            raise NotImplementedError(selected_attack_type)

        # The result dict
        result: dict = {}

        # Make the attack
        with DefaultSession() as BaseSession:
            # Update the user
            curr_user = User.load_by_name(user_name, session=BaseSession)
            curr_user.update()

            # Load the planet and attack
            planet_from: Planet = BaseSession.query(Planet).filter(Planet.planet_name == planet_from_name).first()
            attack: Attack = planet_from.current_offence_attack
            assert attack is not None

            # Get the attacking units and sort them by attack power
            attack_units: list[AttackUnit] = attack.get_attacking_units()
            attack_units = sorted(attack_units, key=lambda x: x.attack_power, reverse=True)

            # Get the attack unit
            attack_unit = None
            for unit in attack_units:
                if isinstance(unit, itemClass):
                    attack_unit = unit
                    break
            assert attack_unit is not None, "No attack unit of asked class"

            # Get the defending units and sort them by attack power
            defending_units: list[AttackUnit] = attack.get_defending_units()
            defending_units = sorted(defending_units, key=lambda x: x.attack_power, reverse=True)
            defending_unit = defending_units[0]

            # Do the attack
            attack.select_unit_attacking(attack_unit.unit_id)
            attack.select_unit_defending(defending_unit.unit_id)
            round_result: dict = attack.play_round(auto_select_defence=False, auto_delete=False)

            # Sort the attacking units by
            result["roll_a"] = round_result["attack_roll"]
            result["roll_b"] = round_result["defence_roll"]
            result["live_a"] = round_result["attack_survive"]
            result["live_a"] = round_result["defence_survive"]
            result["passive_a"] = round_result["passive_attack"]
            result["passive_b"] = round_result["passive_defense"]
            result["combat_result"] = round_result["combat_result"]

            BaseSession.commit()
            return Response(json.dumps(result), mimetype="application/json")
