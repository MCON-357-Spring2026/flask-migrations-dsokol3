import os
from flask import Flask

from .config import Config, DATA_DIR
from .extensions import db, migrate
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(DATA_DIR, exist_ok=True)

    # TODO 1:
    # Initialize the SQLAlchemy extension with the app.
    db.init_app(app)

    # TODO 2:
    # Initialize Flask-Migrate with the app and database.
    migrate.init_app(app, db)

    #Note the url_prefix -> all the routes associated with this blueprint will start with /exercises
    app.register_blueprint(api, url_prefix="/exercises")

    return app