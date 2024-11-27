from app import create_app, db  # Asegúrate de que create_app está correctamente definido
from app.models import Book, Manga  # Importa tus modelos si es necesario

# Crea la aplicación Flask
app = create_app()

# Ejecuta las operaciones dentro del contexto de la aplicación
with app.app_context():
    db.create_all()
    print("Base de datos inicializada con éxito.")
