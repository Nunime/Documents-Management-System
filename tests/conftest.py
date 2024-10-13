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
from models import Folder, Base, User
from auth import get_password_hash
from datetime import datetime, timezone



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
    hashed_password = get_password_hash("unique_password")
    user = User(
        username="testuser_" + str(datetime.now(timezone.utc)),
        email="uniqueuser@example.com",
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # обновление объекта, чтобы получить его ID
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
    folder = Folder(
        name="Test Folder",
        created_by=create_test_user.id,  # Передаем ID созданного пользователя
        created_at=datetime.now(timezone.utc),
        access_level=1  # Указываем корректное значение для access_level
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)  # Обновляем объект, чтобы получить его ID и другие данные
    return folder

