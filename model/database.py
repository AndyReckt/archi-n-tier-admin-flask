from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from model.sa_model import Base

# Create database engine
db_path = os.environ.get("DATABASE_URL", "sqlite:///game.db")
engine = create_engine(db_path)

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def get_db_session():
    """Returns a new database session"""
    return Session()


def close_db_session():
    """Removes the current database session"""
    Session.remove()
