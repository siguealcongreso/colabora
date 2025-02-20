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


def test_a_dict():
    records = [
    (1, 10, 100, 1000),
    (1, 10, 100, 1001),
    (1, 11, 110, 1100),
    (2, 10, 100, 2100),
    ]
    result = colabora.db.a_dict(records)
    assert result == {1: {10: {100: [1000, 1001]},
                          11: {110: [1100]}
                          },
                      2: {10: {100: [2100]}
                          }
                      }


def test_usuario_por_id_encontrado(database):
    database.executescript(_data_sql)
    result = colabora.db.usuario_por_id(database, 1)
    assert result['usuario'] == 'usuario1'
    assert result['legislatura_id'] == 1
    assert result['legislatura'] == 'legislatura1'
    assert result['entidad'] == 'entidad1'

def test_usuario_por_id_no_encontrado(database):
    database.executescript(_data_sql)
    result = colabora.db.usuario_por_id(database, 5)
    assert result == None

def test_usuario_encontrado(database):
    database.executescript(_data_sql)
    result = colabora.db.obten_usuario(database, 'usuario1')
    assert result['usuario_id'] == 1

def test_usuario_no_encontrado(database):
    database.executescript(_data_sql)
    result = colabora.db.obten_usuario(database, 5)
    assert result == None


def test_usuarios(database):
    database.executescript(_data_sql)
    result = colabora.db.usuarios(database)
    assert len(result) == 5
    assert "usuario1" == result[0]["usuario"]
    assert "escritor" == result[0]["rol"]
    assert 1 == result[0]["usuario_id"]
    assert "usuario2" == result[1]["usuario"]
    assert "editor" == result[1]["rol"]

