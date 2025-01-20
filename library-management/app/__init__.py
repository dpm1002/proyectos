from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore


def create_app():
    app = Flask(__name__)

    # Configuración de Firebase
    cred = credentials.Certificate('./.gitignore/credenciales.json')
    firebase_admin.initialize_app(cred)
    app.firestore_db = firestore.client()

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
