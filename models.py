from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Модель пользователя (User)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=True)

    # Отношения с правами доступа
    access_rights = relationship("AccessRight", back_populates="user")

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Модель папки (Folder)
class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    creator = Column(String)  # Можно заменить на ForeignKey к User, если нужно отслеживать пользователя
    last_modifier = Column(String)

    parent_folder_id = Column(Integer, ForeignKey('folders.id'), nullable=True)  # Родительская папка
    parent_folder = relationship("Folder", remote_side=[id], back_populates="sub_folders")
    sub_folders = relationship("Folder", back_populates="parent_folder", cascade="all, delete-orphan")

    # Отношения с документами
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Права доступа
    access_rights = relationship("AccessRight", back_populates="folder")


# Модель документа (Document)
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)  # Путь к файлу в файловой системе
    creator = Column(String)  # Можно заменить на ForeignKey к User
    last_modifier = Column(String)

    folder_id = Column(Integer, ForeignKey('folders.id'))
    folder = relationship("Folder", back_populates="documents")

    # Временные метки
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.utcnow)


# Модель прав доступа (AccessRight)
class AccessRight(Base):
    __tablename__ = "access_rights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    folder_id = Column(Integer, ForeignKey('folders.id'))
    access_level = Column(String)  # 'read' или 'write'

    user = relationship("User", back_populates="access_rights")
    folder = relationship("Folder", back_populates="access_rights")

# Если нужны миграции базы данных с Alembic, не забудьте зарегистрировать все модели:
# Base.metadata.create_all(bind=engine) в database.py
