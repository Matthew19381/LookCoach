import importlib
import os
import sys
from pathlib import Path

import pytest

# No test may reach a paid AI API: blank the keys BEFORE any module runs load_dotenv
# (load_dotenv does not override variables that already exist). A test once sent
# real OpenRouter requests with the owner's key (found 2026-09-27).
for _key in ("OPENROUTER_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
    os.environ[_key] = ""

# Add code/ (parent of backend/) to path so that 'backend' is a package
BACKEND_DIR = Path(__file__).parent.parent
CODE_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(CODE_DIR))

os.chdir(BACKEND_DIR)

create_engine = importlib.import_module("sqlalchemy").create_engine
sessionmaker = importlib.import_module("sqlalchemy.orm").sessionmaker
Base = importlib.import_module("backend.models.base").Base

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
