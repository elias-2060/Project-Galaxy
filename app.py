import json
import os

import type_enforced
from dotenv import load_dotenv
from flask import Flask, Response, make_response, request, send_from_directory, session
from flask_cors import CORS, cross_origin
from flask_restx import reqparse
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from backend.api import api_bp

from backend.game_classes import Achievement, SetupState
from database.config import config_data
from database.database_access import DefaultSession, db_url

load_dotenv()

ADDR: str = os.environ.get("ADDR") or "127.0.0.1"
""" Address to listen on, defaults to localhost if no env variable set. """

PORT: int = os.environ.get("PORT") or 8080
""" Port to listen on, defaults to 8080 if no env variable set. """

DEBUG: bool = os.environ.get("DEBUG") is not None
""" Debug state, defaults to True if no env variable set. """

# Making a Flask app using the library
app = Flask(
    "project-galaxy",
    template_folder="frontend/templates",
    static_folder="frontend/project-galaxy-front/dist",
)

# Set the secret key to the secret key in the environment variables
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Set the session type to redis and the redis url to the local redis server
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SESSION_TYPE"] = "sqlalchemy"

db = SQLAlchemy(app)

app.config["SESSION_SQLALCHEMY"] = db

# Set the session to the app
Session(app)

# Enable Cross-Origin Resource Sharing
CORS(app, origins=["http://localhost:5173/"], resources={r"/": {"origins": ""}}, supports_credentials=True)

# add all api routes
app.config["RESTX_MASK_SWAGGER"] = False
app.register_blueprint(api_bp)

# Deel code voor de tijdelijke homepage
app_data = dict()
app_data["app_name"] = config_data["app_name"]


# handle main page visits/game_classes asset requests
@type_enforced.Enforcer
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def root(path: str):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        res: Response = send_from_directory(app.static_folder, path)
    else:
        res: Response = send_from_directory(app.static_folder, "index.html")
    return res


with app.app_context():
    with DefaultSession(autoflush=True) as session:
        setup_state = SetupState.load(session)
        if setup_state is None:
            print("Creating setup state")
            setup_state = SetupState(
                achievements_created=True,
            )
            Achievement.populate(session)
            session.add(setup_state)
        elif not setup_state.achievements_created:
            print("Creating achievements")
            setup_state.achievements_created = True
            Achievement.populate(session)
        session.commit()


# Main function
if __name__ == "__main__":
    app.run(ADDR, PORT, DEBUG)
