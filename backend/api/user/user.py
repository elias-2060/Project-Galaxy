from http import HTTPStatus

from backend.api.user import api
from backend.game_classes import User
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource, fields

user_model = api.model(
    "UserInfo",
    {
        "user_id": fields.String(required=True, example="0B75004A-9A44-4A63-8DF0-4FAA6947A013"),
        "user_name": fields.String(required=True, example="John"),
        "race_id": fields.String(example="230D3282-68B0-45DF-9DB6-0169FD5E93F6"),
        "race_name": fields.String(example="The Johnian Race"),
    },
)

get_user_parser = api.parser().add_argument("user_id", type=str)


@api.route("")
class UserRes(Resource):
    @api.expect(get_user_parser)
    @api.response(HTTPStatus.OK, "Success", user_model)
    @api.response(HTTPStatus.BAD_REQUEST, "Not logged in")
    @api.response(HTTPStatus.INTERNAL_SERVER_ERROR, "Missing from database")
    def get(self):
        """
        Gets the user from the database.
        """

        user_name = flask_session.get("user_name", None)
        if user_name is None:
            return Response("Not logged in", HTTPStatus.BAD_REQUEST)

        data = get_user_parser.parse_args(request)
        with DefaultSession() as session:
            if data["user_id"] is not None:
                user: User = User.load_by_id(data["user_id"], session=session)
            else:
                user: User = User.load_by_name(user_name, session=session)

            if user is None:
                return Response("Missing from database", HTTPStatus.INTERNAL_SERVER_ERROR)

            user.update()
            return Response(user.json(session=session), HTTPStatus.OK, mimetype="application/json")
