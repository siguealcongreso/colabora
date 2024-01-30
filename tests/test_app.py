from flask import session
from flask import g
from colabora.main import app
import colabora.views
import colabora.db

colabora.views.ENTIDAD = 'entidad1'
colabora.views.LEGISLATURA = 'legislatura1'


def test_list_sin_sesion(client):
    response = client.get('/')
    assert b'tema1' not in response.data
    assert b'resumen1' not in response.data
    assert 'Iniciar sesión' in response.data.decode()
    assert b'title="Editar"' not in response.data
    assert b'tema3' in response.data
    assert b'resumen3' in response.data
    assert b'Registrar' in response.data

def test_list_en_sesion_escritor(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/')
        assert b'tema1' in response.data
        assert b'resumen1' in response.data
        assert 'Terminar sesión' in response.data.decode()
        assert b'1" title="Editar"' in response.data
        assert b"mero</b> 2" not in response.data
        assert b"mero</b> 3" not in response.data
        assert b'3" title="Editar"' not in response.data

def test_list_en_sesion_editor_asignadas(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.get('/')
        assert b'tema1' not in response.data
        assert b'resumen1' not in response.data
        assert 'Terminar sesión' in response.data.decode()
        assert b'1" title="Editar"' not in response.data
        assert b'3" title="Editar"' not in response.data

def test_list_en_sesion_admin_asignadas(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario3',
                                     'password': 'contrasena3'})
        response = client.get('/')
        assert b'tema1' not in response.data
        assert b'resumen1' not in response.data
        assert 'Terminar sesión' in response.data.decode()
        assert b'1" title="Editar"' not in response.data
        assert b'3" title="Editar"' not in response.data
        assert b'href="asigna"' in response.data


def test_lista_todas_sin_sesion(client):
    with client:
        response = client.get('/iniciativas', follow_redirects=True)
        assert len(response.history) == 1
        assert response.history[0].status == '302 FOUND'
        assert response.request.path == "/login"

def test_lista_todas_en_sesion_escritor_no_acceso(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/iniciativas')
        assert 403 == response.status_code
        assert b'Forbidden' in response.data

def test_lista_todas_en_sesion_editor(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.get('/iniciativas')
        assert b'tema1' in response.data
        assert b'resumen1' in response.data
        assert 'Terminar sesión' in response.data.decode()
        assert b'1" title="Editar"' in response.data
        assert b'3" title="Editar"' in response.data

def test_lista_todas_en_sesion_admin(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario3',
                                     'password': 'contrasena3'})
        response = client.get('/iniciativas')
        assert b'tema1' in response.data
        assert b'resumen1' in response.data
        assert 'Terminar sesión' in response.data.decode()
        assert b'1" title="Editar"' in response.data
        assert b'3" title="Editar"' in response.data
        assert b'href="asigna"' in response.data

def test_iniciativas_vacio(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario4',
                                     'password': 'contrasena3'})
        response = client.get('/iniciativas')
        assert b'resumen1' not in response.data


def test_registra_despliega(client):
    response = client.get('/registro')
    assert b'Registro' in response.data

def test_registra_enviar_ok(client):
    response = client.post('/registro', follow_redirects=True,
                           data={'username': 'usuario5',
                                 'password': 'contrasena5'})
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"
    assert b'Usuario creado' in response.data

def test_registra_falta_usuario(client):
    response = client.post('/registro', follow_redirects=True,
                           data={'username': '',
                                 'password': 'contrasena5'})
    assert b'Se requiere un usuario' in response.data

def test_registra_falta_contrasena(client):
    response = client.post('/registro', follow_redirects=True,
                           data={'username': 'usuario5',
                                 'password': ''})
    assert 'Se requiere una contraseña' in response.data.decode()

def test_registra_enviar_usuario_ya_existe(client):
    response = client.post('/registro', follow_redirects=True,
                           data={'username': 'usuario1',
                                 'password': 'contrasena1'})
    assert b'El usuario usuario1 ya existe' in response.data


def test_login_despliega(client):
    response = client.get('/login')
    assert b'username' in response.data
    assert b'password' in response.data

def test_login_enviar(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password':'contrasena1'})
        assert session['uid'] == 1

def test_login_enviar_usuario_incorrecto(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario5',
                                     'password':'contrasena5'},
                               follow_redirects=True)
        assert session['_flashes'][0][1] == 'Usuario incorrecto.'
        assert response.request.path == '/login'

def test_login_enviar_contrasena_incorrecta(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password':'contrasena2'})
        assert session['_flashes'][0][1] == 'Contraseña incorrecta.'

def test_logout(client):
    with client:
        response = client.get('logout')
        assert 'uid' not in session

def test_asigna_reenvia_a_login(client):
    response = client.get('asigna', follow_redirects=True)
    assert response.request.path == "/login"

def test_asigna_despliega(client):
    response = client.post('/login',
                           data={'username': 'usuario3',
                                 'password': 'contrasena3'})
    response = client.get('/asigna')
    assert b'usuario3' in response.data
    assert b"mero</b> 3" in response.data
    assert b'Asignar iniciativas' not in response.data
    assert b'Ver todas las iniciativas' in response.data

def test_asigna_acceso_denegado(client):
    response = client.post('/login',
                           data={'username': 'usuario1',
                                 'password': 'contrasena1'})
    response = client.get('/asigna')
    assert 403 == response.status_code
    assert b'Forbidden' in response.data

def test_asigna_enviar(client):
    response = client.post('/login',
                           data={'username': 'usuario3',
                                 'password': 'contrasena3'})
    response = client.post('/asigna',
                           data={'autor': 'usuario3', 'numero': '1'}
                           )
    assert b'usuario3' in response.data

def test_crea_ok(client):
    response = client.post('/crea/2', data={'cambios': 'cambios2',
                                            'documento': 'documento2'})
    assert b'ok: iniciativa 2 creada' == response.data

def test_crea_error(client):
    response = client.post('/crea/1', data={'cambios': 'cambios1',
                                            'documento': 'documento1'})
    assert b'error: iniciativa 1 no creada' == response.data

def test_edita(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/edita/1')
        assert b'trata?' in response.data
        assert b'name="comentario"' not in response.data
        assert b'comentario1' in response.data

def test_edita_sin_permiso(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario4',
                                     'password': 'contrasena4'})
        response = client.get('/edita/1', follow_redirects=True)
        assert 403 == response.status_code
        assert b'Forbidden' in response.data

def test_edita_comentario(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.get('/edita/1')
        assert b'trata?' in response.data
        assert b'name="comentario"' in response.data
        assert b'comentario1' in response.data

def test_edita_no_existe(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/edita/2')
        assert 404 == response.status_code
        assert b'Not Found' in response.data

def test_edita_sin_area(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.get('/edita/3')
        assert b'trata?' in response.data

def test_edita_reenvia_a_login(client):
    response = client.get('/edita/1', follow_redirects=True)
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"

def test_edita_guardar_area_multiple(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.post('/edita/1', data={'tema': 'TEMA', 'resumen': 'RESUMEN',
                                                 'comentario': 'COMENTARIO',
                                                 'area': ['1', '2']},
                               follow_redirects=True)
        assert 200 == response.status_code
        assert b'TEMA' in response.data
        assert b'RESUMEN' in response.data
        assert b'value="1" selected' in response.data
        assert b'value="2" selected' in response.data

def test_edita_guardar_area_sin_seleccionar(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.post('/edita/1', data={'tema': 'TEMA', 'resumen': 'RESUMEN',
                                                 'comentario': 'COMENTARIO',
                                                 'area': []},
                               follow_redirects=True)
        assert 200 == response.status_code
        assert b'TEMA' in response.data
        assert b'RESUMEN' in response.data
        assert b'value="1">' in response.data
        assert b'value="2">' in response.data

def test_edita_guardar_area_eliminar(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.post('/edita/1', data={'tema': 'TEMA', 'resumen': 'RESUMEN',
                                                 'comentario': 'COMENTARIO',
                                                 'area': ['0']},
                               follow_redirects=True)
        assert 200 == response.status_code
        assert b'TEMA' in response.data
        assert b'RESUMEN' in response.data
        assert b'value="1">' in response.data
        assert b'value="2">' in response.data


def test_load_logged_in_user_none(client):
    with app.test_request_context():
        result = colabora.views.load_logged_in_user()
        assert g.user == None

def test_load_logged_in_user_valid(client):
    with app.test_request_context():
        session['uid'] = 1
        result = colabora.views.load_logged_in_user()
        assert g.user['usuario_id'] == 1

def test_usuario(client):
    with client:
        response = client.get('/usuario')

def test_confirma(client):
    with client:
        response = client.get('/confirma')

def test_nueva(client):
    with client:
        response = client.get('/nueva')
