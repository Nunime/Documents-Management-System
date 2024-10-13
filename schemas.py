from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# Схема для пользователя (User)
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Схема для папки (Folder)
class FolderBase(BaseModel):
    name: str
    description: Optional[str] = None
    access_level: Optional[str] = Field(None, description="Access level for folder")


class FolderCreate(FolderBase):
    pass


class FolderResponse(FolderBase):
    id: int
    created_at: datetime
    created_by: int
    documents: List["DocumentResponse"] = []  # связь с документами

    class Config:
        orm_mode = True


# Схема для документа (Document)
class DocumentBase(BaseModel):
    title: str
    content: Optional[str] = None
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    created_by: int
    folder_id: int  # связь с папкой

    class Config:
        orm_mode = True


# Схемы для прав доступа (Access Rights)
class AccessRightsBase(BaseModel):
    folder_id: int
    user_id: int
    can_read: bool = True
    can_write: bool = False


class AccessRightsResponse(AccessRightsBase):
    id: int

    class Config:
        orm_mode = True
