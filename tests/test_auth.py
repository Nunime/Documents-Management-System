# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from security import get_password_hash
from models import User
from database import get_db

client = TestClient(app)

@pytest.fixture
def create_test_user(db: Session):
    hashed_password = get_password_hash("password")
    user = User(username="testuser", email="testuser@example.com", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_login(client, db, create_test_user):
    # Создание пользователя, если он еще не был создан
    response = client.post("/token", data={"username": "testuser", "password": "password"})
    assert response.status_code == 200  # Убедитесь, что пользователь успешно аутентифицирован
    token_data = response.json()
    assert "access_token" in token_data  # Проверка, что токен был возвращен

def test_protected_route_without_token():
    response = client.post("/folders/", json={"name": "Test Folder"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_with_token(create_test_user):
    response = client.post("/token", data={"username": "testuser", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/folders/", json={"name": "Test Folder"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Folder"
