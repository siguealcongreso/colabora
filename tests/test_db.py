import os
import tempfile

import pytest
from colabora.app import app as appli
from colabora.db import get_db, init_db
import colabora.db


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode()


@pytest.fixture
def database():
    db_fd, db_path = tempfile.mkstemp()
    appli.config['DATABASE'] = db_path
    appli.testing = True
    with appli.app_context():
        init_db()
        db = get_db()
        yield db
    os.close(db_fd)
    os.unlink(db_path)


def test_iniciativas_no_asignadas_vacio(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas_asignadas(database, '')
    assert len(result) == 0

def test_iniciativas_asignadas_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas_asignadas(database, 'autor1')
    assert len(result) == 1
    assert "1" == result[0]["numero"]

def test_iniciativas_asignadas_vacio(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas_asignadas(database, 'autor2')
    assert len(result) == 0


def test_agrega_iniciativa_ok(database):
    result = colabora.db.agrega_iniciativa(database, 'I', '1', 'cambios', '', '', '',
                                           '', '', '')
    assert "ok: iniciativa 1 creada" == result

def test_agrega_iniciativa_error(database):
    result = colabora.db.agrega_iniciativa(database, 'I', '1', 'cambios', '', '', '',
                                           '', '', '')
    result = colabora.db.agrega_iniciativa(database, 'I', '1', 'cambios', '', '', '',
                                           '', '', '')
    assert "error: iniciativa 1 no creada" == result


def test_agrega_area_ok(database):
    result = colabora.db.agrega_area(database, 'area1')
    assert "ok: 'area1' creada" == result

def test_agrega_area_error(database):
    result = colabora.db.agrega_area(database, 'area1')
    result = colabora.db.agrega_area(database, 'area1')
    assert "error: 'area1' no creada" == result


def test_agrega_usuario_ok(database):
    result = colabora.db.agrega_usuario(database, 'usuario1')
    assert "ok: 'usuario1' creado" == result

def test_agrega_usuario_error(database):
    result = colabora.db.agrega_usuario(database, 'usuario1')
    result = colabora.db.agrega_usuario(database, 'usuario1')
    assert "error: 'usuario1' no creado" == result
