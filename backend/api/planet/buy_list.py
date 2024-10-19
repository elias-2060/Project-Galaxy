import json
from http import HTTPStatus

from backend.api.planet import api
from backend.game_classes import Planet
from database.database_access import DefaultSession
from flask import Response
from flask_restx import Resource, fields

buy_list_model = api.model(
    "BuyList",
    {
        "coordinates": fields.List(
            fields.List(
                fields.Integer(description="Coordinate of the planet", example=5495),
                description="X and Y coordinates of the planets",
                example=[5495, 1232],
            ),
            description="List of coordinates",
            example=[
                [5495, 1232],
                [2588, 5953],
                [5283, 2963],
                [4620, 7088],
                [2218, 7655],
                [6579, 3916],
                [3884, 8881],
                [5622, 10104],
                [5618, 12074],
                [6627, 7490],
            ],
        )
    },
)


@api.route("/buy_list", methods=["GET"])  # TODO
class BuyList(Resource):
    @api.response(HTTPStatus.OK, "Success", buy_list_model)
    def get(self):
        """
        Gets the coordinates of the planets.
        """
        with DefaultSession() as BaseSession:
            planets = Planet.get_all_planets_coordinates(session=BaseSession)
            planet_coords: list[tuple[int, int]] = [(planet[0], planet[1]) for planet in planets]
            new_coords = []

            for i in range(10):
                new_coord = Planet.generateNewPlanetCoordinates(planet_coords)
                planets.append(new_coord)
                new_coords.append(new_coord)

            resp = {"coordinates": new_coords}

            return Response(json.dumps(resp), mimetype="application/json")
