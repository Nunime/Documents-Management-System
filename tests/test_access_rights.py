# tests/test_access_rights.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import Session
from database import get_db
from models import User, Folder, AccessRight

client = TestClient(app)

@pytest.fixture
def create_test_user(db: Session):
    user = User(username="test_user", email="test_user@example.com", hashed_password="password")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def create_test_folder(db: Session):
    folder = Folder(name="Test Folder", creator="test_user", last_modifier="test_user")
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder

def test_set_access_rights(create_test_user, create_test_folder):
    user = create_test_user
    folder = create_test_folder

    response = client.post(f"/folders/{folder.id}/access/", json={"user_id": user.id, "access_level": "read"})
    assert response.status_code == 200

    db: Session = next(get_db())
    access_right = db.query(AccessRight).filter_by(folder_id=folder.id, user_id=user.id).first()
    assert access_right is not None
    assert access_right.access_level == "read"
