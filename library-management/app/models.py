from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100))
    published_date = db.Column(db.String(20))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    # Para el usuario
    user_rating = db.Column(db.Float, nullable=True)  # Valoración del usuario
    user_description = db.Column(db.Text, nullable=True)  # Descripción personalizada
    status = db.Column(db.String(20), nullable=True)  # Estado

class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    original_language = db.Column(db.String(10), nullable=True, default="ja")
    year = db.Column(db.String(4), nullable=True)
    content_rating = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    # Para el usuario
    user_rating = db.Column(db.Float, nullable=True)  # Valoración del usuario
    user_description = db.Column(db.Text, nullable=True)  # Descripción personalizada
    status = db.Column(db.String(20), nullable=True)  # Estado

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID de RAWG
    title = db.Column(db.String(200), nullable=False)
    released = db.Column(db.String(20), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    # Para el usuario
    user_rating = db.Column(db.Float, nullable=True)  # Valoración del usuario
    user_description = db.Column(db.Text, nullable=True)  # Descripción personalizada
    status = db.Column(db.String(20), nullable=True)  # Estado


    def __repr__(self):
        return f"<Manga {self.title}>"
