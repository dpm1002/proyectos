from flask import Blueprint, render_template


inicio_bp = Blueprint('inicio', __name__)


@inicio_bp.route("/")
def index():
    return render_template("index.html")
