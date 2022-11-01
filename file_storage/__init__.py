import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        STORAGE=os.path.join(app.instance_path, 'store'),
        DATABASE=os.path.join(app.instance_path, 'app.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['STORAGE'])
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import file_storage
    app.register_blueprint(file_storage.bp)

    @app.route('/')
    def index():
        return "Hello!"

    return app
