import os
import sys
import tempfile
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

os.environ["DATA_MODE"] = "mock"
os.environ["ENABLE_SEED_DATA"] = "true"
os.environ["ENABLE_REAL_COLLECTION"] = "false"
os.environ["SIMULATOR_ENABLED"] = "true"

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base, get_db, engine as app_engine
from app.main import app
from app.services.seed_service import run_full_seed
from app.models.models import Category, Component

TEST_ENGINE = create_engine(
    f"sqlite:///{_db_path}",
    connect_args={"check_same_thread": False},
)
TEST_SESSION = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TEST_SESSION()
    try:
        if db.query(Category).count() == 0:
            run_full_seed(db)
    finally:
        db.close()
    yield
    TEST_ENGINE.dispose()
    app_engine.dispose()
    os.close(_db_fd)
    os.remove(_db_path)


def override_get_db():
    db = TEST_SESSION()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture(scope="session")
def db():
    session = TEST_SESSION()
    yield session
    session.close()


@pytest.fixture(scope="session")
def sample_component(db):
    component = db.query(Component).first()
    assert component is not None, "No seeded components available"
    return component


@pytest.fixture(scope="session")
def category_id(db):
    category = db.query(Category).first()
    assert category is not None, "No seeded categories available"
    return category.id