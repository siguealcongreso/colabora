import sqlite3
from collections import defaultdict

from flask import g
from werkzeug.security import generate_password_hash
from .app import app


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
        db.execute('PRAGMA foreign_keys = ON')
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


def a_dict(records):
    "Convierte lista de tuplas a diccionario anidado."
    d = {}
    for record in records:
        a, b, c, l = record
        d.setdefault(a, dict())
        d[a].setdefault(b, dict())
        d[a][b].setdefault(c, [])
        d[a][b][c].append(l)
    return d


def usuario_por_id(db, usuario_id):
    """Regresa un diccionario con los valores del
    usuario que corresponde a *usuario_id*."""
    cmd = "SELECT * FROM usuarios WHERE usuario_id=?"
    cur = db.cursor()
    cur.execute(cmd, (usuario_id,))
    return cur.fetchone()


def obten_usuario(db, usuario):
    """Regresa un diccionario con los valores del
    usuario que corresponde a *usuario*."""
    cmd = "SELECT * FROM usuarios WHERE usuario=?"
    cur = db.cursor()
    cur.execute(cmd, (usuario,))
    return cur.fetchone()


def usuarios(db):
    """Regresa una lista de los usuarios

    Cada elemento es un diccionario con
    `usuario` y `rol`.
    """
    cmd = "SELECT * FROM usuarios"
    cur = db.cursor()
    cur.execute(cmd)
    records = cur.fetchall()
    return records

def estados(db):
    """Regresa una lista de estados.

    Cada elemento es un diccionario con las
    llaves *estado_id* y *estado*."""
    cmd = "SELECT * FROM estado"
    cur = db.cursor()
    cur.execute(cmd)
    records = cur.fetchall()
    return records

def areas(db):
    """Regresa una lista de areas.

    Cada elemento es un diccionario con las
    llaves *area_id* y *nombre*."""
    cmd = "SELECT nombre FROM areas"
    cur = db.cursor()
    cur.execute(cmd)
    records = cur.fetchall()
    return records

def areas_por_iniciativa(db):
    cmd = ("SELECT entidad.nombre, legislatura.nombre, numero, areas.nombre "
           "FROM clasificacion "
           "LEFT JOIN iniciativas USING (legislatura_id, numero) "
           "JOIN areas USING (area_id) "
           "JOIN legislatura USING (legislatura_id) "
           "JOIN entidad USING (entidad_id)")
    cur = db.cursor()
    cur.execute(cmd)
    records = cur.fetchall()
    return a_dict(records)


def cantidad_asignadas_por_usuario(db, entidad, legislatura):
    cmd = ("SELECT numero, estado, usuario "
           "FROM iniciativas "
           "LEFT JOIN estado USING (estado_id) "
           "LEFT JOIN asignacion USING (legislatura_id, numero) "
           "LEFT JOIN usuarios USING (usuario_id) "
           "WHERE iniciativas.legislatura_id=(SELECT legislatura_id FROM legislatura WHERE nombre=?)")
    cur = db.cursor()
    cur.execute(cmd,(legislatura,))
    records = cur.fetchall()
    asignadas = dict()
    for row in records:
        usuario = row['usuario']
        estado = row['estado']
        if estado == None:
            estado = 'Nueva'
        if usuario == None:
            usuario = ''
        if usuario not in asignadas :
            asignadas[usuario] = dict()
            asignadas[usuario]['Total'] = 0
            asignadas[usuario]['Nueva'] = 0
            asignadas[usuario]['Pendiente'] = 0
            asignadas[usuario]['Revisada'] = 0

        asignadas[usuario][estado] += 1
        asignadas[usuario]['Total'] += 1

    return asignadas

