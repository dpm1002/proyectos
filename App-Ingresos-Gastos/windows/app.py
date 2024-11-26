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
    # Obtener ingresos
    incomes = db.collection("incomes").stream()
    ingresos = [{"id": income.id, **income.to_dict()} for income in incomes]

    # Obtener gastos
    outcomes = db.collection("outcomes").stream()
    gastos = [{"id": outcome.id, **outcome.to_dict()} for outcome in outcomes]

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

# Ruta para añadir un ingreso
@app.route('/add_income', methods=['POST'])
def add_income():
    data = request.form
    income_type = data['type']  # Tipo específico de ingreso
    amount = float(data['amount'])
    description = data.get('description', '')

    # Añadir ingreso a la colección "incomes"
    db.collection("incomes").add({
        "type": income_type,
        "amount": amount,
        "description": description
    })

    return redirect(url_for('index'))


# Ruta para añadir un gasto
@app.route('/add_outcome', methods=['POST'])
def add_outcome():
    data = request.form
    outcome_type = data['type']  # Tipo específico de gasto
    amount = float(data['amount'])
    description = data.get('description', '')

    # Añadir gasto a la colección "outcomes"
    db.collection("outcomes").add({
        "type": outcome_type,
        "amount": amount,
        "description": description
    })

    return redirect(url_for('index'))


# Ruta para eliminar una transacción
@app.route('/delete_transaction', methods=['POST'])
def delete_transaction():
    transaction_id = request.form['transaction_id']  # ID de la transacción
    collection = request.form['collection']  # Nombre de la colección

    try:
        # Eliminar el documento en la colección correspondiente
        db.collection(collection).document(transaction_id).delete()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error al eliminar la transacción: {str(e)}"



# Ruta para gráficos
@app.route('/graficos')
def graficos():
    # Ingresos
    incomes = db.collection("incomes").stream()
    income_by_category = {}
    total_income = 0
    for income in incomes:
        t = income.to_dict()
        total_income += t["amount"]
        income_by_category[t["type"]] = income_by_category.get(t["type"], 0) + t["amount"]

    # Gastos
    outcomes = db.collection("outcomes").stream()
    expense_by_category = {}
    total_expense = 0
    for outcome in outcomes:
        t = outcome.to_dict()
        total_expense += t["amount"]
        expense_by_category[t["type"]] = expense_by_category.get(t["type"], 0) + t["amount"]

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
    transactions = []

    # Obtener ingresos
    incomes = db.collection("incomes").stream()
    for income in incomes:
        t = income.to_dict()
        t["id"] = income.id
        t["collection"] = "incomes"  # Indicar la colección
        transactions.append(t)

    # Obtener gastos
    outcomes = db.collection("outcomes").stream()
    for outcome in outcomes:
        t = outcome.to_dict()
        t["id"] = outcome.id
        t["collection"] = "outcomes"  # Indicar la colección
        transactions.append(t)

    return jsonify(transactions)



if __name__ == '__main__':
    app.run(debug=True)
