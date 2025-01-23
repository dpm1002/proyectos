from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
from datetime import datetime

finanzas_bp = Blueprint('finanzas', __name__)


@finanzas_bp.route("/finanzas", methods=["GET", "POST"])
def finanzas():
    db = current_app.firestore_db

    if request.method == "POST":
        transaction_type = request.form.get("transaction_type")
        category = request.form.get("category")
        amount = float(request.form.get("amount", 0))

        db.collection('transactions').add({
            'transaction_type': transaction_type,
            'category': category,
            'amount': amount,
            'date': datetime.utcnow()
        })

        return redirect(url_for("routes.finanzas"))

    transactions = [doc.to_dict()
                    for doc in db.collection('transactions').stream()]
    return render_template("finanzas/finanzas.html", transactions=transactions)


@finanzas_bp.route("/finanzas/grafico")
def finanzas_grafico():
    db = current_app.firestore_db

    transactions = [doc.to_dict()
                    for doc in db.collection('transactions').stream()]
    total_ingresos = sum(t['amount']
                         for t in transactions if t['transaction_type'] == "ingreso")
    total_gastos = sum(t['amount']
                       for t in transactions if t['transaction_type'] == "gasto")
    balance = total_ingresos - total_gastos

    return render_template("finanzas/finanzas_grafico.html", total_ingresos=total_ingresos, total_gastos=total_gastos, balance=balance)


@finanzas_bp.route('/get-transactions', methods=['GET'])
def get_transactions():
    # Obtener Firestore desde current_app
    db = current_app.firestore_db
    transactions = []

    try:
        # Obtener todas las transacciones desde Firestore
        docs = db.collection('transactions').get()
        for doc in docs:
            transactions.append(doc.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(transactions), 200
