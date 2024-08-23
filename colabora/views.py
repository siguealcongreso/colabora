import functools
import secrets

from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import abort
from flask import flash
from flask import session
from flask import g
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import TimestampSigner
from .app import app
from .db import get_db
from .db import iniciativas_asignadas
from .db import iniciativas, areas as dbareas, usuarios
from .db import cantidad_asignadas_por_usuario
from .db import asigna as dbasigna
from .db import agrega_iniciativa
from .db import iniciativa
from .db import areas_por_iniciativa
from .db import actualiza_iniciativa
from .db import clasifica
from .db import desclasifica
from .db import obten_usuario
from .db import usuario_por_id
from .db import estados as dbestados
from .db import agrega_usuario
from .db import asignadas_por_usuario
from .db import actualiza_usuario
from .util import revisa_tema

ENTIDAD = 'Jalisco'
LEGISLATURA = 'LXIII'
UPDATE_PASSWORD_KEY = secrets.token_hex(32)

s = TimestampSigner(UPDATE_PASSWORD_KEY)


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
    asignadas = cantidad_asignadas_por_usuario(db, ENTIDAD, LEGISLATURA)
    return tags, comentarios, areas, users, asignadas, temas, resumenes



@app.route("/")
def lista():
    db = get_db()
    if 'uid' in session:
        records = iniciativas_asignadas(db, ENTIDAD, LEGISLATURA,
                                            g.user['usuario'])
    else:
        records = iniciativas(db, ENTIDAD, LEGISLATURA,
                              solo_sin_asignar=True)
    tags, comentarios, areas, users, asignadas, temas, resumenes = valores(records)
    roles = {d['usuario']: d['rol'] for d in usuarios(db)}
    correcciones = []
    for tema in range(len(temas)):
        errores = revisa_tema(records[tema][1])
        correcciones.append(errores)
    return render_template(
        "lista.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas, roles=roles,
        temas=temas, resumenes=resumenes, correciones = correcciones
    )

@app.route("/iniciativas")
@login_required
def lista_todas():
    db = get_db()
    if g.user['rol'] == 'escritor':
        abort(403)
    records = iniciativas(db, ENTIDAD, LEGISLATURA)
    tags, comentarios, areas, users, asignadas, temas, resumenes = valores(records)
    roles = {d['usuario']: d['rol'] for d in usuarios(db)}
    asignadas_usuario = asignadas_por_usuario(db, ENTIDAD, LEGISLATURA)
    return render_template(
        "lista_todas.html", records=records, tags=tags, areas=areas,
        comentarios=comentarios, users=users, asignadas=asignadas, roles=roles,
        temas=temas, resumenes=resumenes, asignadas_usuario=asignadas_usuario
    )

@app.route("/registro", methods=('GET', 'POST'))
def registro():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Se requiere un usuario.'
        elif not password:
            error = 'Se requiere una contraseña.'

        if error is None:
            res = agrega_usuario(db, username, password, 'escritor')
            if res.startswith('error'):
                error = f"El usuario {username} ya existe."
            else:
                flash("¡Usuario creado correctamente!")
                return redirect(url_for("login_get"))
        flash(error)

    return render_template("registro.html")


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
    user = obten_usuario(db, username)
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

@app.route("/usuario", methods=('GET', 'POST'))
@login_required
def usuario():
    db = get_db()
    users = usuarios(db)
    if request.method == 'POST':
        user = request.form['autor']
        _user = obten_usuario(db, user)
        userID = _user['usuario_id']

        b_codigo = s.sign(str(userID))
        codigo = b_codigo.decode('utf-8')

        return render_template("codigo.html", codigo=codigo)
    return render_template("usuario.html", users=users)

@app.route("/recupera", methods=('GET', 'POST'))
def recupera():
    if request.method == 'POST':
        codigo = request.form['code']
        val = s.validate(codigo, max_age=86400)

        if val == True:
            _user_id = codigo.split('.')[0]
            session['user_id'] = _user_id
            session.permanent = False
            flash("Código validado correctamente.")
            return redirect(url_for('cambia', _method="GET"))
        else:
            error = 'No se ha podido validar el código.'
            flash(error)
    return render_template("recupera.html")

@app.route("/cambia", methods=('GET', 'POST'))
def cambia():
    if 'user_id' not in session:
        abort(403)
    if request.method == 'POST':
        password = request.form['password']
        db = get_db()
        error = None

        if not password:
            error = 'Se requiere una contraseña.'

        if error is None:
            pwd_hash = generate_password_hash(password)

            user_id = session['user_id']
            actualiza_usuario(db, user_id, contrasena=pwd_hash)
            session.clear()
            flash("Contraseña cambiada correctamente.")
            return redirect(url_for("login_get"))
        flash(error)
    return render_template("cambia.html")

@app.route("/confirma", methods=('GET', 'POST'))
@login_required
def confirma():
    if request.method == 'POST':
        password = request.form['password']
        db = get_db()
        error = None
        user = g.user
        if not check_password_hash(user['contrasena'], password):
            error = 'Contraseña incorrecta.'
        if error is None:
            return redirect(url_for('nueva', _method="GET"))
        flash(error)
        return redirect(url_for('confirma', _method="GET"))
    return render_template("confirma.html")

@app.route("/nueva", methods=('GET', 'POST'))
@login_required
def nueva():
    if request.method == 'POST':
        password = request.form['password']
        db = get_db()
        error = None

        if not password:
            error = 'Se requiere una contraseña.'

        if error is None:
            pwd_hash = generate_password_hash(password)
            actualiza_usuario(db, g.user['usuario_id'], contrasena=pwd_hash)
            flash("Contraseña cambiada correctamente")
            return redirect(url_for("lista"))
        flash(error)
    return render_template("nueva.html")


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
    documento = request.form['documento']
    result = agrega_iniciativa(db, ENTIDAD, LEGISLATURA,
                               numero, cambios, documento, tema="", resumen="",
                               comentario="")
    return result


@app.route("/edita/<numero>")
@login_required
def edita(numero):
    db = get_db()
    record = iniciativa(db, ENTIDAD, LEGISLATURA, numero)
    if not record:
        abort(404)
    if record['usuario'] != g.user['usuario'] and g.user['rol'] not in ('editor', 'admin'):
        abort(403)
    areas = dbareas(db)
    estados = dbestados(db)
    roles = {d['usuario']: d['rol'] for d in usuarios(db)}
    tags = areas_por_iniciativa(db).get(ENTIDAD, {}).get(LEGISLATURA, {}).get(int(numero), [])
    return render_template('edita.html',
                           r=record,
                           tags=tags,
                           estados=estados,
                           roles=roles,
                           areas=areas)

@app.route("/edita/<numero>", methods=["POST"])
@login_required
def edita_post(numero):
    db = get_db()
    tema = request.form['tema']
    resumen = request.form['resumen']
    comentario = request.form.get('comentario')
    estado_id = request.form.get('estado_id')
    area = request.form.getlist('area')
    areas = dbareas(db)
    result = actualiza_iniciativa(db, ENTIDAD, LEGISLATURA, numero,
                                  tema=tema, resumen=resumen,
                                  comentario=comentario,
                                  estado_id=estado_id)
    desclasifica(db, ENTIDAD, LEGISLATURA, numero)
    if "0" in area:
        area.remove("0")
    for i in area:
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
