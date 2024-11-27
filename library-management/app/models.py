from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100))
    published_date = db.Column(db.String(20))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))

class Manga(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # ID de MangaDex (UUID)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    original_language = db.Column(db.String(10), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    content_rating = db.Column(db.String(50), nullable=True)  # Ejemplo: "safe", "suggestive", etc.
    image_url = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Manga {self.title}>"
