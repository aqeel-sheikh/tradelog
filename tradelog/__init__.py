"""
Application factory and blueprint registration for the TradeLog app.
"""
import logging
from flask import Flask
from .config import Config
from .extensions import db, bcrypt, login_manager
from .models import User
from .errors.handlers import register_error_handlers

def create_app(config_name=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .main.routes import main
    from .auth.routes import auth
    from .trading.routes import trading
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(trading)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app
