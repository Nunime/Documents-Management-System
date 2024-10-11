from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class FolderCreate(BaseModel):
    name: str
    created_at: Optional[datetime] = None


class DocumentCreate(BaseModel):
    name: str
    folder_id: int
    created_at: Optional[datetime] = None

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
