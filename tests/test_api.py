from pytest import raises
from werkzeug.exceptions import Forbidden
from colabora.main import app
from colabora.api import key_required


def test_login_ok(client):
    response = client.post('/api/login',
                           json={'username': 'usuario_api',
                                 'password': 'contrasena_api'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'ok: ingreso correcto',
                             'key': 'api-key-cambiar'}


def test_login_error(client):
    response = client.post('/api/login',
                           json={'username': 'usuario_api',
                                 'password': 'contrasena'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'error: ingreso denegado'}


def test_key_required_key_correcto(client):

    def view():
        return 'Ok'
    with app.test_request_context(json={'key': 'api-key-cambiar'}):
        wrapped = key_required(view)
        assert wrapped() == 'Ok'


def test_key_required_key_incorrecto(client):

    def view():
        return 'Ok'
    with app.test_request_context(json={'key': 'api-key-incorrecto'}):
        wrapped = key_required(view)
        with raises(Forbidden):
            assert wrapped()


def test_key_required_no_key(client):

    def view():
        return 'Ok'
    with app.test_request_context(json={}):
        wrapped = key_required(view)
        with raises(Forbidden):
            assert wrapped()


def test_iniciativa(client):
    response = client.get('/api/iniciativa',
                          json={'entidad': 'entidad1',
                                'legislatura': 'legislatura1',
                                'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert len(response.json['result']) == 2


def test_iniciativa_agregar_sin_key(client):
    response = client.post('/api/iniciativa',
                           json={'entidad': 'entidad1',
                                 'legislatura': 'legislatura1',
                                 'numero': 4,
                                 'cambios': 'cambios4',
                                 'documento': 'documento4'})
    assert response.status == '403 FORBIDDEN'


def test_iniciativa_agregar_ok(client):
    response = client.post('/api/iniciativa',
                           json={'entidad': 'entidad1',
                                 'legislatura': 'legislatura1',
                                 'numero': 4,
                                 'cambios': 'cambios4',
                                 'documento': 'documento4',
                                 'tema': 'tema1',
                                 'resumen': 'resumen1',
                                 'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'ok: iniciativa 4 creada'}


def test_iniciativa_agregar_error(client):
    response = client.post('/api/iniciativa',
                           json={'entidad': 'entidad1',
                                 'legislatura': 'legislatura1',
                                 'numero': 3,
                                 'cambios': 'cambios3',
                                 'documento': 'documento3',
                                 'tema': 'tema3',
                                 'resumen': 'resumen3',
                                 'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'error: iniciativa 3 no creada'}


def test_iniciativa_actualizar_sin_key(client):
    response = client.patch('api/iniciativa',
                            json={'entidad': 'entidad1',
                                  'legislatura': 'legislatura1',
                                  'numero': 3,
                                  'cambios': 'cambios33',
                                  'documento': 'documento33'})
    assert response.status == '403 FORBIDDEN'


def test_iniciativa_actualizar_ok(client):
    response = client.patch('api/iniciativa',
                            json={'entidad': 'entidad1',
                                  'legislatura': 'legislatura1',
                                  'numero': 3,
                                  'cambios': 'cambios33',
                                  'documento': 'documento33',
                                  'estado_id': 1,
                                  'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'ok: iniciativa 3 actualizada'}


def test_iniciativa_actualizar_error(client):
    response = client.patch('api/iniciativa',
                            json={'entidad': 'entidad1',
                                  'legislatura': 'legislatura1',
                                  'numero': 2,
                                  'cambios': 'cambios22',
                                  'documento': 'documento22',
                                  'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'error: iniciativa 2 no actualizada'}


def test_iniciativa_remover_sin_key(client):
    response = client.delete('api/iniciativa',
                            json={'entidad': 'entidad1',
                                  'legislatura': 'legislatura1',
                                  'numero': 3,
                                  'cambios': 'cambios33',
                                  'documento': 'documento33'})
    assert response.status == '403 FORBIDDEN'


def test_iniciativa_remover_ok(client):
    response = client.delete('api/iniciativa',
                            json={'entidad': 'entidad1',
                                  'legislatura': 'legislatura1',
                                  'numero': 3,
                                  'cambios': 'cambios33',
                                  'documento': 'documento33',
                                  'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'ok: iniciativa 3 removida'}


def test_iniciativa_remover_error(client):
    response = client.delete('api/iniciativa',
                            json={'entidad': 'entidad1',
                                  'legislatura': 'legislatura1',
                                  'numero': 2,
                                  'cambios': 'cambios22',
                                  'documento': 'documento22',
                                  'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'error: iniciativa 2 no removida'}


def test_asigna_ok(client):
    response = client.post('/api/asigna',
                          json={'entidad': 'entidad1',
                                'legislatura': 'legislatura1',
                                'numero': 3,
                                'usuario': 'usuario3',
                                'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'ok: iniciativa 3 asignada a usuario3'}


def test_asigna_error(client):
    response = client.post('/api/asigna',
                          json={'entidad': 'entidad1',
                                'legislatura': 'legislatura1',
                                'numero': 1,
                                'usuario': 'usuario1',
                                'key': 'api-key-cambiar'})
    assert response.status == '200 OK'
    assert response.json == {'result': 'error: iniciativa 1 no asignada a usuario1'}
