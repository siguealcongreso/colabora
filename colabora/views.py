import functools

from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import abort
from flask import flash
from flask import session
from flask import g
from werkzeug.security import check_password_hash
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
from .db import usuario
from .db import usuario_por_id


ENTIDAD = 'Jalisco'
LEGISLATURA = 'LXIII'


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'uid' not in session:
            flash("Por favor ingresa a sesión")
            return redirect(url_for('login_get'))

        return view(**kwargs)

    return wrapped_view


def valores(records):
    ""
    temas = {r["numero"]: r["tema"].split('\n') for r in records}
    resumenes = {r["numero"]: r["resumen"].split('\n') for r in records}
    comentarios = {r["numero"]: r["comentario"].split('\n') for r in records}
    db = get_db()
    tags = areas_por_iniciativa(db).get(ENTIDAD, {}).get(LEGISLATURA, {})
    areas = dbareas(db)
    users = usuarios(db)
    rows = asignadas_por_autor(db)
    asignadas = {row['usuario']: row['asignadas'] for row in rows}
    return tags, comentarios, areas, users, asignadas, temas, resumenes


@app.route("/iniciativas")
@app.route("/")
def lista():
    db = get_db()
    if 'uid' in session and request.path == '/iniciativas':
        records = iniciativas_asignadas(db, ENTIDAD, LEGISLATURA,
                                        g.user['usuario'])
    else:
        records = iniciativas(db, ENTIDAD, LEGISLATURA)
    tags, comentarios, areas, users, asignadas, temas, resumenes = valores(records)
    roles = {d['usuario']: d['rol'] for d in usuarios(db)}
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas, roles=roles,
        temas=temas, resumenes=resumenes
    )

@app.get("/login")
def login_get():
    return render_template(
        "login.html"
    )

@app.post("/login")
def login_post():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = usuario(db, username)
    if user is None:
        error = 'Usuario incorrecto.'
    elif not check_password_hash(user['contrasena'], password):
        error = 'Contraseña incorrecta.'

    if error is None:
        session.clear()
        session['uid'] = user['usuario_id']
        session.permanent = True
        flash('¡Has ingresado correctamente!')
        return redirect(url_for('lista', _method="GET"))
    flash(error)
    return redirect(url_for('login_get'))

@app.route("/logout")
def logout():
    session.clear()
    flash('¡Terminaste tu sesión correctamente!')
    return redirect(url_for('lista'))

@app.route("/asigna", methods=["GET", "POST"])
@login_required
def asigna():
    db = get_db()
    roles = {d['usuario']: d['rol'] for d in usuarios(db)}
    if g.user['rol'] != 'admin':
        abort(403)
    if request.method == 'POST':
        for numero in request.form.getlist('numero'):
            result = dbasigna(db, ENTIDAD, LEGISLATURA,
                              numero, request.form['autor'])
    records = iniciativas(db, ENTIDAD, LEGISLATURA,
                          solo_sin_asignar=True)
    tags, comentarios, areas, users, asignadas, temas, resumenes = valores(records)
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas, roles=roles,
        temas=temas, resumenes=resumenes
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
    comentario = request.form['comentario']
    area = request.form.getlist('area')
    areas = dbareas(db)
    result = actualiza_iniciativa(db, ENTIDAD, LEGISLATURA, numero,
                                  tema=tema, resumen=resumen,
                                  comentario=comentario)
    desclasifica(db, ENTIDAD, LEGISLATURA, numero)
    for i, nombre in zip(area, areas):
        clasifica(db, ENTIDAD, LEGISLATURA, numero, areas[int(i)-1]['nombre'])
    flash("Información guardada")
    return redirect(url_for('edita', numero=numero))


@app.before_request
def load_logged_in_user():
    usuario_id = session.get('uid')

    if usuario_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = usuario_por_id(db, usuario_id)
