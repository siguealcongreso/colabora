import functools

from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import session
from .app import app
from .db import get_db
from .db import iniciativas_asignadas
from .db import iniciativas, areas as dbareas, usuarios
from .db import asignadas_por_autor
from .db import asigna as dbasigna


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'username' not in session:
            return redirect(url_for('login_get'))

        return view(**kwargs)

    return wrapped_view


def valores(records, cur):
    ""
    tags = {r["numero"]: r["tags"].split("|") for r in records}
    comentarios = {r["numero"]: r["comentario"].split('\n') for r in records}
    db = get_db()
    areas = dbareas(db)
    users = [usuario['usuario'] for usuario in usuarios(db)]
    rows = asignadas_por_autor(db)
    asignadas = {row['autor']: row['asignadas'] for row in rows}
    return tags, comentarios, areas, users, asignadas


@app.route("/iniciativas")
@app.route("/")
def lista():
    db = get_db()
    cur = db.cursor()
    if 'username' in session and request.path == '/iniciativas':
        records = iniciativas_asignadas(db, session['username'])
    else:
        records = iniciativas(db)
    tags, comentarios, areas, users, asignadas = valores(records, cur)
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas
    )

@app.get("/login")
def login_get():
    return render_template(
        "login.html"
    )

@app.post("/login")
def login_post():
    session['username'] = request.form['username']
    session.permanent = True
    return redirect(url_for('lista', _method="GET"))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('lista'))

@app.route("/asigna", methods=["GET", "POST"])
@login_required
def asigna():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        for numero in request.form.getlist('numero'):
            result = dbasigna(db, 'LXIII', numero, request.form['autor'])
    records = iniciativas_asignadas(db, usuario='')
    tags, comentarios, areas, users, asignadas = valores(records, cur)
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas
    )


@app.route("/crea/<numero>", methods=['POST'])
def crea(numero):
    db = get_db()
    cur = db.cursor()
    cmd = "SELECT * FROM iniciativas WHERE numero=?"
    cur.execute(cmd, (numero,))
    if cur.fetchone():
        return f"error: {numero} existe"
    cambios = request.form['cambios']
    params = ('LXIII', numero, cambios)
    cmd = "INSERT INTO iniciativas (legislatura, numero, cambios) VALUES (?, ?, ?)"
    cur.execute(cmd, params)
    db.commit()
    return f"ok: {numero} creada"


@app.route("/edita/<numero>")
@login_required
def edita(numero):
    cur = get_db().cursor()
    cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM iniciativas WHERE numero=?"
    cur.execute(cmd, (numero,))
    record = cur.fetchone()
    comentarios = record["comentario"].split('\n')
    cmd = "SELECT nombre FROM areas"
    cur.execute(cmd)
    areas = cur.fetchall()
    return render_template('edita.html',
                           r=record,
                           tags=record['tags'],
                           comentarios=comentarios,
                           areas=areas)
