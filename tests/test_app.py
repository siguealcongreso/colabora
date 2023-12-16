from flask import session
from colabora.main import app


def test_list(client):
    response = client.get('/')
    assert b'tema1' in response.data
    assert b'resumen1' in response.data
    assert 'Iniciar sesión' in response.data.decode()

def test_login_despliega(client):
    response = client.get('/login')
    assert b'username' in response.data
    assert b'password' in response.data

def test_login_enviar(client):
    with client:
        response = client.post('/login',
                               data={'username': 'autor1'})
        assert session['username'] == 'autor1'

def test_logout(client):
    with client:
        response = client.get('logout')
        assert 'username' not in session

def test_iniciativas_vacio(client):
    with client:
        response = client.post('/login',
                               data={'username': 'xx'})
        response = client.get('/iniciativas')
        assert b'resumen1' not in response.data

def test_iniciativas_normal(client):
    app.autor = 'autor1'
    response = client.get('/iniciativas')
    assert b'resumen1' in response.data

def test_asigna_reenvia_a_login(client):
    response = client.get('asigna', follow_redirects=True)
    assert response.request.path == "/login"

def test_asigna_despliega(client):
    response = client.post('/login',
                           data={'username': 'autor1'})
    response = client.get('/asigna')
    assert b'cc' in response.data

def test_asigna_enviar(client):
    response = client.post('/login',
                           data={'username': 'autor1'})
    response = client.post('/asigna',
                           data={'autor': 'autor1', 'numero': '1'}
                           )
    assert b'cc' in response.data

def test_crea_ok(client):
    response = client.post('/crea/2', data={'cambios': 'cambios2'})
    assert b'ok: iniciativa 2 creada' == response.data

def test_crea_error(client):
    response = client.post('/crea/1', data={'cambios': 'cambios1'})
    assert b'error: 1 existe' == response.data

def test_edita(client):
    with client:
        response = client.post('/login',
                               data={'username': 'autor1'})
        response = client.get('/edita/1')
        assert b'trata?' in response.data

def test_edita_reenvia_a_login(client):
    response = client.get('/edita/1', follow_redirects=True)
    assert len(response.history) == 1
    assert response.history[0].status == '302 FOUND'
    assert response.request.path == "/login"
