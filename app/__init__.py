from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.fx_routes import fx_bp
    app.register_blueprint(fx_bp, url_prefix='/api/v1')

    # Create tables
    with app.app_context():
        db.create_all()

    return app