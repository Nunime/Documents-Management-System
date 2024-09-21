# tests/conftest.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import Base, get_db
from main import app

# Настраиваем тестовую базу данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Фикстура для создания тестовой базы данных и сессии
@pytest.fixture(scope="function")
def db():
    # Создаём все таблицы
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db  # Передаём сессию тесту
    finally:
        db.close()  # Закрываем сессию
        Base.metadata.drop_all(bind=engine)  # Удаляем все таблицы после теста


# Фикстура для тестового клиента FastAPI
@pytest.fixture(scope="module")
def client():
    # Переопределяем зависимость get_db, чтобы использовать тестовую БД
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client  # Передаём клиент тесту

    app.dependency_overrides.clear()  # Очищаем переопределённые зависимости