def test_actualiza_usuario_error(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_usuario(database, usuario_id=1)
    assert 'error: usuario 1 no actualizado' in result

def test_actualiza_usuario_id_inexistente(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_usuario(database, usuario_id=99,
                                           rol='escritor')
    assert 'error: usuario 99 no actualizado' in result

def test_actualiza_usuario_contrasena(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_usuario(database, usuario_id=1,
                                           contrasena='contrasena9')
    assert 'ok: usuario 1 actualizado' in result

def test_actualiza_usuario_usuario(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_usuario(database, usuario_id=1,
                                           usuario='usuario20')
    assert 'ok: usuario 1 actualizado' in result

def test_actualiza_usuario_rol(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_usuario(database, usuario_id=1,
                                           rol='admin')
    assert 'ok: usuario 1 actualizado' in result

def test_actualiza_usuario_activo(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_usuario(database, usuario_id=1,
                                           activo=0)
    assert 'ok: usuario 1 actualizado' in result

def test_actualiza_usuario_legislatura(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_usuario(database, usuario_id=1,
                                           legislatura_id=2)
    assert 'ok: usuario 1 actualizado' in result


def test_estados(database):
    database.executescript(_data_sql)
    result = colabora.db.estados(database)
    assert len(result) == 1
    assert "Pendiente" == result[0]["estado"]


def test_areas(database):
    database.executescript(_data_sql)
    result = colabora.db.areas(database)
    assert len(result) == 2
    assert "area1" == result[0]["nombre"]

def test_areas_por_iniciativa(database):
    database.executescript(_data_sql)
    result = colabora.db.areas_por_iniciativa(database)
    assert len(result) == 1
    assert result['entidad1']['legislatura1'][1] == ['area1']

def test_areas_por_iniciativa_vacio(database):
    result = colabora.db.areas_por_iniciativa(database)
    assert result == {}


def test_cantidad_asignadas_por_usuario(database):
    database.executescript(_data_sql)
    result = colabora.db.cantidad_asignadas_por_usuario(database, entidad= 'entidad1', legislatura= 'legislatura1')
    assert len(result) == 2
    assert result['usuario1']['Nueva'] == 1
    assert result['usuario1']['Total'] == 1
    assert result['usuario1']['Pendiente'] == 0
    assert result['usuario1']['Revisada'] == 0

def test_cantidad_asignadas_por_usuario_sin_iniciativas(database):
    database.executescript(_data_sql)
    result = colabora.db.cantidad_asignadas_por_usuario(database, entidad= 'entidad1', legislatura= 'legislatura2')
    assert len(result) == 1
    assert result == {'': {'Total': 0, 'Nueva': 0, 'Pendiente': 0, 'Revisada': 0}}

def test_cantidad_asignadas_por_usuario_todas_asignadas(database):
    database.executescript(_data_sql)
    result = colabora.db.cantidad_asignadas_por_usuario(database, entidad= 'entidad1', legislatura= 'legislatura3')
    assert len(result) == 2
    assert result == {'': {'Total': 0, 'Nueva': 0, 'Pendiente': 0, 'Revisada': 0}, 'usuario1': {'Total': 1, 'Nueva': 0, 'Pendiente': 1, 'Revisada': 0}}

def test_asignadas_por_usuario(database):
    database.executescript(_data_sql)
    result = colabora.db.asignadas_por_usuario(database, 'entidad1', 'legislatura1')
    assert len(result) == 2
    assert result['usuario1'][0]['numero'] == 1
    assert result[''][0]['numero'] == 3

def test_iniciativa_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativa(database, entidad='entidad1' ,
                                    legislatura='legislatura1',
                                    numero=1)
    assert "tema1" == result['tema']
    assert "documento1" == result['documento']

def test_iniciativa_none(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativa(database, entidad='entidad1',
                                    legislatura='legislatura1',
                                    numero=2)
    assert None == result


def test_iniciativas(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas(database, entidad='entidad1',
                                     legislatura='legislatura1')
    assert len(result) == 2
    assert result[0]['documento'] == 'documento1'


def test_iniciativas_solo_no_asignadas(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas(database, entidad='entidad1',
                                     legislatura='legislatura1',
                                     solo_sin_asignar=True)
    assert len(result) == 1


def test_iniciativas_no_asignadas_vacio(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas_asignadas(database, entidad='entidad1',
                                               legislatura='legislatura1',
                                               usuario='')
    assert len(result) == 0

def test_iniciativas_asignadas_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas_asignadas(database, entidad='entidad1',
                                               legislatura='legislatura1',
                                               usuario='usuario1')
    assert len(result) == 1
    assert 1 == result[0]["numero"]
    assert 'documento1' == result[0]["documento"]

def test_iniciativas_asignadas_vacio(database):
    database.executescript(_data_sql)
    result = colabora.db.iniciativas_asignadas(database, entidad='entidad1',
                                               legislatura='legislatura1',
                                               usuario='usuario2')
    assert len(result) == 0


def test_asigna_una(database):
    database.executescript(_data_sql)
    result = colabora.db.asigna(database, 'entidad1', 'legislatura1', 1, 'usuario2')
    assert f"ok: iniciativa 1 asignada a usuario2" == result

def test_asigna_ninguna(database):
    database.executescript(_data_sql)
    result = colabora.db.asigna(database, 'entidad1', 'legislatura1', 2, 'usuario1')
    assert f"error: iniciativa 2 no asignada a usuario1" == result


def test_clasifica_una(database):
    database.executescript(_data_sql)
    result = colabora.db.clasifica(database, 'entidad1', 'legislatura1', 1, 'area2')
    assert f"ok: iniciativa 1 asignada a area2" == result

def test_clasifica_ninguna(database):
    database.executescript(_data_sql)
    result = colabora.db.clasifica(database, 'entidad1', 'legislatura1', 2, 'area1')
    assert f"error: iniciativa 2 no asignada a area1" == result


def test_desclasifica_una(database):
    database.executescript(_data_sql)
    result = colabora.db.desclasifica(database, 'entidad1', 'legislatura1', 1)
    assert f"ok: se removieron 1 areas de iniciativa 1" == result

def test_desclasifica_ninguna(database):
    database.executescript(_data_sql)
    result = colabora.db.desclasifica(database, 'entidad1', 'legislatura1', 2)
    assert f"error: no se removieron areas de iniciativa 2" == result

def test_desclasifica_dos(database):
    database.executescript(_data_sql)
    result = colabora.db.desclasifica(database, 'entidad1', 'legislatura1', 3)
    assert f"ok: se removieron 2 areas de iniciativa 3" == result

def test_agrega_iniciativa_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.agrega_iniciativa(database, 'entidad1', 'legislatura1', 2,
                                           'cambios', 'documento1',  '', '', '')
    assert "ok: iniciativa 2 creada" == result

def test_agrega_iniciativa_error(database):
    database.executescript(_data_sql)
    result = colabora.db.agrega_iniciativa(database, 'entidad1', 'legislatura1', 1,
                                           'cambios', 'documento1', '', '', '')
    assert "error: iniciativa 1 no creada" == result


def test_agrega_area_ok(database):
    result = colabora.db.agrega_area(database, 'area1')
    assert "ok: 'area1' creada" == result

def test_agrega_area_error(database):
    result = colabora.db.agrega_area(database, 'area1')
    result = colabora.db.agrega_area(database, 'area1')
    assert "error: 'area1' no creada" == result


def test_agrega_estado_ok(database):
    result = colabora.db.agrega_estado(database, 'estado1')
    assert "ok: 'estado1' creada" == result

def test_agrega_estado_error(database):
    result = colabora.db.agrega_estado(database, 'estado1')
    result = colabora.db.agrega_estado(database, 'estado1')
    assert "error: 'estado1' no creada" == result


def test_agrega_usuario_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.agrega_usuario(database, 'usuario5', 'contrasena5', 'rol1', 'entidad1', 'legislatura1')
    assert "ok: 'usuario5' creado" == result

def test_agrega_usuario_error(database):
    database.executescript(_data_sql)
    result = colabora.db.agrega_usuario(database, 'usuario1', 'contrasena1', 'rol1', 'entidad1', 'legislatura1')
    assert "error: 'usuario1' no creado" == result


def test_agrega_entidad_ok(database):
    result = colabora.db.agrega_entidad(database, 'entidad1')
    assert "ok: 'entidad1' creado" == result

def test_agrega_entidad_error(database):
    result = colabora.db.agrega_entidad(database, 'entidad1')
    result = colabora.db.agrega_entidad(database, 'entidad1')
    assert "error: 'entidad1' no creado" == result


def test_agrega_legislatura_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.agrega_legislatura(database, 'entidad1', 'legislatura1')
    assert "ok: 'legislatura1' creado" == result

def test_agrega_legislatura_error(database):
    result = colabora.db.agrega_legislatura(database, 'entidad1', 'legislatura1')
    result = colabora.db.agrega_legislatura(database, 'entidad1', 'legislatura1')
    assert "error: 'legislatura1' no creado" == result

def test_actualiza_iniciativa_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_iniciativa(database, 'entidad1', 'legislatura1', 1,
                                              tema='TEMA')
    assert result == 'ok: iniciativa 1 actualizada'

def test_actualiza_iniciativa_todo_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_iniciativa(database, 'entidad1', 'legislatura1', 1,
                                              tema='TEMA', resumen='RESUMEN',
                                              comentario='COMENTARIO')
    assert result == 'ok: iniciativa 1 actualizada'

def test_actualiza_iniciativa_estado(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_iniciativa(database, 'entidad1', 'legislatura1', 1,
                                              estado_id=1)
    assert result == 'ok: iniciativa 1 actualizada'

def test_actualiza_iniciativa_error(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_iniciativa(database, 'entidad1', 'legislatura1', 4,
                                              tema='TEMA')
    assert result == 'error: iniciativa 4 no actualizada'

def test_actualiza_iniciativa_omitir(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_iniciativa(database, 'entidad1', 'legislatura1', 1)
    assert result == 'error: iniciativa 1 no actualizada'

def test_actualiza_iniciativa_vacios(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_iniciativa(database, 'entidad1', 'legislatura1', 1,
                                              tema='', resumen='')
    assert result == 'ok: iniciativa 1 actualizada'

def test_actualiza_iniciativa_cambios_documento(database):
    database.executescript(_data_sql)
    result = colabora.db.actualiza_iniciativa(database, 'entidad1', 'legislatura1', 1,
                                              cambios='CAMBIOS', documento='documento1')
    assert result == 'ok: iniciativa 1 actualizada'

def test_remueve_iniciativa_ok(database):
    database.executescript(_data_sql)
    result = colabora.db.remueve_iniciativa(database, 'entidad1', 'legislatura1', 3)
    assert result == "ok: iniciativa 3 removida"

def test_remueve_inciativa_error_asignada(database):
    database.executescript(_data_sql)
    result = colabora.db.remueve_iniciativa(database, 'entidad1', 'legislatura1', 1)
    assert result == "error: iniciativa 1 no removida"

def test_remueve_inciativa_error_inexistente(database):
    database.executescript(_data_sql)
    result = colabora.db.remueve_iniciativa(database, 'entidad1', 'legislatura1', 1000)
    assert result == "error: iniciativa 1000 no removida"

def test_remueve_usuario(database):
    database.executescript(_data_sql)
    result = colabora.db.remueve_usuario(database, 4)
    assert result == "ok: usuario 4 removido"

def test_remueve_usuario_error(database):
    database.executescript(_data_sql)
    result = colabora.db.remueve_usuario(database, 1)
    assert result == "error: usuario 1 no removido"

def test_temas_creados(database):
    database.executescript(_data_sql)
    result = colabora.db.temas_creados(database)
    assert result[0][0] == "tema1"
    assert result[1][0] == "tema3"
    
def test_legislaturas(database):
    database.executescript(_data_sql)
    result = colabora.db.legislaturas(database)
    assert result == {'entidad1': [('legislatura1', 1), ('legislatura2', 2), ('legislatura3', 4)], 'entidad2': [('legislatura1', 3)]}
