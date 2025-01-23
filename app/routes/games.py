from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
import requests
import os
from dotenv import load_dotenv
from app.utils.firestore import get_firestore_db

# Cargar las variables del archivo .env
load_dotenv()

RAWG_API = os.getenv("RAWG_API")

games_bp = Blueprint('games', __name__)


@games_bp.route("/add_game", methods=["POST"])
def add_game():
    db = get_firestore_db()
    game_data = request.form

    # Añadir un nuevo documento y obtener su referencia
    game_ref = db.collection('games').document()
    game_ref.set({
        'title': game_data["title"],
        'released': game_data.get("released"),
        'rating': game_data.get("rating"),
        'image_url': game_data.get("image_url"),
        'id': game_ref.id  # Guardar el ID generado en el documento
    })

    return redirect(url_for("library.library"))


@games_bp.route("/game/<game_id>")
def game_details(game_id):
    db = get_firestore_db()
    game_doc = db.collection('games').document(game_id).get()

    if not game_doc.exists:
        return f"El juego con ID {game_id} no existe.", 404

    game = game_doc.to_dict()
    return render_template("games/game_details.html", game=game)


@games_bp.route("/game/<game_id>/update", methods=["POST"])
def update_game(game_id):
    db = get_firestore_db()
    game_data = request.form

    db.collection('games').document(game_id).update({
        'user_rating': float(game_data.get("user_rating", 0)),
        'user_description': game_data.get("user_description"),
        'status': game_data.get("status")
    })

    return redirect(url_for("routes.game_details", game_id=game_id))


@games_bp.route("/search_game", methods=["GET", "POST"])
def search_game():
    if request.method == "POST":
        query = request.form.get("query")
        api_key = RAWG_API
        url = f"https://api.rawg.io/api/games"
        params = {
            "key": api_key,
            "search": query,
            "page_size": 50,
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            games = response.json().get("results", [])
            # Asegúrate de que cada juego tenga un 'id' (si RAWG no lo proporciona, genera uno temporal)
            for game in games:
                # Usa 'slug' como ID alternativo si existe
                game['id'] = game.get('id', game.get('slug', 'temp-id'))
            return render_template("games/game_results.html", games=games)
        else:
            return f"Error al conectar con la API de RAWG: {response.status_code}", 500
    return render_template("games/game_search.html")


@games_bp.route("/games")
def games():
    return render_template("games/games.html")
