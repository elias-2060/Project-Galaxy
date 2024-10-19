from backend.api.account import api as account_ns
from backend.api.achievement import api as achievemnt_ns
from backend.api.building import api as building_ns
from backend.api.planet import api as planet_ns
from backend.api.race import api as race_ns
from backend.api.settlement import api as settlement_ns
from backend.api.user import api as user_ns
from backend.api.combat import api as combat_ns
from backend.api.ship import api as ship_ns
from flask import Blueprint, make_response
from flask_restx import Api

api_desc: str = """
Backend API for Project Galaxy.
"""

api_bp = Blueprint("api_v1", __name__, url_prefix="/api")
api: Api = Api(
    app=api_bp,
    version="1.0",
    title="Project Galaxy API",
    description=api_desc,
    doc="/",
)

# add namespaces
api.add_namespace(account_ns)
api.add_namespace(achievemnt_ns)
api.add_namespace(building_ns)
api.add_namespace(planet_ns)
api.add_namespace(race_ns)
api.add_namespace(settlement_ns)
api.add_namespace(user_ns)
api.add_namespace(combat_ns)
api.add_namespace(ship_ns)

# api catchall
@api_bp.route("", defaults={"endpoint": ""})
@api_bp.route("/<path:endpoint>")
def api_catchall(endpoint: str):
    return make_response(
        f"<html><h1><center>404</center></h1><center>/api/{endpoint} does not exist</center>" f"</html>", 404
    )
