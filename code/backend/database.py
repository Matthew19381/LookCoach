from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os

# Load the single root-level .env (same source as main.py — no CWD ambiguity)
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./looks_optimizer.db")

# Anchor relative SQLite paths to this file's directory so the DB location is
# identical no matter which CWD the app/alembic/tests are launched from.
if DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith("sqlite:////"):
    _db_file = DATABASE_URL.removeprefix("sqlite:///")
    if not Path(_db_file).is_absolute():
        DATABASE_URL = f"sqlite:///{Path(__file__).parent / _db_file}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from .models.base import Base

    Base.metadata.create_all(bind=engine)
