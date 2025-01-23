from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
import requests
from google.cloud import firestore
import os
from dotenv import load_dotenv
from app.utils.firestore import get_firestore_db

# Cargar las variables del archivo .env
load_dotenv()

EXERCISE_API_URL = os.getenv("EXERCISE_API_URL")
EXERCISE_HEADERS = eval(os.getenv("EXERCISE_HEADERS"))

ejercicios_bp = Blueprint('ejercicios', __name__)


@ejercicios_bp.route("/buscar_ejercicio", methods=["GET", "POST"])
def buscar_ejercicio():
    ejercicios = []
    termino_busqueda = None

    # Si la solicitud es POST, redirigir a la misma ruta con el término como parámetro
    if request.method == "POST":
        termino_busqueda = request.form.get("termino", "").strip().lower()
        return redirect(url_for("routes.buscar_ejercicio", termino=termino_busqueda))

    # Si el término ya está en la URL, realizar la búsqueda
    termino_busqueda = request.args.get("termino", "").strip().lower()
    if termino_busqueda:
        url = f"https://exercisedb.p.rapidapi.com/exercises/name/{termino_busqueda}"
        headers = EXERCISE_HEADERS

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            ejercicios = response.json()
        else:
            ejercicios = []  # Si hay un error, vaciar lista

        # Depuración
        print(f"Término buscado: {termino_busqueda}")
        print(f"Estado de respuesta: {response.status_code}")
        print(f"Respuesta de la API: {response.json()}")

    return render_template("ejercicio/buscar_ejercicio.html", ejercicios=ejercicios, termino=termino_busqueda)


@ejercicios_bp.route("/resultado_ejercicio/<termino>")
def resultado_ejercicio(termino):
    """Mostrar detalles de un ejercicio"""
    response = requests.get(
        f"{EXERCISE_API_URL}/search/{termino}", headers=EXERCISE_HEADERS)
    exercises = response.json() if response.status_code == 200 else []
    return render_template("ejercicio/resultado_ejercicio.html", exercises=exercises)


@ejercicios_bp.route("/guardar_ejercicio", methods=["POST"])
def guardar_ejercicio():
    db = get_firestore_db()
    ejercicio_data = request.form

    # Extraer datos del formulario
    ejercicio = {
        "id": ejercicio_data.get("id"),
        "name": ejercicio_data.get("name"),
        "bodyPart": ejercicio_data.get("bodyPart"),
        "equipment": ejercicio_data.get("equipment"),
        "gifUrl": ejercicio_data.get("gifUrl"),
    }
    lista = ejercicio_data.get("lista", "Default")

    # Guardar en Firebase
    db.collection("listas").document(lista).set(
        {"ejercicios": firestore.ArrayUnion([ejercicio])}, merge=True
    )

    return jsonify({"message": f"Ejercicio '{ejercicio['name']}' guardado en la lista '{lista}'"}), 200


@ejercicios_bp.route("/ver_lista/<string:lista>")
def ver_lista(lista):
    """Ver los ejercicios de una lista específica."""
    db = get_firestore_db()
    lista_doc = db.collection("listas").document(lista).get()

    if not lista_doc.exists:
        return f"La lista '{lista}' no existe.", 404

    ejercicios = lista_doc.to_dict().get("ejercicios", [])
    return render_template("ejercicio/lista.html", lista=lista, ejercicios=ejercicios)


@ejercicios_bp.route("/agregar_ejercicio", methods=["POST"])
def agregar_ejercicio():
    db = get_firestore_db()
    lista = request.form.get("lista")
    ejercicio_id = request.form.get("ejercicio_id")
    nombre_ejercicio = request.form.get("nombre_ejercicio")

    # Agregar ejercicio a la lista
    db.collection("listas").document(lista).set(
        {"ejercicios": firestore.ArrayUnion(
            [{"id": ejercicio_id, "name": nombre_ejercicio}])},
        merge=True,
    )

    return redirect(url_for("routes.ejercicios"))


@ejercicios_bp.route("/ejercicios", methods=["GET"])
def ejercicios():
    db = get_firestore_db()
    listas_ref = db.collection("listas").stream()

    listas = []
    for lista in listas_ref:
        data = lista.to_dict()
        listas.append({
            "nombre": lista.id,
            "ejercicios": data.get("ejercicios", [])
        })

    return render_template("ejercicio/ejercicios.html", listas=listas)


@ejercicios_bp.route("/ejercicio/<string:ejercicio_id>")
def ejercicio_detalle(ejercicio_id):
    url = f"{EXERCISE_API_URL}/exercise/{ejercicio_id}"
    response = requests.get(url, headers=EXERCISE_HEADERS)

    if response.status_code == 200:
        ejercicio = response.json()
    else:
        ejercicio = {
            "error": "No se pudo obtener la información del ejercicio."}

    return render_template("ejercicio/ejercicio_detalle.html", ejercicio=ejercicio)
