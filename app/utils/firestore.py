from flask import current_app


def get_firestore_db():
    return current_app.firestore_db
