from http import HTTPStatus
from backend.api.building import api
from backend.api.building.building import building_model, building_parser
from backend.api.planet.planet import planet_model
from backend.game_classes import Planet, User, Settlement, Warper, Building
from database.database_access import DefaultSession
from flask import request, session as flask_session
from flask_restx import Resource, fields, marshal

# Planet model with the owner's username
planet_user_name_model = api.clone(
    'PlanetUserName',
    planet_model,
    {
        "user_name": fields.String(
            description="Username of the planet owner",
            required=True,
            attribute=lambda b: b.user.user_name
        ),
    }
)


# If there is no link, get the linkable planets
warper_unlinked_model = api.clone(
    "WarperInfo",
    building_model,
    {
        "linkable_planets": fields.List(
            fields.Nested(planet_user_name_model),
            description="Possible Warp Locations",
            required=True,
            attribute=lambda b: b.get_possible_warp_locations()
        ),
    },
)

# If the warper has a link, don't get the linkable planets
warper_linked_model = api.clone(
    "BuildingWithLinkInfo",
    building_model,
    {
        "current_warp_to": fields.Nested(
            planet_model,
            description="Current Warp Location",
            attribute=lambda b: b.get_warp_to()
        ),
    }
)


@api.route("/warper")
class WarperRes(Resource):
    @api.expect(building_parser)
    @api.response(HTTPStatus.OK, "Successfully got warp locations", warper_unlinked_model)
    @api.response(HTTPStatus.UNAUTHORIZED, "Not logged in")
    @api.response(HTTPStatus.BAD_REQUEST, "Invalid planet number")
    def get(self):
        """
        Gets the warp locations the planet can set up a warp to.
        """
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            return api.abort(HTTPStatus.UNAUTHORIZED, "Not logged in")

        data = building_parser.parse_args(request)

        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            user.update()

            planet: Planet = user.planets[data["planet_number"]]
            settlement: Settlement = planet.settlements[data["settlement_number"]]

            settlement_grid = settlement.get_grid(False)

            warper: Building = settlement_grid[data["pos_x"]][data["pos_y"]]

            if not isinstance(warper, Warper):
                api.abort(HTTPStatus.BAD_REQUEST, "Requested building is not a warper")

            # If the warper has a link, get that link
            if warper.planet_link is None:
                return marshal(warper, warper_unlinked_model)

            # Else, get the list of linkable planets
            else:
                return marshal(warper, warper_linked_model)
