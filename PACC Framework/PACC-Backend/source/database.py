from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from os import environ

# Sqlite3 Environmental variables
SQLITE_DB_PATH = environ['SQLITE_DB_PATH']

# Sqlalchemy Environmental variables
SQLALCHEMY_DATABASE_URL = "sqlite:///"+SQLITE_DB_PATH

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

