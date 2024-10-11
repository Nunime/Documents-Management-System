from sqlalchemy.orm import Session
from models import Folder, Document, User, AccessLevel, FolderAccess, DocumentAccess
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, password: str, email: str):
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def check_folder_access(db: Session, folder_id: int, user_id: int, required_level: AccessLevel):
    access = db.query(FolderAccess).filter(
        FolderAccess.folder_id == folder_id,
        FolderAccess.user_id == user_id,
        FolderAccess.access_level == required_level
    ).first()
    return access is not None


def check_document_access(db: Session, document_id: int, user_id: int, required_level: AccessLevel):
    access = db.query(DocumentAccess).filter(
        DocumentAccess.document_id == document_id,
        DocumentAccess.user_id == user_id,
        DocumentAccess.access_level == required_level
    ).first()
    return access is not None


def create_folder(db: Session, folder_data, user_id: int):
    new_folder = Folder(**folder_data, created_by=user_id)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    db.add(FolderAccess(user_id=user_id, folder_id=new_folder.id, access_level=AccessLevel.write))
    db.commit()
    return new_folder


def create_document(db: Session, document_data, user_id: int):
    new_document = Document(**document_data, created_by=user_id)
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    db.add(DocumentAccess(user_id=user_id, document_id=new_document.id, access_level=AccessLevel.write))
    db.commit()
    return new_document


def update_folder(db: Session, folder_id: int, folder_data, user_id: int):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder and folder.created_by == user_id:
        for key, value in folder_data.items():
            setattr(folder, key, value)
        db.commit()
        db.refresh(folder)
        return folder
    return None


def update_document(db: Session, document_id: int, document_data, user_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document and document.created_by == user_id:
        for key, value in document_data.items():
            setattr(document, key, value)
        db.commit()
        db.refresh(document)
        return document
    return None


def delete_folder(db: Session, folder_id: int, user_id: int):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder and folder.created_by == user_id:
        db.delete(folder)
        db.commit()
        return True
    return False


def delete_document(db: Session, document_id: int, user_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document and document.created_by == user_id:
        db.delete(document)
        db.commit()
        return True
    return False
