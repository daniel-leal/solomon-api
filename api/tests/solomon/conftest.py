import pytest
from fastapi.testclient import TestClient
from pytest_factoryboy import register
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from api.solomon.infrastructure.config import DATABASE_URL
from api.solomon.infrastructure.database import Base, get_db_session
from api.solomon.main import app
from api.tests.solomon.factories.user_factory import UserFactory

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db


def clear_data(engine: Engine):
    with engine.connect() as connection:
        trans = connection.begin()
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
        trans.commit()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

    # delete all data after each test
    clear_data(engine)


register(UserFactory)
