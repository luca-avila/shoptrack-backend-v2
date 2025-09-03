import os
import logging
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Engine creation
database_url = os.getenv("DATABASE_URL", "sqlite:///shoptrack.db")
safe_url = database_url.split('@')[-1] if "@" in database_url else database_url
logger.info(f"Connecting to database: {safe_url}")

try:
    engine = create_engine(database_url, echo=False, future=True)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.exception("Failed to create database engine")
    raise

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
ScopedSession = scoped_session(SessionLocal)

def init_app(app):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created")
    except SQLAlchemyError:
        logger.exception("Error while creating tables")
        raise

    @app.before_request
    def create_session():
        g.db = ScopedSession()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = g.pop('db', None)
        if db is not None:
            if exception:
                logger.warning(f"Session rolled back due to exception: {exception}")
                db.rollback()
            db.close()
            ScopedSession.remove()
