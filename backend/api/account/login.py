from http import HTTPStatus

from backend.api.account import active_users, api
from backend.game_classes import User
from backend.game_classes.General import check_user
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource, fields

login_model = api.model(
    "LoginInfo",
    {
        "user_name": fields.String(description="Name of user logging in", example="John", required=True),
        "password": fields.String(description="Password of the user", example="5aBG2Th", required=True),
    },
)
login_parser = (
    api.parser()
    .add_argument(
        "user_name",
        type=str,
        required=True,
        trim=True,
        help="Expected username. Encountered error {error_msg}",
    )
    .add_argument(
        "password",
        type=str,
        required=True,
        trim=True,
        help="Expected user password. Encountered error {error_msg}",
    )
)


@api.route("/login")
class Login(Resource):
    @api.response(HTTPStatus.OK, "Successfully logged in")
    @api.response(HTTPStatus.BAD_REQUEST, "Invalid combination of username and password")
    # @api.expect(api.model("TestMod", {"Test": fields.String(example="tes")}))
    @api.expect(login_model)
    def post(self):
        """
        Checks if the user and password combination exists and logs a user in to the game_classes
        """
        data = login_parser.parse_args(request)
        result: bool = check_user(user_name=data["user_name"], user_password=data["password"])
        if not result:
            return Response("Invalid combination of username and password", HTTPStatus.BAD_REQUEST)

        with DefaultSession() as db_session:
            # We load the user into the backend classes
            user = User.load_by_name(data["user_name"], session=db_session)

            # Add the user to the list of active users
            active_users[user.user_id] = user

            flask_session["user_id"] = user.user_id
            flask_session["user_name"] = user.user_name

            user.update(session=db_session)

        # Return the response
        return Response("Successfully logged in", HTTPStatus.OK)
