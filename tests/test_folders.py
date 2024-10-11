# tests/test_folders.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from models import Folder
from crud import create_folder

client = TestClient(app)

@pytest.fixture
def create_test_folder(db: Session, create_test_user):
    folder_data = {"name": "Test Folder"}
    folder = create_folder(db, folder_data, create_test_user.id)
    return folder


def test_create_folder(client, db):
    response = client.post("/folders/", json={"name": "Test Folder"})  # Создание папки
    assert response.status_code == 200  # Убедитесь, что папка была создана
    data = response.json()
    assert data["name"] == "Test Folder"  # Проверка корректности данных

def test_get_folder(create_test_folder):
    folder = create_test_folder
    response = client.get(f"/folders/{folder.id}")
    assert response.status_code == 200
    assert response.json()["name"] == folder.name

def test_update_folder(create_test_folder):
    folder = create_test_folder
    response = client.put(f"/folders/{folder.id}", json={"name": "Updated Folder", "description": "Updated description"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Folder"

def test_delete_folder(create_test_folder):
    folder = create_test_folder
    response = client.delete(f"/folders/{folder.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Folder deleted"
