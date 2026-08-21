import os

from flask import Flask

from .routes import main_blueprint


def create_app():
    """Create and configure the Flask application instance."""
    base_dir = os.path.dirname(__file__)
    template_folder = os.path.abspath(os.path.join(base_dir, '..', 'templates'))
    static_folder = os.path.abspath(os.path.join(base_dir, '..', 'static'))

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.register_blueprint(main_blueprint)
    app.CURRENT = {
        'puzzle': None,
        'solution': None,
    }
    return app
