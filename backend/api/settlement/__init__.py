from flask_cors import cross_origin
from flask_restx import Namespace

settlement_desc = """
Settlement information
"""

api: Namespace = Namespace(
    "settlement",
    settlement_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        )
    ],
)

# load routes
import backend.api.settlement.building
import backend.api.settlement.settlement
