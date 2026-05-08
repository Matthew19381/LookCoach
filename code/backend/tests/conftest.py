import sys
from pathlib import Path
import pytest

# Add code/ (parent of backend/) to path so that 'backend' is a package
BACKEND_DIR = Path(__file__).parent.parent
CODE_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(CODE_DIR))

import os
os.chdir(BACKEND_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.base import Base

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
