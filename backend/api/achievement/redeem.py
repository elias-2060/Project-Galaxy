from http import HTTPStatus

from backend import game_classes
from backend.api.achievement import api
from backend.game_classes import Achievement, User
from database.database_access import DefaultSession
from flask import request, session as flask_session
from flask_restx import Resource, fields, marshal


redeem_parser = api.parser().add_argument("achievement_id", type=str, required=True)


@api.route("/redeem")
class Redeem(Resource):
    @api.expect(redeem_parser)
    @api.response(HTTPStatus.OK, "Redeemed achievement")
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    @api.response(HTTPStatus.NOT_FOUND, "Achievement not found")
    @api.response(HTTPStatus.BAD_REQUEST, "Achievement not redeemable or already redeemed")
    def post(self):
        """
        Redeem an achievement.
        """
        user_name = flask_session.get("user_name")
        if user_name is None:
            return api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = redeem_parser.parse_args(request)
        with DefaultSession() as session:
            user = session.query(User).filter(User.user_name == user_name).first()
            
            achievement = Achievement.load(data["achievement_id"], session)
            if achievement is None:
                return api.abort(HTTPStatus.NOT_FOUND, "Achievement not found")

            if any(a.achievement_id == achievement.achievement_id for a in user.achievements):
                return api.abort(HTTPStatus.BAD_REQUEST, "Achievement already redeemed")
            
            if not eval(achievement.requirement):
                return api.abort(HTTPStatus.BAD_REQUEST, "Achievement not redeemable")

            user.achievements.append(achievement)
            user.planets[0].add_building_materials(achievement.reward)
            session.commit()