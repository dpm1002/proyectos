from flask import Blueprint, render_template, request, redirect, url_for
import requests
from app import db
from app.models import Book, Manga

bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/searchBOOK", methods=["POST"])
def searchBook():
    query = request.form.get("query")
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}")
    books = response.json().get("items", [])
    return render_template("results.html", books=books)

@bp.route("/searchMANGA", methods=["POST"])
def searchManga():
    if request.method == "POST":
        query = request.form.get("query")
        results = search_manga(query)
        return render_template("manga_results.html", mangas=results)
    return render_template("manga_search.html")

    

def search_manga(query):
    url = f"https://api.jikan.moe/v4/manga"
    params = {"q": query, "limit": 10}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json().get("data", [])
        return [
            {
                "id": manga.get("mal_id"),
                "title": manga.get("title", "Título desconocido"),
                "description": manga.get("synopsis", "Sin descripción disponible"),
                "image_url": (
                    manga.get("images", {}).get("jpg", {}).get("image_url")
                    if manga.get("images") and manga.get("images").get("jpg")
                    else "/static/no_image.png"
                ),
                "year": (
                    manga.get("published", {}).get("from", "").split("-")[0]
                    if manga.get("published") and manga.get("published").get("from")
                    else "Desconocido"
                ),
                "content_rating": manga.get("rating", "Desconocido"),
            }
            for manga in data
        ]
    else:
        print(f"Error al conectar con Jikan API: {response.status_code}")
        return []

    
@bp.route("/add_manga", methods=["POST"])
def add_manga():
    manga_data = request.form

    # Verificar si el manga ya existe en la base de datos
    existing_manga = Manga.query.get(manga_data["id"])
    if existing_manga:
        print(f"Manga ya existe en la base de datos: {existing_manga.title}")
        return redirect(url_for("routes.library"))

    try:
        # Crear un nuevo objeto Manga si no existe
        manga = Manga(
            id=manga_data["id"],
            title=manga_data["title"],
            description=manga_data.get("description", ""),
            original_language="ja",  # Idioma predeterminado
            year=manga_data.get("year"),
            content_rating=manga_data.get("content_rating", "safe"),
            image_url=manga_data.get("image_url", ""),
        )
        db.session.add(manga)
        db.session.commit()
        print(f"Manga guardado: {manga.title}")
    except Exception as e:
        print(f"Error al guardar el manga: {e}")
        db.session.rollback()  # Revertir la transacción en caso de error

    return redirect(url_for("routes.library"))



@bp.route("/add_book", methods=["POST"])
def add_book():
    book_data = request.form
    book = Book(
        title=book_data["title"],
        author=book_data["author"],
        series=book_data.get("series"),
        published_date=book_data.get("published_date"),
        description=book_data.get("description"),
        image_url=book_data.get("image_url")
    )
    db.session.add(book)
    db.session.commit()
    return redirect(url_for("routes.library"))

@bp.route("/library")
def library():
    books = Book.query.all()
    mangas = Manga.query.all()
    return render_template("library.html", books=books, mangas=mangas)

@bp.route("/libros")
def libros():
    return render_template("libros.html")

@bp.route("/manga")
def manga():
    return render_template("manga.html")
