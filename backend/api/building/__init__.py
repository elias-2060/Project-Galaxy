from flask_cors import cross_origin
from flask_restx import Namespace

building_desc = """
Manage building status
"""

api: Namespace = Namespace(
    "building",
    building_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        ),
    ],
)

# load routes
import backend.api.building.barrack
import backend.api.building.warper
import backend.api.building.building
import backend.api.building.production
import backend.api.building.upgrade
import backend.api.building.spaceport
