from http import HTTPStatus

from backend.api.account import active_users, api
from backend.game_classes import Planet, Settlement, TownHall, User
from backend.game_classes.General import add_user, check_password
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource, fields

register_model = api.model(
    "RegisterInfo",
    {
        "user_name": fields.String(description="Name of user", example="John", required=True),
        "password": fields.String(description="Password of the user", example="5aBG2Th", required=True),
        "planet_name": fields.String(description="Name of first planet", example="Johnville", required=True),
    },
)

register_parser = (
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
    .add_argument(
        "planet_name",
        type=str,
        required=True,
        trim=True,
        help="Expected name of starting planet. Encountered error {error_msg}",
    )
)


@api.route("/register")
class Register(Resource):
    @api.expect(register_model)
    @api.response(HTTPStatus.OK, "Successfully logged in")
    @api.response(HTTPStatus.BAD_REQUEST, "Missing fields")
    @api.response(HTTPStatus.BAD_REQUEST, "Password is not strong enough")
    def post(self):
        """
        Adds a user to the database
        """

        data = register_parser.parse_args(request)

        # if data["username"] == "" or data["password"] == "":
        #     return Response("Missing fields", HTTPStatus.BAD_REQUEST)

        if check_password(data["password"]) != "correct":
            return Response("Password is not strong enough!", HTTPStatus.BAD_REQUEST)

        # Insert this value into table User and get the result string
        result: str = add_user(data["user_name"], data["password"])

        if result == "Successfully added user":
            with DefaultSession(autoflush=False) as db_session:
                user = User.load_by_name(data["user_name"], session=db_session)

                all_planets = Planet.get_all_planets_coordinates(session=db_session)

                planet_coordinate = Planet.generateNewPlanetCoordinates(all_planets)

                planet: Planet = Planet(
                    user_id=user.user_id,
                    planet_x=planet_coordinate[0],
                    planet_y=planet_coordinate[1],
                    name=data["planet_name"],
                )

                user.add_planet(planet, session=db_session)

                settlement: Settlement = Settlement(0, planet.planet_id)
                planet.add_settlement(settlement, session=db_session)

                town_hall = TownHall(settlement_id=settlement.settlement_id, grid_pos_x=2, grid_pos_y=2)

                settlement.build(town_hall, session=db_session)

                user.update(session=db_session)

                db_session.commit()

                """
                this does not work yet, but this is how i want to immediately log in the user after registering.
                Problem: i can't get the credentials in the request.

                # The URL of the login endpoint
                url = "http://localhost:8080/api/login"

                # The data to be sent in the request body
                data = {
                    "Username": data['Username'],
                    "Password": data['Password']
                }

                # Send the POST request to the login endpoint
                response = requests.post(url, json=data)

                return Response(response)
                """
                active_users[user.user_id] = user

                flask_session["user_id"] = user.user_id
                flask_session["user_name"] = user.user_name

                user.update(session=db_session)

                return Response("Successfully logged in", HTTPStatus.OK)

        return Response(result, HTTPStatus.BAD_REQUEST)
