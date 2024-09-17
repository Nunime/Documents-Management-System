# tests/test_documents.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_document():
    with open("tests/test_file.txt", "w") as f:
        f.write("This is a test document.")

    with open("tests/test_file.txt", "rb") as file:
        response = client.post("/upload/", files={"file": file})
    assert response.status_code == 200
    assert response.json()["filename"] == "test_file.txt"


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
