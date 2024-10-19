from flask_cors import cross_origin
from flask_restx import Namespace

planet_desc = """
Planet information
"""

api: Namespace = Namespace(
    "planet",
    planet_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        )
    ],
)

# load routes
import backend.api.planet.all
import backend.api.planet.opponent
import backend.api.planet.buy_list
import backend.api.planet.planet
import backend.api.planet.settlement