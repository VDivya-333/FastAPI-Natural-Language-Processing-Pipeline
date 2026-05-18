import os
from urllib.parse import quote_plus
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


_engine = None
_SessionLocal = None

def get_session_local():
    """
    Lazily initializes and returns the database engine and session maker.
    This defers the access to settings and database connection until needed.
    """
    global _engine, _SessionLocal
    if _engine is None or _SessionLocal is None:
        try:
            SQLALCHEMY_DATABASE_URL = (
                f"mysql+pymysql://{settings.MYSQL_USER}:{quote_plus(settings.MYSQL_PASSWORD)}@"
                f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
            )
            _engine = create_engine(
                SQLALCHEMY_DATABASE_URL, 
                pool_pre_ping=True,
                # Ensure full UTF-8 support for NLP text processing
                connect_args={"charset": "utf8mb4"}
            )
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        except AttributeError as e:
            raise RuntimeError(f"Database configuration error: Missing attribute in settings (e.g., MYSQL_USER, MYSQL_PASSWORD). Please check app/core/config.py and environment variables. Original error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database connection: {e}") from e
    return _SessionLocal

def get_engine():
    """Returns the database engine, initializing it if necessary."""
    get_session_local()
    return _engine

def get_db():
    """Dependency to provide a database session to routes."""
    SessionLocal = get_session_local()
    db = SessionLocal() # Call the session maker to get a session
    try:
        yield db
    finally:
        db.close()
