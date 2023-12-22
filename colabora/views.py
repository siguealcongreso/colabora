import functools

from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import abort
from flask import flash
from flask import session
from .app import app
from .db import get_db
from .db import iniciativas_asignadas
from .db import iniciativas, areas as dbareas, usuarios
from .db import asignadas_por_autor
from .db import asigna as dbasigna
from .db import agrega_iniciativa
from .db import iniciativa
from .db import areas_por_iniciativa
from .db import actualiza_iniciativa
from .db import clasifica
from .db import desclasifica

ENTIDAD = 'Jalisco'
LEGISLATURA = 'LXIII'


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'username' not in session:
            flash("Por favor ingresa a sesión")
            return redirect(url_for('login_get'))

        return view(**kwargs)

    return wrapped_view


def valores(records):
    ""
    comentarios = {r["numero"]: r["comentario"].split('\n') for r in records}
    db = get_db()
    tags = areas_por_iniciativa(db).get(ENTIDAD, {}).get(LEGISLATURA, {})
    areas = dbareas(db)
    users = usuarios(db)
    rows = asignadas_por_autor(db)
    asignadas = {row['usuario']: row['asignadas'] for row in rows}
    return tags, comentarios, areas, users, asignadas


@app.route("/iniciativas")
@app.route("/")
def lista():
    db = get_db()
    if 'username' in session and request.path == '/iniciativas':
        records = iniciativas_asignadas(db, ENTIDAD, LEGISLATURA,
                                        session['username'])
    else:
        records = iniciativas(db, ENTIDAD, LEGISLATURA)
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
    flash('¡Has ingresado correctamente!')
    return redirect(url_for('lista', _method="GET"))

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('¡Terminaste tu sesión correctamente!')
    return redirect(url_for('lista'))

@app.route("/asigna", methods=["GET", "POST"])
@login_required
def asigna():
    db = get_db()
    if request.method == 'POST':
        for numero in request.form.getlist('numero'):
            result = dbasigna(db, ENTIDAD, LEGISLATURA,
                              numero, request.form['autor'])
    records = iniciativas(db, ENTIDAD, LEGISLATURA,
                          solo_sin_asignar=True)
    tags, comentarios, areas, users, asignadas = valores(records)
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas
    )


@app.route("/crea/<numero>", methods=['POST'])
def crea(numero):
    db = get_db()
    cambios = request.form['cambios']
    result = agrega_iniciativa(db, ENTIDAD, LEGISLATURA,
                               numero, cambios, tema="", resumen="",
                               comentario="", estado="")
    return result


@app.route("/edita/<numero>")
@login_required
def edita(numero):
    db = get_db()
    record = iniciativa(db, ENTIDAD, LEGISLATURA, numero)
    if not record:
        abort(404)
    comentarios = record["comentario"].split('\n')
    areas = dbareas(db)
    roles = {d['usuario']: d['rol'] for d in usuarios(db)}
    tags = areas_por_iniciativa(db).get(ENTIDAD, {}).get(LEGISLATURA, {}).get(int(numero), [])
    return render_template('edita.html',
                           r=record,
                           tags=tags,
                           comentarios=comentarios,
                           roles=roles,
                           areas=areas)

@app.route("/edita/<numero>", methods=["POST"])
@login_required
def edita_post(numero):
    db = get_db()
    tema = request.form['tema']
    resumen = request.form['resumen']
    area = request.form.getlist('area')
    areas = dbareas(db)
    result = actualiza_iniciativa(db, ENTIDAD, LEGISLATURA, numero,
                                  tema=tema, resumen=resumen)
    desclasifica(db, ENTIDAD, LEGISLATURA, numero)
    for i, nombre in zip(area, areas):
        clasifica(db, ENTIDAD, LEGISLATURA, numero, areas[int(i)-1]['nombre'])
    flash("Información guardada")
    return redirect(url_for('edita', numero=numero))