def asignadas_por_usuario(db, entidad, legislatura):
    cmd = ("SELECT numero, cambios, documento, tema, resumen, estado, comentario, usuario "
           "FROM iniciativas "
           "LEFT JOIN estado USING (estado_id) "
           "LEFT JOIN asignacion USING (legislatura_id, numero) "
           "LEFT JOIN usuarios USING (usuario_id) "
           "WHERE iniciativas.legislatura_id=(SELECT legislatura_id FROM legislatura WHERE nombre=?)")
    cur = db.cursor()
    cur.execute(cmd, (legislatura,))
    records = cur.fetchall()
    asignadas = defaultdict(list)
    for row in records:
        usuario = row['usuario']
        if usuario == None:
            usuario = ''
        asignadas[usuario].append(row)
    return asignadas

def iniciativa(db, entidad, legislatura, numero):
    cur = db.cursor()
    cmd = ("SELECT numero, cambios, documento, tema, resumen, estado, comentario, usuario "
           "FROM iniciativas "
           "LEFT JOIN estado USING (estado_id) "
           "LEFT JOIN asignacion USING (legislatura_id, numero) "
           "LEFT JOIN usuarios USING (usuario_id) "
           "WHERE iniciativas.legislatura_id=(SELECT legislatura_id FROM legislatura WHERE nombre=?) AND "
           "numero=?")
    cur.execute(cmd, (legislatura, numero))
    record = cur.fetchone()
    return record

def iniciativas(db, entidad, legislatura, solo_sin_asignar=False):
    cmd = ("SELECT numero, cambios, documento, tema, resumen, estado, comentario, usuario "
           "FROM iniciativas "
           "LEFT JOIN estado USING (estado_id) "
           "LEFT JOIN asignacion USING (legislatura_id, numero) "
           "LEFT JOIN usuarios USING (usuario_id) "
           "WHERE iniciativas.legislatura_id=(SELECT legislatura_id FROM legislatura WHERE nombre=?)")
    if solo_sin_asignar:
        cmd += " AND usuario ISNULL"
    cur = db.cursor()
    cur.execute(cmd,(legislatura,))
    records = cur.fetchall()
    return records


def iniciativas_asignadas(db, entidad, legislatura, usuario):
    cmd = ("SELECT numero, cambios, documento, tema, resumen, estado, comentario, usuario "
           "FROM iniciativas "
           "LEFT JOIN estado USING (estado_id) "
           "LEFT JOIN asignacion USING (legislatura_id, numero) "
           "LEFT JOIN usuarios USING (usuario_id) "
           "WHERE iniciativas.legislatura_id=(SELECT legislatura_id FROM legislatura WHERE nombre=?) AND "
           "usuario=?")
    cur = db.cursor()
    cur.execute(cmd, (legislatura, usuario))
    records = cur.fetchall()
    return records

def asigna(db, entidad, legislatura, numero, usuario):
    cmd = ("INSERT INTO asignacion (legislatura_id, numero, usuario_id) "
           "VALUES"
           "((SELECT legislatura_id FROM legislatura WHERE nombre=? AND "
           "entidad_id=(SELECT entidad_id FROM entidad WHERE nombre=?)), "
           "?, "
           "(SELECT usuario_id FROM usuarios WHERE usuario=?))")
    cur = db.cursor()
    try:
        cur.execute(cmd, (legislatura, entidad, numero, usuario))
        db. commit()
    except sqlite3.DatabaseError:
        return f"error: iniciativa {numero} no asignada a {usuario}"
    return f"ok: iniciativa {numero} asignada a {usuario}"


def clasifica(db, entidad, legislatura, numero, area):
    cmd = ("INSERT INTO clasificacion (legislatura_id, numero, area_id) "
           "VALUES"
           "((SELECT legislatura_id FROM legislatura WHERE nombre=? AND entidad_id=(SELECT entidad_id FROM entidad WHERE nombre=?)), "
           "?, "
           "(SELECT area_id FROM areas WHERE nombre=?))")
    cur = db.cursor()
    try:
        cur.execute(cmd, (legislatura, entidad, numero, area))
        db. commit()
    except sqlite3.DatabaseError:
        return f"error: iniciativa {numero} no asignada a {area}"
    return f"ok: iniciativa {numero} asignada a {area}"

