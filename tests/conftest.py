import pytest
import os
from shoptrack import create_app
from shoptrack.database import engine, Base


@pytest.fixture(scope='session')
def app():
    """Create a test app"""

    os.environ['FLASK_ENV'] = 'testing'

    app = create_app('testing')

    with app.app_context():
        Base.metadata.create_all(bind=engine)
        yield app

        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='session')
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    """Create a test runner"""
    return app.test_runner()