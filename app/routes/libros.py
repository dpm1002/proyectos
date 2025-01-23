from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
import requests
from app.utils.firestore import get_firestore_db

books_bp = Blueprint('libros', __name__)


@books_bp.route("/add_book", methods=["POST"])
def add_book():
    db = get_firestore_db()
    book_data = request.form

    # Añadir un nuevo documento con un ID generado automáticamente
    book_ref = db.collection('books')
    doc_ref = book_ref.add({
        'title': book_data["title"],
        'author': book_data["author"],
        'series': book_data.get("series"),
        'published_date': book_data.get("published_date"),
        'description': book_data.get("description"),
        'image_url': book_data.get("image_url")
    })

    # Guardar el ID generado en el documento
    doc_ref[1].update({'id': doc_ref[1].id})

    return redirect(url_for("library.library"))


@books_bp.route("/book/<book_id>/update", methods=["POST"])
def update_book(book_id):
    db = get_firestore_db()
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


@books_bp.route("/book/<string:book_id>", methods=["GET", "POST"])
def book_details(book_id):
    db = get_firestore_db()
    print(f"Obteniendo libro con ID: {book_id}")

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
    return render_template("libros/book_details.html", book=book)


@books_bp.route("/book/<string:book_id>/update_genres", methods=["POST"])
def update_book_genres(book_id):
    db = get_firestore_db()
    genres = request.form.get("genres")

    db.collection('books').document(book_id).update({
        'genres': genres
    })

    return redirect(url_for("routes.book_details", book_id=book_id))


@books_bp.route("/searchBOOK", methods=["POST"])
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
        return render_template("libros/results.html", books=books)
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de Google Books: {e}")
        return f"Error al conectar con la API de Google Books: {e}", 500


@books_bp.route("/libros", methods=["GET"])
def libros():
    db = get_firestore_db()
    books = [doc.to_dict() for doc in db.collection('books').stream()]
    print("IDs disponibles:", books)
    return render_template("libros/libros.html", books=books)
