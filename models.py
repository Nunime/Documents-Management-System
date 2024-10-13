from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class AccessLevel(enum.Enum):
    read = "read"
    write = "write"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Добавляем отношение к папкам
    folders = relationship("Folder", back_populates="creator", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="creator", cascade="all, delete-orphan")


class Folder(Base):
    __tablename__ = 'folders'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    access_level = Column(String, nullable=False)

    # Связь с пользователем, создавшим папку
    creator = relationship("User", back_populates="folders")
    documents = relationship('Document', back_populates='folder')


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    folder_id = Column(Integer, ForeignKey('folders.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Связь с пользователем и папкой
    folder = relationship("Folder", back_populates="documents")
    creator = relationship("User", back_populates="documents")


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
