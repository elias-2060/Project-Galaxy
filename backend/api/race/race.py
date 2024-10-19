from http import HTTPStatus

from backend.api.race import api
from backend.game_classes import Race, User
from database.database_access import DefaultSession
from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource, fields, inputs, marshal

member_model = api.model(
    "RaceMember",
    {
        "user_id": fields.String(description="ID of the member", required=True),
        "user_name": fields.String(description="Name of the member", required=True),
    },
)


race_model = api.model(
    "RaceInfo",
    {
        "race_id": fields.String(description="ID of the race", required=True),
        "race_name": fields.String(description="Name of the race", required=True),
        "leader": fields.String(
            description="Name of the leader", required=True, attribute=lambda r: r.leader.user_name
        ),
        "leader_id": fields.String(description="ID of the leader", required=True),
    },
)
race_model_with_members = api.clone(
    "RaceInfoWithMembers",
    race_model,
    {
        "members": fields.List(
            fields.Nested(member_model), description="List of members", attribute=lambda r: r.members
        ),
    },
)


get_race_parser = api.parser().add_argument("include_members", type=inputs.boolean)
post_race_parser = (
    api.parser()
    .add_argument("race_name", type=str, required=True)
    .add_argument("no_join", type=inputs.boolean)
    .add_argument("no_create", type=inputs.boolean)
)
delete_race_parser = (
    api.parser().add_argument("no_leave", type=inputs.boolean).add_argument("no_delete", type=inputs.boolean)
)


@api.route("")
class Members(Resource):
    @api.expect(get_race_parser)
    @api.response(HTTPStatus.OK, "Race information", race_model)
    @api.response(HTTPStatus.OK, "Race information with members list", race_model_with_members)
    @api.response(HTTPStatus.NOT_FOUND, "User not in race")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def get(self):
        """
        Get race information.
        Optionally include list of members.
        """
        data = get_race_parser.parse_args(request)
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            race: Race | None = user.race
            if race is None:
                return Response("User not in race")

            if data.get("include_members", None):
                return marshal(race, race_model_with_members)
            return marshal(race, race_model)

    @api.expect(post_race_parser)
    @api.response(HTTPStatus.OK, "Created race")
    @api.response(HTTPStatus.OK, "Joined race")
    @api.response(HTTPStatus.CONFLICT, "User already in race")
    @api.response(HTTPStatus.CONFLICT, "No race to join exists")
    @api.response(HTTPStatus.CONFLICT, "Race with same name already exists")
    def post(self):
        """
        Join or create a race.
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = post_race_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            if user.race is not None:
                api.abort(HTTPStatus.CONFLICT, "User already in race")

            race: Race | None = Race.load(data["race_name"], session=session)

            if race is None:  # creating a race
                if data["no_create"]:
                    api.abort(HTTPStatus.CONFLICT, "No race to join exists")
                race = Race(race_name=data["race_name"], leader_id=user.user_id)
                session.add(race)
                race.members.append(user)
                session.commit()
                resp = "Created race"
            else:  # joining a race
                if data["no_join"]:
                    api.abort(HTTPStatus.CONFLICT, "Race with same name already exists")
                race.members.append(user)
                session.commit()
                resp = "Joined race"

            return Response(resp, HTTPStatus.OK)

    @api.expect(delete_race_parser)
    @api.response(HTTPStatus.OK, "Deleted race")
    @api.response(HTTPStatus.OK, "Left race")
    @api.response(HTTPStatus.NOT_FOUND, "User not in race")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    @api.response(HTTPStatus.CONFLICT, "Not allowed to delete race but user is the leader")
    @api.response(HTTPStatus.CONFLICT, "Not allowed to leave race but user is not the leader")
    def delete(self):
        """
        Leave or delete the race.
        If the user is the leader, delete the race.
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = delete_race_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            if user.race is None:
                api.abort(HTTPStatus.NOT_FOUND, "User not in race")

            if user.race.leader_id == user.user_id:
                if data["no_delete"]:
                    api.abort(HTTPStatus.CONFLICT, "Not allowed to delete race but user is the leader")
                session.delete(user.race)
                user.race = None
                resp = "Deleted race"
            elif data["no_leave"]:
                api.abort(HTTPStatus.CONFLICT, "Not allowed to leave race but user is not the leader")
            else:
                user.race = None
                resp = "Left race"

            session.commit()
            return Response(resp, HTTPStatus.OK)
