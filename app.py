import sqlite3
from flask import Flask
from flask import render_template
from flask import g


app = Flask(__name__)
app.config.from_object("config")
DATABASE = app.config["DATABASE"]


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def lista():
    cur = get_db().cursor()
    cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado FROM sintema"
    cur.execute(cmd)
    records = cur.fetchall()
    editar = {r["numero"]: r["estado"] == "" for r in records}
    tags = {r["numero"]: r["tags"].split("|") for r in records}
    cmd = "SELECT nombre FROM areas"
    cur.execute(cmd)
    areas = cur.fetchall()
    return render_template(
        "lista.html", records=records, editar=editar, tags=tags, areas=areas
    )
