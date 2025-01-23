from flask import Flask
from google.cloud import firestore
from app.routes.pantalla_inicio import inicio_bp
from app.routes.ejercicios import ejercicios_bp
from app.routes.finanzas import finanzas_bp
from app.routes.games import games_bp
from app.routes.library import library_bp
from app.routes.libros import books_bp
from app.routes.manga import manga_bp
from app.routes.spotify import spotify_bp
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

    # Registra el inicio
    app.register_blueprint(inicio_bp)

    # Registra los Blueprints
    app.register_blueprint(ejercicios_bp, url_prefix="/ejercicios")
    app.register_blueprint(finanzas_bp, url_prefix="/finanzas")
    app.register_blueprint(games_bp, url_prefix="/games")
    app.register_blueprint(library_bp, url_prefix="/library")
    app.register_blueprint(books_bp, url_prefix="/libros")
    app.register_blueprint(manga_bp, url_prefix="/manga")
    app.register_blueprint(spotify_bp, url_prefix="/spotify")

    return app
