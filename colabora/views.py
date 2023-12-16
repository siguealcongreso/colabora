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
from .db import agrega_iniciativa
from .db import iniciativa


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'username' not in session:
            return redirect(url_for('login_get'))

        return view(**kwargs)

    return wrapped_view


def valores(records):
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
    if 'username' in session and request.path == '/iniciativas':
        records = iniciativas_asignadas(db, session['username'])
    else:
        records = iniciativas(db)
    tags, comentarios, areas, users, asignadas = valores(records)
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
    if request.method == 'POST':
        for numero in request.form.getlist('numero'):
            result = dbasigna(db, 'LXIII', numero, request.form['autor'])
    records = iniciativas_asignadas(db, usuario='')
    tags, comentarios, areas, users, asignadas = valores(records)
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas
    )


@app.route("/crea/<numero>", methods=['POST'])
def crea(numero):
    db = get_db()
    cambios = request.form['cambios']
    result = agrega_iniciativa(db, "LXIII", numero, cambios, tema="", resumen="",
                               tags="", comentario="", autor="", estado="")
    return result


@app.route("/edita/<numero>")
@login_required
def edita(numero):
    db = get_db()
    record = iniciativa(db, numero)
    comentarios = record["comentario"].split('\n')
    areas = dbareas(db)
    return render_template('edita.html',
                           r=record,
                           tags=record['tags'],
                           comentarios=comentarios,
                           areas=areas)
