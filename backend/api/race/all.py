from http import HTTPStatus

from backend.api.race import api
from backend.game_classes import Race
from database.database_access import DefaultSession
from flask_restx import Resource, fields, marshal

race_model = api.model(
    "RaceInfo",
    {
        "race_name": fields.String(description="Name of the race", required=True),
        "race_id": fields.String(description="ID of the race", required=True),
        "leaer": fields.String(description="Name of the leader", required=True, attribute=lambda r: r.leader.user_name),
        "leader_id": fields.String(description="ID of the leader", required=True),
    },
)


@api.route("/all")
class All(Resource):
    @api.response(HTTPStatus.OK, "Race information", [race_model])
    def get(self):
        """
        Show all races.
        """
        with DefaultSession() as session:
            races: list[Race] = session.query(Race).all()
            return marshal(races, race_model)
