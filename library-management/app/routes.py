from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
import requests
from datetime import datetime
import os

bp = Blueprint('routes', __name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"


def get_firestore_db():
    from flask import current_app
    return current_app.firestore_db


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/library")
def library():
    db = current_app.firestore_db

    books = [doc.to_dict() for doc in db.collection('books').stream()]
    mangas = [doc.to_dict() for doc in db.collection('mangas').stream()]
    games = [doc.to_dict() for doc in db.collection('games').stream()]

    return render_template("library.html", books=books, mangas=mangas, games=games)


@bp.route("/add_book", methods=["POST"])
def add_book():
    db = current_app.firestore_db
    book_data = request.form

    book_ref = db.collection('books').document()
    book_ref.set({
        'title': book_data["title"],
        'author': book_data["author"],
        'series': book_data.get("series"),
        'published_date': book_data.get("published_date"),
        'description': book_data.get("description"),
        'image_url': book_data.get("image_url")
    })

    return redirect(url_for("routes.library"))


@bp.route("/book/<book_id>/update", methods=["POST"])
def update_book(book_id):
    db = current_app.firestore_db
    if request.is_json:
        book_data = request.json
    else:
        book_data = request.form

    db.collection('books').document(book_id).update({
        'user_rating': float(book_data.get("user_rating", 0)),
        'user_description': book_data.get("user_description"),
        'status': book_data.get("status")
    })

    if request.is_json:
        return jsonify({"success": True}), 200
    return redirect(url_for("routes.book_details", book_id=book_id))


@bp.route("/book/<string:book_id>", methods=["GET", "POST"])
def book_details(book_id):
    db = current_app.firestore_db

    if request.method == "POST":
        user_rating = request.form.get("user_rating")
        user_description = request.form.get("user_description")
        status = request.form.get("status")
        genres = request.form.get("genres")

        db.collection('books').document(book_id).update({
            'user_rating': float(user_rating) if user_rating else None,
            'user_description': user_description,
            'status': status,
            'genres': genres
        })

        return redirect(url_for("routes.book_details", book_id=book_id))

    book_doc = db.collection('books').document(book_id).get()
    if not book_doc.exists:
        return f"El libro con ID {book_id} no existe.", 404

    book = book_doc.to_dict()
    book['id'] = book_id
    return render_template("book_details.html", book=book)


@bp.route("/add_manga", methods=["POST"])
def add_manga():
    db = current_app.firestore_db
    manga_data = request.form

    manga_ref = db.collection('mangas').document()
    manga_ref.set({
        'title': manga_data["title"],
        'description': manga_data.get("description"),
        'original_language': manga_data.get("original_language", "ja"),
        'year': manga_data.get("year"),
        'content_rating': manga_data.get("content_rating", "safe"),
        'image_url': manga_data.get("image_url")
    })

    return redirect(url_for("routes.library"))


@bp.route("/manga/<manga_id>")
def manga_details(manga_id):
    db = get_firestore_db()
    manga = db.collection('mangas').document(manga_id).get().to_dict()
    return render_template("manga_details.html", manga=manga)


@bp.route("/manga/<manga_id>/update", methods=["POST"])
def update_manga(manga_id):
    db = get_firestore_db()
    manga_data = request.form

    db.collection('mangas').document(manga_id).update({
        'user_rating': float(manga_data.get("user_rating", 0)),
        'user_description': manga_data.get("user_description"),
        'status': manga_data.get("status")
    })

    return redirect(url_for("routes.manga_details", manga_id=manga_id))


@bp.route("/add_game", methods=["POST"])
def add_game():
    db = get_firestore_db()
    game_data = request.form

    game_ref = db.collection('games').document()
    game_ref.set({
        'title': game_data["title"],
        'released': game_data.get("released"),
        'rating': game_data.get("rating"),
        'image_url': game_data.get("image_url")
    })

    return redirect(url_for("routes.library"))


@bp.route("/game/<game_id>")
def game_details(game_id):
    db = get_firestore_db()
    game = db.collection('games').document(game_id).get().to_dict()
    return render_template("game_details.html", game=game)


@bp.route("/game/<game_id>/update", methods=["POST"])
def update_game(game_id):
    db = get_firestore_db()
    game_data = request.form

    db.collection('games').document(game_id).update({
        'user_rating': float(game_data.get("user_rating", 0)),
        'user_description': game_data.get("user_description"),
        'status': game_data.get("status")
    })

    return redirect(url_for("routes.game_details", game_id=game_id))


@bp.route("/spotify/login")
def spotify_login():
    scope = "user-read-playback-state user-modify-playback-state playlist-modify-private playlist-read-private user-read-email user-read-recently-played"
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

    profile_response = requests.get(f"{SPOTIFY_API_URL}/me", headers=headers)
    profile_data = profile_response.json() if profile_response.status_code == 200 else None

    playlists_response = requests.get(
        f"{SPOTIFY_API_URL}/me/playlists", headers=headers)
    playlists_data = playlists_response.json().get(
        "items", []) if playlists_response.status_code == 200 else []

    if not profile_data:
        return "No se pudo obtener el perfil del usuario. Por favor, inicia sesión nuevamente.", 500
    if not playlists_data:
        return "No se encontraron listas de reproducción. Por favor, verifica tu cuenta de Spotify.", 500

    return render_template("spotify_player.html", profile=profile_data, playlists=playlists_data, access_token=access_token)


@bp.route("/spotify/stats")
def user_stats():
    access_token = session.get("access_token")
    if not access_token:
        return "No token disponible. Por favor, inicia sesión.", 401

    headers = {"Authorization": f"Bearer {access_token}"}

    response_recently_played = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=50", headers=headers
    )

    response_top_tracks = requests.get(
        "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=50", headers=headers
    )

    tracks_by_month = {}

    if response_recently_played.status_code == 200:
        recently_played = response_recently_played.json().get("items", [])
        for item in recently_played:
            played_at = item["played_at"]
            track = item["track"]
            month = played_at[:7]
            if month not in tracks_by_month:
                tracks_by_month[month] = {}

            track_id = track["id"]
            tracks_by_month[month][track_id] = tracks_by_month[month].get(
                track_id, 0) + 1

    if response_top_tracks.status_code == 200:
        top_tracks = response_top_tracks.json().get("items", [])
        for track in top_tracks:
            album = track.get("album", {})
            release_date = album.get("release_date", "1900-01-01")
            month = release_date[:7]
            if month not in tracks_by_month:
                tracks_by_month[month] = {}

            track_id = track["id"]
            tracks_by_month[month][track_id] = tracks_by_month[month].get(
                track_id, 0) + 1

    sorted_tracks_by_month = {}
    for month, tracks in tracks_by_month.items():
        sorted_tracks = sorted(
            tracks.items(), key=lambda x: x[1], reverse=True
        )[:5]
        sorted_tracks_by_month[month] = sorted_tracks

    detailed_tracks_by_month = {}
    for month, tracks in sorted_tracks_by_month.items():
        detailed_tracks_by_month[month] = []
        for track_id, count in tracks:
            track_response = requests.get(
                f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers
            )
            if track_response.status_code == 200:
                detailed_tracks_by_month[month].append(track_response.json())

    return render_template("spotify_stats.html", tracks_by_month=detailed_tracks_by_month)


