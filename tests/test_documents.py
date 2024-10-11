# tests/test_documents.py
import pytest
from fastapi.testclient import TestClient
from crud import create_folder
from main import app

client = TestClient(app)

def test_create_document(client, db, create_test_folder):
    response = client.post(f"/documents/{create_test_folder.id}/", json={"name": "Test Document"})
    assert response.status_code == 200  # Проверяем, что документ был успешно создан
    data = response.json()
    assert data["name"] == "Test Document"

def test_upload_document(client, db):
    # Создаём папку, в которой будем загружать документ
    folder_data = {"name": "Test Folder"}
    folder = create_folder(db, folder_data, user_id=1)

    # Загружаем документ
    with open("tests/test_file.txt", "w") as f:
        f.write("This is a test document.")

    with open("tests/test_file.txt", "rb") as file:
        response = client.post(f"/folders/{folder.id}/documents/", files={"file": file})

    assert response.status_code == 200

def test_get_document():
    response = client.get("/documents/1")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data

def test_download_document():
    response = client.get("/documents/download/1")
    assert response.status_code == 200
    assert "application/octet-stream" in response.headers["content-type"]

def test_delete_document():
    response = client.delete("/documents/1")
    assert response.status_code == 200
    assert response.json()["detail"] == "Document deleted"
