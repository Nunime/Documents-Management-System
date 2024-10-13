# tests/conftest.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from database import get_db
from main import app
from models import Folder, Base

# Настраиваем тестовую базу данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Фикстура для создания тестовой базы данных и сессии
@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)  # Создаем таблицы для тестовой базы данных
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)  # Удаляем таблицы после тестов

# Фикстура для тестового клиента FastAPI
@pytest.fixture(scope="module")
def client():
    # Переопределяем зависимость get_db, чтобы использовать тестовую БД
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.rollback()
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client  # Передаём клиент тесту

    app.dependency_overrides.clear()  # Очищаем переопределённые зависимости

@pytest.fixture
def create_test_user(db: Session):
    from models import User
    from security import get_password_hash

    # Удаляем пользователя с таким именем, если он уже существует
    existing_user = db.query(User).filter(User.username == "testuser").first()
    if existing_user:
        db.delete(existing_user)
        db.commit()

    hashed_password = get_password_hash("password")
    user = User(username="testuser", email="testuser@example.com", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(autouse=True)
def clean_db(db: Session):
    # Очистка базы данных перед каждым тестом
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        db.execute(table.delete())
    db.commit()

@pytest.fixture
def create_test_folder(db: Session, create_test_user):
    folder = Folder(name="Test Folder", created_by=create_test_user.id)
    db.add(folder)
    db.commit()
    return folder

