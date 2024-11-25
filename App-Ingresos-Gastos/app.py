from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

# Ruta de la base de datos
DB_PATH = "data/database.db"
os.makedirs("data", exist_ok=True)

# Inicialización de la base de datos
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT
                     )''')
        # Poblar datos iniciales si la tabla está vacía
        c.execute("SELECT COUNT(*) FROM transactions")
        if c.fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO transactions (type, amount, description) VALUES (?, ?, ?)",
                [
                    ('income', 1000, 'Sueldo'),
                    ('income', 500, 'Freelance'),
                    ('expense', 200, 'Alquiler'),
                    ('expense', 100, 'Comida'),
                    ('expense', 50, 'Transporte'),
                ]
            )
        conn.commit()

init_db()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener todas las transacciones
@app.route('/transacciones')
def transacciones():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM transactions WHERE type = 'income'")
        ingresos = c.fetchall()
        c.execute("SELECT * FROM transactions WHERE type = 'expense'")
        gastos = c.fetchall()
    return render_template('transacciones.html', ingresos=ingresos, gastos=gastos)

# Ruta para añadir una nueva transacción
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.form
    t_type = data['type']
    amount = float(data['amount'])
    description = data.get('description', '')

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO transactions (type, amount, description) VALUES (?, ?, ?)",
                  (t_type, amount, description))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/delete_transaction', methods=['POST'])
def delete_transaction():
    data = request.form
    transaction_id = int(data['transaction_id'])

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
    
    return redirect(url_for('index'))


# Ruta para ver solo los ingresos
@app.route('/ingresos')
def ingresos():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Obtener ingresos
        c.execute("SELECT * FROM transactions WHERE type = 'income'")
        ingresos = c.fetchall()
        # Obtener gastos
        c.execute("SELECT * FROM transactions WHERE type = 'expense'")
        gastos = c.fetchall()
    # Pasar ambos a la plantilla
    return render_template('ingresos.html', ingresos=ingresos, gastos=gastos)


# Ruta para gráficos
@app.route('/graficos')
def graficos():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
        total_income = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
        total_expense = c.fetchone()[0] or 0
        c.execute("SELECT description, SUM(amount) FROM transactions WHERE type = 'income' GROUP BY description")
        income_by_category = c.fetchall()
        c.execute("SELECT description, SUM(amount) FROM transactions WHERE type = 'expense' GROUP BY description")
        expense_by_category = c.fetchall()

    return render_template(
        'graficos.html',
        total_income=total_income,
        total_expense=total_expense,
        income_by_category=income_by_category,
        expense_by_category=expense_by_category
    )

# API para obtener transacciones en formato JSON
@app.route('/api/transacciones', methods=['GET'])
def api_transacciones():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM transactions WHERE type = 'income'")
        ingresos = c.fetchall()
        c.execute("SELECT * FROM transactions WHERE type = 'expense'")
        gastos = c.fetchall()
    return jsonify({'ingresos': ingresos, 'gastos': gastos})

# API para añadir transacciones vía JSON
@app.route('/api/add_transaction', methods=['POST'])
def api_add_transaction():
    data = request.get_json()
    t_type = data['type']
    amount = float(data['amount'])
    description = data.get('description', '')

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO transactions (type, amount, description) VALUES (?, ?, ?)",
                  (t_type, amount, description))
        conn.commit()
    return jsonify({'status': 'success', 'message': 'Transaction added'})

@app.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, type, amount, description FROM transactions")
        transactions = c.fetchall()
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True)
