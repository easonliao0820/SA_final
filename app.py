import os
from flask import Flask
from extensions import db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'boardgame-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'sqlite:///{os.path.join(BASE_DIR, "boardgame.db")}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'image')

    db.init_app(app)

    from routes.public import public_bp
    from routes.admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    return app
