from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.routes.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)

    from app.routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from app.routes.metas import metas as metas_blueprint
    app.register_blueprint(metas_blueprint)

    from app.routes.relatorios import relatorios as relatorios_blueprint
    app.register_blueprint(relatorios_blueprint)

    return app

