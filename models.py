from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class AccessLevel(enum.Enum):
    read = "read"
    write = "write"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))  # Добавляем столбец created_by
    created_at = Column(String)
    access_level = Column(String)

    user = relationship("User", back_populates="folders")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

    access_level = Column(Enum(AccessLevel), default=AccessLevel.read)
    allowed_users = relationship("User", secondary="document_access")


# Ассоциативные таблицы для прав доступа
class FolderAccess(Base):
    __tablename__ = "folder_access"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), primary_key=True)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.read)


class DocumentAccess(Base):
    __tablename__ = "document_access"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.read)
