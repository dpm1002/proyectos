# init_db.py
from app import create_app, db  # Asegúrate de que create_app() y db estén disponibles
from app.models import Book, Manga, Game, Transaction  # <--- Importa todos los modelos, incluyendo Transaction

app = create_app()

with app.app_context():
    db.create_all()
    print("Base de datos inicializada con éxito.")
