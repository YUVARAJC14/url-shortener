from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    from app import models

    from app.auth import bp as auth_bp
    from app.links import bp as links_bp
    from app.main import bp as main_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(links_bp, url_prefix="/links")
    app.register_blueprint(main_bp)

    @app.errorhandler(429)
    def too_many(e):
        return "Too many requests. Please wait a minute and try again.", 429
    def not_found(e):
        return render_template("404.html"), 404
    @app.errorhandler(410)
    def gone(e):
        return render_template("410.html"), 410
    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return "Something went wrong on our side. Please try again.", 500
    with app.app_context():
        db.create_all()

    return app