import pytest
import os
from shoptrack import create_app
from shoptrack.database import engine, Base


@pytest.fixture(scope='function')
def app():
    """Create a test app for each test function"""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        # Create fresh tables for each test
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        yield app
        # Clean up after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a test database session"""
    from shoptrack.database import ScopedSession
    session = ScopedSession()
    yield session
    session.rollback()
    session.close()
    ScopedSession.remove()