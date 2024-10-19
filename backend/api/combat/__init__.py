from flask_cors import cross_origin
from flask_restx import Namespace

combat_desc = """
Planet information
"""

api: Namespace = Namespace(
    "combat",
    combat_desc,
    decorators=[
        cross_origin(
            supports_credentials=True,
            origin="http://localhost:5173",
        )
    ],
)

# load routes
import backend.api.combat.load_enemy
import backend.api.combat.load_attack_data
import backend.api.combat.play_round
