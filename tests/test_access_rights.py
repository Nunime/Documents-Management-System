# tests/test_access_rights.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from models import User, FolderAccess
from database import get_db
from crud import create_folder

client = TestClient(app)

@pytest.fixture
def create_test_user(db: Session):
    user = User(username="test_user", email="test_user@example.com", hashed_password="password")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def create_test_folder(db: Session, create_test_user):
    folder_data = {"name": "Test Folder"}
    folder = create_folder(db, folder_data, create_test_user.id)
    return folder

def test_set_access_rights(db: Session, create_test_user, create_test_folder):
    user = create_test_user
    folder = create_test_folder

    response = client.post(f"/folders/{folder.id}/access/", json={"user_id": user.id, "access_level": "read"})
    assert response.status_code == 200

    access_right = db.query(FolderAccess).filter_by(folder_id=folder.id, user_id=user.id).first()
    assert access_right is not None
    assert access_right.access_level == "read"
