import os
import secrets
from dotenv import load_dotenv
from datetime import timedelta
import firebase_admin
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from firebase_admin import credentials

# Blueprints
from handlers.auth_handler import auth_blueprint

def create_app():
    app = Flask(__name__)
    load_dotenv()
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    #Handle Cors
    CORS(app=app, supports_credentials=True)

    app.secret_key = secrets.token_hex(32)
    # JWT Configuration
    app.secret_key = secrets.token_hex(32)
    app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(64)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(weeks=1)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['SESSION_COOKIE_AGE'] = timedelta(weeks=1)

    # Firebase configurations
    cred_path = os.path.join(os.path.dirname(__file__), 'firebase_credentials.json')
    if not firebase_admin._apps:
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    JWTManager(app=app)

    # Regsiter blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv("FLASK_RUN_PORT", 8080))
    app.run(port=port)