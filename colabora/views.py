import functools

from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import session
from .app import app
from .db import get_db


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
    cmd = "SELECT nombre FROM areas"
    cur.execute(cmd)
    areas = cur.fetchall()
    cur.execute("SELECT usuario FROM usuarios")
    users = [usuario['usuario'] for usuario in cur.fetchall()]
    cmd = "SELECT autor, count(numero) as asignadas FROM iniciativas GROUP BY autor"
    cur.execute(cmd)
    rows = cur.fetchall()
    asignadas = {row['autor']: row['asignadas'] for row in rows}
    return tags, comentarios, areas, users, asignadas


@app.route("/iniciativas")
@app.route("/")
def lista():
    db = get_db()
    cur = db.cursor()
    if 'username' in session and request.path == '/iniciativas':
        params = (session['username'],)
        cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM iniciativas WHERE autor=?"
        cur.execute(cmd, params)
    else:
        cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM iniciativas"
        cur.execute(cmd)
    records = cur.fetchall()
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
def asigna():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        for numero in request.form.getlist('numero'):
            params = (request.form['autor'], 'LXIII', numero)
            cmd = "UPDATE iniciativas SET autor=? WHERE legislatura=? AND numero=?"
            cur.execute(cmd, params)
            db.commit()
    cmd = "SELECT numero, cambios, tema, resumen, tags, autor, estado, comentario FROM iniciativas WHERE autor=''"
    cur.execute(cmd)
    records = cur.fetchall()
    tags, comentarios, areas, users, asignadas = valores(records, cur)
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas
    )


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