def desclasifica(db, entidad, legislatura, numero):
    cmd = ("DELETE FROM clasificacion WHERE "
           "legislatura_id=(SELECT legislatura_id FROM legislatura WHERE nombre=? AND entidad_id=(SELECT entidad_id FROM entidad WHERE nombre=?)) AND "
           "numero=?")
    cur = db.cursor()
    cur.execute(cmd, (legislatura, entidad, numero))
    if cur.rowcount >= 1:
        db. commit()
        return f"ok: se removieron {cur.rowcount} areas de iniciativa {numero}"
    return f"error: no se removieron areas de iniciativa {numero}"

def agrega_iniciativa(db, entidad, legislatura, numero, cambios, documento,
                      tema, resumen, comentario):
    """Se agrega una iniciativa que corresponde a *entidad*, *legislatura*,
    *numero*, con los valores *cambios*, *documento*, *tema*, *resumen*,
    *comentario*.

    Regresa:

     - 'ok: iniciativa *numero* creada'
     - 'error: iniciativa *numero* no creada'"""
    cmd = ("INSERT INTO iniciativas (legislatura_id, numero, "
           "cambios, documento, tema, resumen, comentario) "
           "VALUES "
           "((SELECT legislatura_id FROM legislatura WHERE nombre=? AND entidad_id=(SELECT entidad_id FROM entidad WHERE nombre=?)), "
           "?, ?, ?, ?, ?, ?)")
    cur = db.cursor()
    try:
        cur.execute(cmd, (legislatura, entidad, numero, cambios, documento,
                          tema, resumen, comentario))
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


def agrega_estado(db, estado):
    cmd = "INSERT INTO estado (estado) VALUES (?)"
    cur = db.cursor()
    try:
        cur.execute(cmd, (estado,))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: '{estado}' no creada"
    return f"ok: '{estado}' creada"


def agrega_usuario(db, nombre, contrasena, rol):
    cmd = "INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)"
    cur = db.cursor()
    try:
        cur.execute(cmd, (nombre, generate_password_hash(contrasena), rol))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: '{nombre}' no creado"
    return f"ok: '{nombre}' creado"


def agrega_entidad(db, nombre):
    cmd = "INSERT INTO entidad (nombre) VALUES (?)"
    cur = db.cursor()
    try:
        cur.execute(cmd, (nombre,))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: '{nombre}' no creado"
    return f"ok: '{nombre}' creado"


def agrega_legislatura(db, entidad, nombre):
    """Agrega la legislatura *nombre*, si aún no existe.

    Regresa:

     - 'ok: *nombre* creado'
     - 'error: *nombre* no creado'"""
    cmd = "INSERT INTO legislatura (nombre, entidad_id) VALUES (?, (SELECT entidad_id FROM entidad WHERE nombre=?))"
    cur = db.cursor()
    try:
        cur.execute(cmd, (nombre, entidad))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: '{nombre}' no creado"
    return f"ok: '{nombre}' creado"

