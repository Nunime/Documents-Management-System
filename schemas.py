from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Базовая схема для документа (Document)
class DocumentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    folder_id: int  # Указываем ID папки, к которой привязан документ

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    creator: str
    last_modifier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Позволяет Pydantic работать с SQLAlchemy моделями


# Базовая схема для папки (Folder)
class FolderBase(BaseModel):
    name: str
    description: Optional[str] = None

class FolderCreate(FolderBase):
    parent_folder_id: Optional[int] = None  # ID родительской папки, если есть

class FolderResponse(FolderBase):
    id: int
    creator: str
    last_modifier: str
    created_at: datetime
    updated_at: datetime
    sub_folders: List['FolderResponse'] = []  # Список дочерних папок
    documents: List[DocumentResponse] = []  # Список документов в папке

    class Config:
        orm_mode = True


# Схемы для прав доступа (Access Rights)
class AccessRightBase(BaseModel):
    user_id: int
    access_level: str = Field(..., regex="^(read|write)$")  # Доступен только "read" или "write"

class AccessRightCreate(AccessRightBase):
    pass  # Эта схема используется для создания новых прав

class AccessRightResponse(AccessRightBase):
    folder_id: int

    class Config:
        orm_mode = True


# Схемы для пользователей (User)
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True
