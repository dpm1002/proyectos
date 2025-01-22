from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave_por_defecto_segura")
    # Configuración de Firebase
    cred = credentials.Certificate('./credentials/credenciales.json')
    firebase_admin.initialize_app(cred)
    app.firestore_db = firestore.client()

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
