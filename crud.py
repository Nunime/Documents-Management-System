from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Folder, Document, User, AccessRight
from schemas import FolderCreate, DocumentCreate, UserCreate
from passlib.context import CryptContext

# Инициализация объекта для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширование пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# CRUD для пользователей (User)
def create_user(db: Session, user: UserCreate):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# CRUD для папок (Folder)
def create_folder(db: Session, folder: FolderCreate, creator: str):
    new_folder = Folder(
        name=folder.name,
        description=folder.description,
        creator=creator,
        last_modifier=creator,
        parent_folder_id=folder.parent_folder_id
    )
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder

def get_folder(db: Session, folder_id: int):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

def get_folders(db: Session):
    return db.query(Folder).all()

def update_folder(db: Session, folder_id: int, folder_data: FolderCreate, modifier: str):
    folder = get_folder(db, folder_id)
    folder.name = folder_data.name
    folder.description = folder_data.description
    folder.last_modifier = modifier
    db.commit()
    db.refresh(folder)
    return folder

def delete_folder(db: Session, folder_id: int):
    folder = get_folder(db, folder_id)
    db.delete(folder)
    db.commit()
    return folder


# CRUD для документов (Document)
def create_document(db: Session, document: DocumentCreate, file_path: str, creator: str):
    folder = get_folder(db, document.folder_id)
    new_document = Document(
        name=document.name,
        description=document.description,
        file_path=file_path,
        folder_id=document.folder_id,
        creator=creator,
        last_modifier=creator
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document

def get_document(db: Session, document_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

def get_documents_by_folder(db: Session, folder_id: int):
    return db.query(Document).filter(Document.folder_id == folder_id).all()

def update_document(db: Session, document_id: int, document_data: DocumentCreate, modifier: str):
    document = get_document(db, document_id)
    document.name = document_data.name
    document.description = document_data.description
    document.last_modifier = modifier
    db.commit()
    db.refresh(document)
    return document

def delete_document(db: Session, document_id: int):
    document = get_document(db, document_id)
    db.delete(document)
    db.commit()
    return document


# CRUD для прав доступа (AccessRight)
def set_access_rights(db: Session, folder_id: int, user_id: int, access_level: str):
    access_right = db.query(AccessRight).filter_by(folder_id=folder_id, user_id=user_id).first()
    if access_right:
        access_right.access_level = access_level
    else:
        access_right = AccessRight(folder_id=folder_id, user_id=user_id, access_level=access_level)
        db.add(access_right)
    db.commit()
    db.refresh(access_right)
    return access_right

def check_access_rights(db: Session, folder_id: int, user_id: int, required_level: str):
    access = db.query(AccessRight).filter_by(folder_id=folder_id, user_id=user_id).first()
    if not access:
        raise HTTPException(status_code=403, detail="Access Denied")
    if access.access_level != required_level and required_level == 'write':
        raise HTTPException(status_code=403, detail="Write access required")
    return access
