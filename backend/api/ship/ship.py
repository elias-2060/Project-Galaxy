"""
API routes common for all ship types.
"""

from backend.game_classes.Planet import Planet
from backend.game_classes.User import User
from database.config import config_data
from database.database_access import DefaultSession
from flask import Blueprint, Response, render_template, request

route = "/api/ship"

# create a blueprint for the '/api/ship/' endpoints
ship_bp = Blueprint(route, __name__)


@ship_bp.route(f"{route}/create", methods=["POST"])
def create() -> Response:
    """Create a new ship."""
    with DefaultSession(autoflush=False) as session:
        ...
        return Response("unimplemented", 404)


@ship_bp.route(f"{route}/delete", methods=["POST"])
def api__ship__delete() -> Response:
    """Delete a ship."""
    with DefaultSession(autoflush=False) as session:
        ...
        return Response("unimplemented", 404)


@ship_bp.route(f"{route}/move", methods=["POST"])
def api__ship__move() -> Response:
    """Move a ship to a different planet."""
    with DefaultSession(autoflush=False) as session:
        ...
        return Response("unimplemented", 404)


@ship_bp.route(f"{route}/land", methods=["POST"])
def api__ship__land() -> Response:
    """Make a ship land at a spaceport."""
    with DefaultSession(autoflush=False) as session:
        ...
        return Response("unimplemented", 404)


@ship_bp.route(f"{route}/takeoff", methods=["POST"])
def api__ship__takeoff() -> Response:
    """Make a ship take off from it's spaceport."""
    with DefaultSession(autoflush=False) as session:
        ...
        return Response("unimplemented", 404)


@ship_bp.route(f"{route}/get", methods=["POST"])
def api__ship__get() -> Response:
    """Get information about the ship."""
    with DefaultSession(autoflush=False) as session:
        ...
        return Response("unimplemented", 404)
