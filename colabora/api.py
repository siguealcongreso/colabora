import functools
from werkzeug.security import check_password_hash
from flask import Blueprint
from flask import request
from flask import abort
from flask import current_app
from .db import get_db
from .db import agrega_iniciativa
from .db import actualiza_iniciativa
from .db import remueve_iniciativa
from .db import iniciativas
from .db import asigna
from .db import clasifica


bp = Blueprint('api', __name__, url_prefix='/api')


def key_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if request.json.get('key') != current_app.config['API_KEY']:
            abort(403)

        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=['POST'])
def login():
    json = request.json
    user = json['username']
    password = json['password']
    if check_password_hash(current_app.config['API_PASSWORD'], password):
        return {'result': 'ok: ingreso correcto',
                'key': current_app.config['API_KEY']}
    else:
        return {'result': 'error: ingreso denegado'}


@bp.route('/iniciativa', methods=['GET'])
@key_required
def iniciativas_lista():
    db = get_db()
    json = request.json
    entidad = json['entidad']
    legislatura = json['legislatura']
    result = iniciativas(db, entidad=entidad, legislatura=legislatura)
    json = [dict(row) for row in result]
    return {'result': json}


@bp.route('/iniciativa', methods=['POST'])
@key_required
def iniciativa_agrega():
    db = get_db()
    json = request.json
    entidad = json['entidad']
    legislatura = json['legislatura']
    numero = json['numero']
    documento = json['documento']
    cambios = json['cambios']
    tema = json.get('tema', '')
    resumen = json.get('resumen', '')
    result = agrega_iniciativa(db, entidad, legislatura,
                               numero, cambios, documento,
                               tema=tema, resumen=resumen, comentario="")
    return {'result': result}


@bp.route('/iniciativa', methods=['PATCH'])
@key_required
def iniciativa_actualiza():
    db = get_db()
    json = request.json
    entidad = json['entidad']
    legislatura = json['legislatura']
    numero = json['numero']
    documento = json.get('documento', None)
    cambios = json.get('cambios', None)
    estado_id = json.get('estado_id', None)
    result = actualiza_iniciativa(db, entidad, legislatura, numero,
                                  cambios=cambios, documento=documento, estado_id=estado_id)
    return {'result': result}

@bp.route('/iniciativa', methods=['DELETE'])
@key_required
def iniciativa_remueve():
    db = get_db()
    json = request.json
    entidad = json['entidad']
    legislatura = json['legislatura']
    numero = json['numero']
    result = remueve_iniciativa(db, entidad, legislatura,
                               numero)
    return {'result': result}

@bp.route('/asigna', methods=['POST'])
@key_required
def asigna_usuario():
    db = get_db()
    json = request.json
    entidad = json['entidad']
    legislatura = json['legislatura']
    numero = json['numero']
    usuario = json['usuario']
    result = asigna(db, entidad, legislatura,
                    numero, usuario)
    return {'result': result}

@bp.route('/clasifica', methods=['POST'])
@key_required
def clasifica_area():
    db = get_db()
    json = request.json
    entidad = json['entidad']
    legislatura = json['legislatura']
    numero = json['numero']
    area = json['area']
    result = clasifica(db, entidad, legislatura,
                       numero, area)
    return {'result': result}
