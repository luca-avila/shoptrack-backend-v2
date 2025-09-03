import os
import logging
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
Session = scoped_session(SessionLocal)

def init_app(app):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created")
    except SQLAlchemyError:
        logger.exception("Error while creating tables")
        raise

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception:
            logger.warning(f"Session rolled back due to exception: {exception}")
            Session.rollback()
        Session.remove()
