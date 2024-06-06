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


@bp.route('/iniciativa', methods=['POST'])
@key_required
def iniciativa():
    db = get_db()
    json = request.json
    entidad = json['entidad']
    legislatura = json['legislatura']
    numero = json['numero']
    documento = json['documento']
    cambios = json['cambios']
    result = agrega_iniciativa(db, entidad, legislatura,
                               numero, cambios, documento,
                               tema="", resumen="", comentario="")
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
    result = actualiza_iniciativa(db, entidad, legislatura, numero,
                                  cambios=cambios, documento=documento)
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
