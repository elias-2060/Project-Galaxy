"""
API routes specific to colony ships.
"""

from backend.game_classes.Planet import Planet
from backend.game_classes.User import User
from database.config import config_data
from flask import Blueprint, Response, render_template, request

route = "/api/colony_ship"

# create a blueprint for the '/api/colony_ship/' endpoints
colony_ship_bp = Blueprint(route, __name__)


@colony_ship_bp.route(f"{route}/create_colony", methods=["POST"])
def api__colony_ship__create_colony() -> Response:
    """Create a new colony with a colony ship."""
    return Response("unimplemented", 404)
