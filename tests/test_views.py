import re
from flask import session
from flask import g
from colabora.main import app
import colabora.views
import colabora.db
import colabora.util
import secrets
from itsdangerous import TimestampSigner
import pytest

colabora.views.ENTIDAD = 'entidad1'
colabora.views.LEGISLATURA = 'legislatura1'

from colabora.views import UPDATE_PASSWORD_KEY
s = TimestampSigner(UPDATE_PASSWORD_KEY)


def test_list_sin_sesion(client):
    response = client.get('/')
    assert b'tema1' not in response.data
    assert b'resumen1' not in response.data
    assert 'Iniciar sesión' in response.data.decode()
    assert b'title="Editar"' not in response.data
    assert b'tema3' not in response.data
    assert b'resumen3' not in response.data
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
    assert re.search('usuario1.*1.*1.*0.*0.*usuario2', response.text, re.S)

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

def test_edita_escritor(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/edita/1')
        assert b'trata?' in response.data
        assert b'name="comentario"' not in response.data
        assert b'comentario1' in response.data
        
        assert b'href="..">Ver mis asignadas</a>' in response.data
        assert b'href="../iniciativas">Ver todas las iniciativas</a>' not in response.data

def test_edita_editor(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.get('/edita/1')
        assert b'trata?' in response.data
        assert b'name="comentario"' in response.data
        assert b'comentario1' in response.data
        
        assert b'href="..">Ver mis asignadas</a>' in response.data
        assert b'href="../iniciativas">Ver todas las iniciativas</a>' in response.data

def test_edita_sin_permiso(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario4',
                                     'password': 'contrasena4'})
        response = client.get('/edita/1', follow_redirects=True)
        assert 403 == response.status_code
        assert b'Forbidden' in response.data

def test_edita_comentario_editor(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.get('/edita/1')
        assert b'trata?' in response.data
        assert b'name="comentario"' in response.data
        assert b'comentario1' in response.data

def test_edita_comentario_admin(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario3',
                                     'password': 'contrasena3'})
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

def test_usuario_reenvia_a_login(client):
    response = client.get('/usuario', follow_redirects=True)
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"

def test_usuario_despliega_escritor(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/usuario')
        assert 'Cambiar mi contraseña' in response.data.decode()
        assert 'Enviar código' not in response.data.decode()
        assert b'Ver todas las iniciativas' not in response.data

def test_usuario_despliega_editor(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.get('/usuario')
        assert 'Cambiar mi contraseña' in response.data.decode()
        assert 'Enviar código' in response.data.decode()

def test_usuario_envia(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario2',
                                     'password': 'contrasena2'})
        response = client.post('/usuario',
                               data={'autor': 'usuario1'})
        codigo = s.sign('1').decode('utf-8')
        assert response.request.path == '/usuario'
        assert f'{codigo}' in response.data.decode()

def test_confirma_reenvia_a_login(client):
    response = client.get('/confirma', follow_redirects=True)
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"

def test_confirma_despliega(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/confirma')
        assert b'password' in response.data

def test_confirma_enviar_contrasena_correcta(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.post('/confirma',
                              data={'password': 'contrasena1'},
                              follow_redirects=True)
        assert response.request.path  == '/nueva'

def test_confirma_enviar_contrasena_incorrecta(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.post('/confirma',
                               data={'password': 'contrasena2'},
                               follow_redirects=True)
        assert session['_flashes'][1][1] == 'Contraseña incorrecta.'
        assert response.request.path  == '/confirma'

def test_nueva_reenvia_a_login(client):
    response = client.get('/nueva', follow_redirects=True)
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"

def test_nueva_despliega(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/nueva')
        assert b'Establecer nueva' in response.data

def test_nueva_enviar_ok(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.post('/nueva', follow_redirects=True,
                               data={'password': 'contrasena5'})
        assert len(response.history) == 1
        assert response.history[0].status == '302 FOUND'
        assert response.request.path == "/"
        assert 'Contraseña cambiada' in response.data.decode()

def test_nueva_falta_contrasena(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.post('/nueva', follow_redirects=True,
                               data={'password': ''})
        assert 'Se requiere una contraseña' in response.data.decode()

def test_recupera_despliega(client):
    with client:
        response = client.get('/recupera')
        assert b'<input type="text" class="form-control" id="codigo-recuperacion" name="code">' in response.data

def test_recupera_enviar_ok(client):
    with client:
        response = client.post('/recupera', follow_redirects=True,
                               data={'code': s.sign('1').decode('utf-8')})
        assert len(response.history) == 1
        assert response.history[0].status == '302 FOUND'
        assert response.request.path == "/cambia"
        assert 'Código validado correctamente.' in response.data.decode()

def test_recupera_enviar_incorrecto(client):
    with client:
        response = client.post('/recupera', follow_redirects=True,
                               data={'code': 'invalid'})
        assert 'No se ha podido validar el código.' in response.data.decode()

def test_cambia_sin_sesion(client):
    with client:
        response = client.get('/cambia')
        assert 'user_id' not in session
        assert 403 == response.status_code
        assert b'Forbidden' in response.data


def test_cambia_en_sesion(client):
    with client.session_transaction() as session:
        session['user_id'] = 1
    response = client.get('/cambia')
    assert 'user_id' in session
    assert b'Establecer' in response.data

def test_cambia_en_session_enviar_incorrecto(client):
    with client.session_transaction() as session:
        session['user_id'] = 1
    response = client.post('/cambia', follow_redirects=True,
                               data={'password': ''})
    assert 'Se requiere una contraseña.' in response.data.decode()

def test_cambia_en_session_enviar_ok(client):
    with client.session_transaction() as session:
        session['user_id'] = 1
    response = client.post('/cambia', follow_redirects=True,
                               data={'password': 'contrasenanueva'})
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"
    assert 'Contraseña cambiada correctamente.' in response.data.decode()

def test_buscar_reenvia_a_login(client):
    response = client.post('/buscar', follow_redirects=True)
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"

def test_buscar_tema_no_input(client):
    with client.session_transaction() as session:
        session['uid'] = 1
    response = client.post('/buscar',
                           data={'tema': ''})
    assert response.status == '200 OK'
    assert b'<td ondblclick="llenarTema(\'tema1\')"' not in response.data
    assert b'<td ondblclick="llenarTema(\'tema3\')"' not in response.data

def test_buscar_tema_input(client):
    with client.session_transaction() as session:
        session['uid'] = 1
    response = client.post('/buscar',
                           data={'tema': '1'})
    assert response.status == '200 OK'
    assert b'<td ondblclick="llenarTema(\'tema1\')"' in response.data

def test_buscar_tema_sugerencias_rechazadas(client):
    def mock_revisa_tema(tema):
        return ('Error', [])
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(colabora.views, 'revisa_tema',
                        mock_revisa_tema)
    with client.session_transaction() as session:
        session['uid'] = 1
    response = client.post('/buscar',
                           data={'tema': '1'})
    monkeypatch.undo()
    assert response.status == '200 OK'
    assert '' == response.text

def test_buscar_tema_input_acento(client):
    with client.session_transaction() as session:
        session['uid'] = 1
    response = client.post('/buscar',
                           data={'tema': 'téma1'})
    assert response.status == '200 OK'
    assert b'<td ondblclick="llenarTema(\'tema1\')"' in response.data

def test_buscar_tema_no_resultados(client):
    with client.session_transaction() as session:
        session['uid'] = 1
    response = client.post('/buscar',
                           data={'tema': 'tema4'})
    assert response.status == '200 OK'
    assert b'<td ondblclick="llenarTema(\'tema1\')"' not in response.data
    assert b'<td ondblclick="llenarTema(\'tema3\')"' not in response.data

def test_legislatura_get(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/legislatura')
        assert 200 == response.status_code

def test_legislatura_post(client):
    with client:
        response = client.post('/login',
                               data={'username': 'usuario1',
                                     'password': 'contrasena1'})
        response = client.get('/usuario')
        response = client.post('/legislatura', follow_redirects=True, data={'entidad': 2}, headers={'referer': '/'})
        assert 200 == response.status_code
