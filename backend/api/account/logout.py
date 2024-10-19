from http import HTTPStatus

from backend.api.account import api
from flask import Response
from flask import session as flask_session
from flask_restx import Resource


@api.route("/logout")
class Logout(Resource):
    @api.response(HTTPStatus.NO_CONTENT, "Logged out")
    @api.response(HTTPStatus.BAD_REQUEST, "Not logged in")
    def post(self):
        """
        Logs a user out of the game
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            return Response("Not logged in", HTTPStatus.OK)

        flask_session.pop("user_name")
        flask_session.clear()

        return Response(f"{user_name} logged out", HTTPStatus.OK)
