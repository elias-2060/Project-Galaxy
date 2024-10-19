from http import HTTPStatus

from backend import game_classes
from backend.api.achievement import api
from backend.game_classes import Achievement, User
from database.database_access import DefaultSession
from flask import request, session as flask_session
from flask_restx import Resource, fields, marshal


achievement_model = api.model(
    "Achievement",
    {
        "achievement_id": fields.String(
            description="ID of the achievement", required=True, attribute=lambda a: str(a.achievement_id)
        ),
        "achievement_name": fields.String(description="Name of the achievement", required=True),
        "achievement_description": fields.String(description="Description of the achievement", required=True),
        "reward": fields.Integer(description="Reward for the achievement", required=True),
        "redeem_state": fields.String(description="If the achievement is/can be redeemed", required=True),
    },
)


@api.route("/all")
class AllAchievements(Resource):
    # @api.expect()
    @api.response(HTTPStatus.OK, "List of all achievements", [achievement_model])
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    def get(self):
        """
        Get the list of all locked and unlocked achievements.
        """
        user_name = flask_session.get("user_name")
        if user_name is None:
            return api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        with DefaultSession() as session:
            user = session.query(User).filter(User.user_name == user_name).first()

            all_achievements = session.query(Achievement).all()
            user_achievement_ids = [a.achievement_id for a in user.achievements]

            # set unlocked flag
            for achievement in all_achievements:
                if achievement.achievement_id in user_achievement_ids:
                    achievement.redeem_state = "redeemed"
                elif eval(achievement.requirement):
                    achievement.redeem_state = "redeemable"
                else:
                    achievement.redeem_state = "non-redeemable"
            
            return marshal(all_achievements, achievement_model)