@bp.route("/search_game", methods=["GET", "POST"])
def search_game():
    if request.method == "POST":
        query = request.form.get("query")
        api_key = "9422c4d6ee1c4a90b9e87e170f5f2aac"
        url = f"https://api.rawg.io/api/games"
        params = {
            "key": api_key,
            "search": query,
            "page_size": 50,
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
    query = request.form.get("query")
    filter_categories = request.form.getlist("filter_category")

    if not query and not filter_categories:
        return "Debe proporcionar un término de búsqueda o seleccionar al menos un género.", 400

    url = "https://www.googleapis.com/books/v1/volumes?q="

    if query:
        url += query

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


@bp.route("/searchMANGA", methods=["POST"])
def searchManga():
    query = request.form.get("query")
    results = search_manga(query)
    return render_template("manga_results.html", mangas=results)


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


@bp.route("/libros", methods=["GET"])
def libros():
    db = current_app.firestore_db
    books = [doc.to_dict() for doc in db.collection('books').stream()]
    return render_template("libros.html", books=books)


@bp.route("/finanzas", methods=["GET", "POST"])
def finanzas():
    db = current_app.firestore_db

    if request.method == "POST":
        transaction_type = request.form.get("transaction_type")
        category = request.form.get("category")
        amount = float(request.form.get("amount", 0))

        db.collection('transactions').add({
            'transaction_type': transaction_type,
            'category': category,
            'amount': amount,
            'date': datetime.utcnow()
        })

        return redirect(url_for("routes.finanzas"))

    transactions = [doc.to_dict()
                    for doc in db.collection('transactions').stream()]
    return render_template("finanzas.html", transactions=transactions)


@bp.route("/finanzas/grafico")
def finanzas_grafico():
    db = current_app.firestore_db

    transactions = [doc.to_dict()
                    for doc in db.collection('transactions').stream()]
    total_ingresos = sum(t['amount']
                         for t in transactions if t['transaction_type'] == "ingreso")
    total_gastos = sum(t['amount']
                       for t in transactions if t['transaction_type'] == "gasto")
    balance = total_ingresos - total_gastos

    return render_template("finanzas_grafico.html", total_ingresos=total_ingresos, total_gastos=total_gastos, balance=balance)


@bp.route('/get-transactions', methods=['GET'])
def get_transactions():
    # Obtener Firestore desde current_app
    db = current_app.firestore_db
    transactions = []

    try:
        # Obtener todas las transacciones desde Firestore
        docs = db.collection('transactions').get()
        for doc in docs:
            transactions.append(doc.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(transactions), 200


@bp.route("/manga")
def manga():
    return render_template("manga.html")


@bp.route("/games")
def games():
    return render_template("games.html")
