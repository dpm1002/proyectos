from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
import requests
from app.utils.firestore import get_firestore_db
manga_bp = Blueprint('manga', __name__)


@manga_bp.route("/add_manga", methods=["POST"])
def add_manga():
    db = get_firestore_db()
    manga_data = request.form

    manga_ref = db.collection('mangas').document()
    manga_ref.set({
        'title': manga_data["title"],
        'description': manga_data.get("description"),
        'original_language': manga_data.get("original_language", "ja"),
        'year': manga_data.get("year"),
        'content_rating': manga_data.get("content_rating", "safe"),
        'image_url': manga_data.get("image_url"),
        'id': manga_ref.id
    })

    return redirect(url_for("library.library"))


@manga_bp.route("/manga/<manga_id>")
def manga_details(manga_id):
    db = get_firestore_db()
    manga_doc = db.collection('mangas').document(manga_id).get()

    if not manga_doc.exists:
        return f"El manga con ID {manga_id} no existe.", 404

    manga = manga_doc.to_dict()
    return render_template("manga/manga_details.html", manga=manga)


@manga_bp.route("/manga/<manga_id>/update", methods=["POST"])
def update_manga(manga_id):
    db = get_firestore_db()
    manga_data = request.form

    db.collection('mangas').document(manga_id).update({
        'user_rating': float(manga_data.get("user_rating", 0)),
        'user_description': manga_data.get("user_description"),
        'status': manga_data.get("status")
    })

    return redirect(url_for("routes.manga_details", manga_id=manga_id))


@manga_bp.route("/searchMANGA", methods=["POST"])
def searchManga():
    query = request.form.get("query")
    results = search_manga(query)
    return render_template("manga/manga_results.html", mangas=results)


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


@manga_bp.route("/manga")
def manga():
    return render_template("manga/manga.html")
