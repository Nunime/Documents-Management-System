# tests/test_documents.py
import sys
import os

from crud import create_folder

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_document(client, db):
    # Создаём папку, в которой будем загружать документ
    folder = create_folder(db, name="Test Folder", description="Test folder")

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
