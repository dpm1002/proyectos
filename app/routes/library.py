from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
from app.utils.firestore import get_firestore_db

library_bp = Blueprint('library', __name__)


@library_bp.route("/library")
def library():
    db = get_firestore_db()

    books = []
    for doc in db.collection('books').stream():
        book = doc.to_dict()
        book['id'] = doc.id  # Asegúrate de incluir el ID
        books.append(book)

    mangas = [doc.to_dict() for doc in db.collection('mangas').stream()]
    games = [doc.to_dict() for doc in db.collection('games').stream()]

    return render_template("library.html", books=books, mangas=mangas, games=games)
