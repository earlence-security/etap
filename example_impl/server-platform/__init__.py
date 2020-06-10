from flask import Flask
import os, logging


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'platform.sqlite'),
    )

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from .server import bp
    app.register_blueprint(bp)

    return app

