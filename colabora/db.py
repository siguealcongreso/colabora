import sqlite3

from flask import g
from .app import app


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode())
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()



def agrega_iniciativa(db, legislatura, numero, cambios, tema, resumen,
                      tags, comentario, autor, estado):
    cmd = "INSERT INTO iniciativas (legislatura, numero, cambios, tema, resumen, tags, comentario, autor, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur = db.cursor()
    try:
        cur.execute(cmd, (legislatura, numero, cambios, tema, resumen,
                          tags, comentario, autor, estado))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: iniciativa {numero} no creada"
    return f"ok: iniciativa {numero} creada"


def agrega_area(db, nombre):
    cmd = "INSERT INTO areas (nombre) VALUES (?)"
    cur = db.cursor()
    try:
        cur.execute(cmd, (nombre,))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: '{nombre}' no creada"
    return f"ok: '{nombre}' creada"


def agrega_usuario(db, nombre):
    cmd = "INSERT INTO usuarios (usuario) VALUES (?)"
    cur = db.cursor()
    try:
        cur.execute(cmd, (nombre,))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: '{nombre}' no creado"
    return f"ok: '{nombre}' creado"
