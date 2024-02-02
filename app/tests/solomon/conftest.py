import pytest
from fastapi.testclient import TestClient
from fastapi_sqlalchemy import db
from pytest_factoryboy import register
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.solomon.auth.application.security import generate_hashed_password, verify_token
from app.solomon.infrastructure.config import DATABASE_URL
from app.solomon.infrastructure.database import Base, get_db_session
from app.solomon.main import app
from app.solomon.users.domain.models import User
from app.tests.solomon.factories.category_factory import CategoryFactory
from app.tests.solomon.factories.credit_card_factory import CreditCardFactory
from app.tests.solomon.factories.transaction_factory import TransactionCreateFactory, TransactionFactory
from app.tests.solomon.factories.user_factory import UserFactory

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


@pytest.fixture
def current_user_token(client, user_factory) -> str:
    with db():
        password = "123456"
        user = user_factory.create(
            username="John Doe", hashed_password=generate_hashed_password(password)
        )

        body = {
            "username": user.username,
            "password": password,
        }

        response = client.post("/auth/login", json=body)

        token = response.json()["access_token"]
        user = db.session.query(User).filter_by(id=user.id).first()

        return token


@pytest.fixture
def auth_client(client, current_user_token):
    token = current_user_token
    headers = {"Authorization": f"Bearer {token}"}
    with TestClient(app) as client:
        client.headers = headers
        yield client

    # delete all data after each test
    clear_data(engine)


@pytest.fixture
def current_user(current_user_token) -> User:
    with db():
        token = current_user_token
        user_id = verify_token(token)["sub"]

        user = db.session.query(User).filter_by(id=user_id).first()

        return user


register(UserFactory)
register(CreditCardFactory)
register(CategoryFactory)
register(TransactionCreateFactory)
register(TransactionFactory)
