import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / 'test_academic.db'
    application = create_app(
        {
            'TESTING': True,
            'AUTO_CARREGAR_DADOS_SIMULADOS': False,
            'DATABASE_PATH': str(database_path),
            'SECRET_KEY': 'test-secret',
        }
    )
    return application


@pytest.fixture
def client(app):
    return app.test_client()
