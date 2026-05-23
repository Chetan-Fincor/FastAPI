from TodoApp.models import Users, Todos
from TodoApp.database import Base
from TodoApp.main import app

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient
import pytest

from TodoApp.routers.auth import bcrypt_context
from TodoApp.routers.todos import get_db, get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {
        'username': 'chetan',
        'user_id': 1,
        'user_role': 'admin'
    }


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="LastAPI",
        description="Because its not fast enough!",
        priority=5,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo)

    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username='chetan',
        email='chetan@localhost',
        first_name='chetan',
        last_name='roby',
        hashed_password=bcrypt_context.hash('testpassword'),
        role='admin',
        phone_number='1234567890'
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()