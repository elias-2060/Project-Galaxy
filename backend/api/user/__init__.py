from flask_cors import cross_origin
from flask_restx import Namespace

user_desc = """
User information
"""

api: Namespace = Namespace(
    "user",
    user_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        )
    ],
)

# load routes
import backend.api.user.user
