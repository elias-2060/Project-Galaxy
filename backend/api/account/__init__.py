from backend.game_classes import User
from flask_cors import cross_origin
from flask_restx import Namespace

account_desc = """
Manage account status
"""

api: Namespace = Namespace(
    "account",
    account_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        )
    ],
)

# Active users right now, key being the user_id and the value being a Player
active_users: dict[int, User] = {}

# load routes
import backend.api.account.login
import backend.api.account.logout
import backend.api.account.register
