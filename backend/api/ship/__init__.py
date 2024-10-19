from flask_cors import cross_origin
from flask_restx import Namespace

settlement_desc = """
Ship information
"""

api: Namespace = Namespace(
    "ship",
    settlement_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        )
    ],
)

# load routes
import backend.api.ship.spaceship
