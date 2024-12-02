from flask import Blueprint, render_template, request, redirect, url_for
import requests
from app import db
from app.models import Book, Manga, Game
from dotenv import load_dotenv
from flask import session
import os

load_dotenv()

bp = Blueprint('routes', __name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/spotify/login")
def spotify_login():
    scope = "user-read-playback-state user-modify-playback-state playlist-modify-private playlist-read-private user-read-email"
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?response_type=code"
        f"&client_id={SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(auth_url)

@bp.route("/spotify/callback")
def spotify_callback():
    code = request.args.get("code")
    token_response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        },
    )
    tokens = token_response.json()
    session["access_token"] = tokens.get("access_token")
    return redirect(url_for("routes.spotify_player"))


@bp.route("/spotify/player")
def spotify_player():
    access_token = session.get("access_token")
    if not access_token:
        return "No access token available. Please log in again.", 401

    headers = {"Authorization": f"Bearer {access_token}"}

    # Obtener información del perfil
    profile_response = requests.get(f"{SPOTIFY_API_URL}/me", headers=headers)
    profile_data = profile_response.json() if profile_response.status_code == 200 else None
    print("Perfil del usuario:", profile_data)  # Verificar la respuesta en los logs

    # Obtener listas de reproducción
    playlists_response = requests.get(f"{SPOTIFY_API_URL}/me/playlists", headers=headers)
    playlists_data = playlists_response.json().get("items", []) if playlists_response.status_code == 200 else []
    print("Listas de reproducción:", playlists_data)  # Verificar la respuesta en los logs

    # Si no hay datos en el perfil o playlists, devuelve un mensaje
    if not profile_data:
        return "No se pudo obtener el perfil del usuario. Por favor, inicia sesión nuevamente.", 500
    if not playlists_data:
        return "No se encontraron listas de reproducción. Por favor, verifica tu cuenta de Spotify.", 500

    # Pasar los datos al template
    return render_template("spotify_player.html", profile=profile_data, playlists=playlists_data, access_token=access_token)



@bp.route("/search_game", methods=["GET", "POST"])
def search_game():
    if request.method == "POST":
        query = request.form.get("query")
        api_key = "9422c4d6ee1c4a90b9e87e170f5f2aac"  # Reemplaza con tu clave de RAWG
        url = f"https://api.rawg.io/api/games"
        params = {
            "key": api_key,
            "search": query,
            "page_size": 50,  # Limita los resultados
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            games = response.json().get("results", [])
            return render_template("game_results.html", games=games)
        else:
            return f"Error al conectar con la API de RAWG: {response.status_code}", 500
    return render_template("game_search.html")


@bp.route("/searchBOOK", methods=["POST"])
def searchBook():
    query = request.form.get("query")  # Texto de búsqueda
    filter_categories = request.form.getlist("filter_category")  # Géneros seleccionados (lista)

    if not query and not filter_categories:
        return "Debe proporcionar un término de búsqueda o seleccionar al menos un género.", 400

    # Base de la URL
    url = "https://www.googleapis.com/books/v1/volumes?q="

    # Construcción de la consulta de texto
    if query:
        url += query

    # Construcción de la consulta de géneros (OR lógico)
    if filter_categories:
        if query:
            url += "+"
        url += "+subject:" + "+OR+subject:".join(filter_categories)

    try:
        response = requests.get(url)
        response.raise_for_status()
        books = response.json().get("items", [])
        return render_template("results.html", books=books)
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de Google Books: {e}")
        return f"Error al conectar con la API de Google Books: {e}", 500




@bp.route("/book/<int:book_id>/update_genres", methods=["POST"])
def update_book_genres(book_id):
    book = Book.query.get_or_404(book_id)
    book.genres = request.form.get("genres")
    db.session.commit()
    return redirect(url_for("routes.book_details", book_id=book_id))


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
    
@bp.route("/add_game", methods=["POST"])
def add_game():
    game_data = request.form

    # Verificar si el juego ya existe
    existing_game = Game.query.get(game_data["id"])
    if existing_game:
        print(f"El juego ya existe en la base de datos: {existing_game.title}")
        return redirect(url_for("routes.library"))

    try:
        # Crear un nuevo objeto Game
        game = Game(
            id=game_data["id"],
            title=game_data["title"],
            released=game_data.get("released"),
            rating=game_data.get("rating"),
            image_url=game_data.get("image_url"),
        )
        db.session.add(game)
        db.session.commit()
        print(f"Juego guardado: {game.title}")
    except Exception as e:
        print(f"Error al guardar el juego: {e}")
        db.session.rollback()

    return redirect(url_for("routes.library"))

@bp.route("/game/<int:game_id>")
def game_details(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template("game_details.html", game=game)

@bp.route("/game/<int:game_id>/update", methods=["POST"])
def update_game(game_id):
    game = Game.query.get_or_404(game_id)
    game.user_rating = request.form.get("user_rating", type=float)
    game.user_description = request.form.get("user_description")
    game.status = request.form.get("status")
    db.session.commit()
    return redirect(url_for("routes.game_details", game_id=game_id))

    
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

@bp.route("/manga/<int:manga_id>/update", methods=["POST"])
def update_manga(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    manga.user_rating = request.form.get("user_rating", type=float)
    manga.user_description = request.form.get("user_description")
    manga.status = request.form.get("status")
    db.session.commit()
    return redirect(url_for("routes.manga_details", manga_id=manga_id))




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

@bp.route("/book/<int:book_id>/update", methods=["POST"])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.user_rating = request.form.get("user_rating", type=float)
    book.user_description = request.form.get("user_description")
    book.status = request.form.get("status")
    db.session.commit()
    return redirect(url_for("routes.book_details", book_id=book_id))



@bp.route("/book/<int:book_id>")
def book_details(book_id):
    # Obtener el libro de la base de datos
    book = Book.query.get_or_404(book_id)
    return render_template("book_details.html", book=book)

@bp.route("/manga/<int:manga_id>")
def manga_details(manga_id):
    # Obtener el manga de la base de datos
    manga = Manga.query.get_or_404(manga_id)
    return render_template("manga_details.html", manga=manga)


@bp.route("/library")
def library():
    books = Book.query.all()
    mangas = Manga.query.all()
    games = Game.query.all()
    return render_template("library.html", books=books, mangas=mangas, games=games)

@bp.route("/get_categories", methods=["GET"])
def get_categories():
    url = "https://www.googleapis.com/books/v1/volumes?q=science"
    response = requests.get(url)
    categories = set()

    if response.status_code == 200:
        books = response.json().get("items", [])
        for book in books:
            categories.update(book.get("volumeInfo", {}).get("categories", []))
    
    return {"categories": list(categories)}


@bp.route("/libros")
def libros():
    return render_template("libros.html")

@bp.route("/manga")
def manga():
    return render_template("manga.html")

@bp.route("/games")
def games():
    return render_template("games.html")
