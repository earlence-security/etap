from flask import Flask
import logging
import sys

sys.path.insert(0, "/home/ruizhe/oblivtap/")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    from .server import bp
    app.register_blueprint(bp)

    return app

