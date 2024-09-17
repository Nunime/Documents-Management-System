# tests/test_folders.py
import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import Session
from database import get_db
from models import Folder

client = TestClient(app)

@pytest.fixture
def create_test_folder(db: Session):
    folder = Folder(name="Test Folder", creator="test_user", last_modifier="test_user")
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder

def test_create_folder():
    response = client.post("/folders/", json={"name": "New Folder", "description": "A test folder"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Folder"

def test_get_folder(create_test_folder):
    folder = create_test_folder
    response = client.get(f"/folders/{folder.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == folder.name

def test_update_folder(create_test_folder):
    folder = create_test_folder
    response = client.put(f"/folders/{folder.id}", json={"name": "Updated Folder", "description": "Updated description"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Folder"

def test_delete_folder(create_test_folder):
    folder = create_test_folder
    response = client.delete(f"/folders/{folder.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Folder deleted"
