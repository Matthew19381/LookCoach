from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os

# Load the single root-level .env (same source as main.py — no CWD ambiguity)
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./looks_optimizer.db")

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
    from .models.user import User
    from .models.profile import UserProfile
    from .models.photo import Photo
    from .models.analysis import Analysis
    from .models.recommendation import Recommendation
    from .models.progress import ProgressLog

    Base.metadata.create_all(bind=engine)
