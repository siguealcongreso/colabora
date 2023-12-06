"""Aplicación para colaboar"""

__version__ = "0.2"
import sqlite3
from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect, url_for


app = Flask(__name__)
app.config.from_object("defaults")
app.config.from_envvar("COLABORA_CONFIG", silent=True)
DATABASE = app.config["DATABASE"]
app.is_authenticated = False
app.autor = ''
app.users = ['usuario1', 'usuario2', 'usuario3', 'usuario4']


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


@app.route("/asigna", methods=["GET", "POST"])
@app.route("/iniciativas")
@app.route("/")
def lista():
    db = get_db()
    cur = db.cursor()
    if app.autor and request.path == '/iniciativas':
        params = (app.autor,)
        cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM sintema WHERE autor=?"
        cur.execute(cmd, params)
    elif request.path == '/asigna':
        if request.method == 'POST':
            for numero in request.form.getlist('numero'):
                params = (request.form['autor'], 'LXIII', numero)
                cmd = "UPDATE sintema SET autor=? WHERE legislatura=? AND numero=?"
                cur.execute(cmd, params)
                db.commit()
        cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM sintema WHERE autor=''"
        cur.execute(cmd)
    else:
        cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM sintema"
        cur.execute(cmd)
    records = cur.fetchall()
    editar = {r["numero"]: "editar" in r["estado"] for r in records}
    tags = {r["numero"]: r["tags"].split("|") for r in records}
    comentarios = {r["numero"]: r["comentario"].split('\n') for r in records}
    cmd = "SELECT nombre FROM areas"
    cur.execute(cmd)
    areas = cur.fetchall()
    request.is_authenticated = app.is_authenticated
    request.user = app.autor
    users = app.users
    return render_template(
        "lista.html", records=records, editar=editar, tags=tags, areas=areas,
        comentarios=comentarios, users=users
    )

@app.get("/login")
def login_get():
    return render_template(
        "login.html"
    )

@app.post("/login")
def login_post():
    app.is_authenticated = True
    app.autor = request.form['username']
    return redirect(url_for('lista'))

@app.route("/logout")
def logout():
    app.is_authenticated = False
    return redirect(url_for('lista'))

@app.route("/edita/<numero>")
def edita(numero):
    cur = get_db().cursor()
    cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM sintema WHERE numero=?"
    cur.execute(cmd, (numero,))
    record = cur.fetchone()
    comentarios = record["comentario"].split('\n')
    cmd = "SELECT nombre FROM areas"
    cur.execute(cmd)
    areas = cur.fetchall()
    request.user = app.autor
    return render_template('edita.html',
                           r=record,
                           tags=record['tags'],
                           comentarios=comentarios,
                           areas=areas)
