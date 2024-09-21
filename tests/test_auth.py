# tests/test_auth.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import Session
from database import get_db
from models import User
from security import get_password_hash

client = TestClient(app)

@pytest.fixture
def create_test_user(db: Session):
    hashed_password = get_password_hash("password")
    user = User(username="testuser", email="testuser@example.com", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_login(create_test_user):
    response = client.post("/token", data={"username": "testuser", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_route_without_token():
    response = client.post("/folders/", json={"name": "Test Folder", "description": "Test description"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_with_token(create_test_user):
    response = client.post("/token", data={"username": "testuser", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/folders/", json={"name": "Test Folder", "description": "Test description"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Folder"
