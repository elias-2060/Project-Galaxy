from flask_cors import cross_origin
from flask_restx import Namespace

race_desc = """
Race information
"""

api: Namespace = Namespace(
    "race",
    race_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        )
    ],
)

# load routes
import backend.api.race.all
import backend.api.race.chat
import backend.api.race.race
