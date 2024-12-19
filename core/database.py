from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import env

DATABASE_URL = f"postgresql://{env.POSTGRES_USER}:{env.POSTGRES_PASSWORD}@{env.POSTGRES_HOST}:{env.POSTGRES_PORT}/{env.POSTGRES_DB_NAME}"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def get_db_session():
    """
    Yields a database session for use in database operations.

    This function creates a new database session using the `SessionLocal` sessionmaker.
    It ensures that the session is properly closed after the database operations are complete.
    The session is yielded to be used within a context (e.g., for queries and transactions),
    and it will automatically be closed when the context is exited.

    Returns:
        Session: A SQLAlchemy session object that can be used to interact with the database.
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
