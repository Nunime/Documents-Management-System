from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from crud import check_folder_access, check_document_access
from models import AccessLevel
from database import get_db
from passlib.context import CryptContext

def require_folder_access(access_level: AccessLevel):
    def decorator(func):
        def wrapper(folder_id: int, *args, db: Session = Depends(get_db), user_id: int = Depends(get_current_user), **kwargs):
            if not check_folder_access(db, folder_id, user_id, access_level):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return func(folder_id, *args, **kwargs)
        return wrapper
    return decorator


def require_document_access(access_level: AccessLevel):
    def decorator(func):
        def wrapper(document_id: int, *args, db: Session = Depends(get_db), user_id: int = Depends(get_current_user), **kwargs):
            if not check_document_access(db, document_id, user_id, access_level):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return func(document_id, *args, **kwargs)
        return wrapper
    return decorator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Функция для хеширования паролей"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Функция для проверки пароля"""
    return pwd_context.verify(plain_password, hashed_password)