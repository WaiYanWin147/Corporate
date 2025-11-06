from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object("app.config.Config")
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app.entity.user_profile import UserProfile
        from app.entity.user_account import UserAccount
        from app.entity.category import Category
        from app.entity.request import Request
        from app.entity.shortlist import Shortlist
        from app.entity.match_record import MatchRecord
        from app.entity.report import Report
        db.create_all()
        register_blueprints(app)

    login_manager.login_view = "boundary.login"
    return app

def register_blueprints(app):
    from app.boundary.routes import boundary_bp
    app.register_blueprint(boundary_bp)
