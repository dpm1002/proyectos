from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Configurar Firebase
cred = credentials.Certificate("serviceAccountKey.json")  # Ruta al archivo JSON descargado
firebase_admin.initialize_app(cred)

# Conectar a Firestore
db = firestore.client()

app = Flask(__name__)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener todas las transacciones
@app.route('/transacciones')
def transacciones():
    transactions = db.collection("transactions").stream()

    ingresos = []
    gastos = []

    for transaction in transactions:
        t = transaction.to_dict()
        t["id"] = transaction.id  # Agregar el ID del documento
        if t["type"] == "income":
            ingresos.append(t)
        elif t["type"] == "expense":
            gastos.append(t)

    return render_template('transacciones.html', ingresos=ingresos, gastos=gastos)

# Ruta para añadir una nueva transacción
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.form
    t_type = data['type']
    amount = float(data['amount'])
    description = data.get('description', '')

    # Añadir transacción a Firestore
    db.collection("transactions").add({
        "type": t_type,
        "amount": amount,
        "description": description
    })

    return redirect(url_for('index'))

# Ruta para eliminar una transacción
@app.route('/delete_transaction', methods=['POST'])
def delete_transaction():
    transaction_id = request.form['transaction_id']

    # Eliminar transacción por ID
    db.collection("transactions").document(transaction_id).delete()

    return redirect(url_for('index'))

# Ruta para gráficos
@app.route('/graficos')
def graficos():
    transactions = db.collection("transactions").stream()

    total_income = 0
    total_expense = 0
    income_by_category = {}
    expense_by_category = {}

    for transaction in transactions:
        t = transaction.to_dict()
        if t["type"] == "income":
            total_income += t["amount"]
            income_by_category[t["description"]] = income_by_category.get(t["description"], 0) + t["amount"]
        elif t["type"] == "expense":
            total_expense += t["amount"]
            expense_by_category[t["description"]] = expense_by_category.get(t["description"], 0) + t["amount"]

    return render_template(
        'graficos.html',
        total_income=total_income,
        total_expense=total_expense,
        income_by_category=income_by_category.items(),
        expense_by_category=expense_by_category.items()
    )

# API para obtener transacciones en formato JSON
@app.route('/api/transacciones', methods=['GET'])
def api_transacciones():
    transactions = db.collection("transactions").stream()

    data = []
    for transaction in transactions:
        t = transaction.to_dict()
        t["id"] = transaction.id  # Incluir el ID del documento
        data.append(t)

    return jsonify(data)

@app.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    transactions = db.collection("transactions").stream()
    data = []
    for transaction in transactions:
        doc = transaction.to_dict()
        doc["id"] = transaction.id  # Añadir el ID único del documento
        data.append(doc)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