def actualiza_iniciativa(db, entidad, legislatura, numero, tema=None, resumen=None,
                         comentario=None, estado_id=None, cambios=None, documento=None):
    """Actualiza la iniciativa que corresponde a *entidad*,
    *legislatura*, *numero* con los valores de *tema*, *resumen*,
    *comentario*, *estado*, *cambios* o *documento*.  Los
    parámetros que no es incluyen no se modifican.

    Regresa:

      - 'ok: usuario *usuario_id* actualizado'
      - 'error: usuario *usuario_id* no actualizado'
    """
    fields = []
    values = []
    if cambios != None:
        fields.append(f"cambios=?")
        values.append(cambios)
    if documento != None:
        fields.append(f"documento=?")
        values.append(documento)
    if tema != None:
        fields.append(f"tema=?")
        values.append(tema)
    if resumen != None:
        fields.append(f"resumen=?")
        values.append(resumen)
    if comentario != None:
        fields.append(f"comentario=?")
        values.append(comentario)
    if estado_id != None:
        fields.append(f"estado_id=?")
        values.append(estado_id)
    sets = ', '.join(fields)
    if sets:
        cmd = (f"UPDATE iniciativas SET {sets} WHERE "
               "legislatura_id=(SELECT legislatura_id FROM legislatura WHERE nombre=? AND entidad_id=(SELECT entidad_id FROM entidad WHERE nombre=?)) "
               "AND numero=?")
        values.extend([legislatura, entidad, numero])
        cur = db.cursor()
        cur.execute(cmd, values)
        if cur.rowcount == 1:
            db.commit()
            return f"ok: iniciativa {numero} actualizada"
    return f"error: iniciativa {numero} no actualizada"


def actualiza_usuario(db, usuario_id, usuario=None, contrasena=None,
                      rol=None, activo=None):
    """Actualiza el usuario que corresponde a *usuario_id* con los
    valores de *usuario*, *contrasena*, *rol* o *activo*.  Los
    parámetros que no es incluyen no se modifican.

    Regresa:

      - 'ok: usuario *usuario_id* actualizado'
      - 'error: usuario *usuario_id* no actualizado'
    """
    fields = []
    values = []
    if usuario != None:
        fields.append(f"usuario=?")
        values.append(usuario)
    if contrasena != None:
        fields.append(f"contrasena=?")
        values.append(contrasena)
    if rol != None:
        fields.append(f"rol=?")
        values.append(rol)
    if activo != None:
        fields.append(f"activo=?")
        values.append(activo)
    sets = ', '.join(fields)
    if sets:
        cmd = (f"UPDATE usuarios SET {sets} WHERE usuario_id=?")
        values.extend([usuario_id])
        cur = db.cursor()
        cur.execute(cmd, values)
        if cur.rowcount == 1:
            db.commit()
            return f"ok: usuario {usuario_id} actualizado"
    return f"error: usuario {usuario_id} no actualizado"

def remueve_iniciativa(db, entidad, legislatura, numero):
    """Remueve la iniciativa que corresponde a *entidad*,
    *legislatura*, *numero*, solamente si no está asignada.
    Antes de remover, se desclasifica.

    Regresa:

     - 'ok: iniciativa *numero* removida'
     - 'error: iniciativa *numero* no removida'
    """
    cmd = ("DELETE FROM iniciativas WHERE "
           "legislatura_id = (SELECT legislatura_id FROM legislatura WHERE nombre=? AND entidad_id = (SELECT entidad_id FROM entidad WHERE nombre=?)) AND "
           "numero = ?")
    cur = db.cursor()
    row = iniciativa(db, entidad, legislatura, numero)
    if row is None:
        return f"error: iniciativa {numero} no removida"
    elif row['usuario'] is not None:
         return f"error: iniciativa {numero} no removida"
    desclasifica(db, entidad, legislatura, numero)
    cur.execute(cmd, (legislatura, entidad, numero))
    db.commit()
    return f"ok: iniciativa {numero} removida"

def remueve_usuario(db, usuario_id):
    """Remueve el usuario que corresponde a *usuario_id*,
    solamente si no tienen iniciativas asignadas.

    Regresa:

     - 'ok: usuario *usuario_id* removido'
     - 'error: usuario *usuario_id* no removido'
    """
    cmd = ("DELETE FROM usuarios WHERE usuario_id = ?")
    cur = db.cursor()
    try:
        cur.execute(cmd, (usuario_id,))
        db.commit()
    except sqlite3.DatabaseError:
        return f"error: usuario {usuario_id} no removido"
    return f"ok: usuario {usuario_id} removido"
