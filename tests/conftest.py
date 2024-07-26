import os
import tempfile

import pytest
import colabora.views
from colabora.app import app as appli
from colabora.db import get_db, init_db


def mock_generate_password_hash(password):
    return password + ':hashed'


def mock_check_password_hash(hash, password):
    return hash == password + ':hashed'


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode()


@pytest.fixture
def app():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(colabora.views, 'generate_password_hash',
                        mock_generate_password_hash)
    monkeypatch.setattr(colabora.views, 'check_password_hash',
                        mock_check_password_hash)

    db_fd, db_path = tempfile.mkstemp()
    print(db_fd, db_path)

    appli.config['DATABASE'] = db_path
    appli.testing = True
    with appli.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield appli

    monkeypatch.undo()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
