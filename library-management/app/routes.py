from flask import Blueprint, render_template, request, redirect, url_for
import requests
from app import db
from app.models import Book

bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}")
    books = response.json().get("items", [])
    return render_template("results.html", books=books)

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
    return render_template("library.html", books=books)

@bp.route("/libros")
def libros():
    return render_template("libros.html")
