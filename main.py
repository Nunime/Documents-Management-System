from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User
from schemas import FolderCreate, FolderResponse, DocumentCreate, DocumentResponse, UserCreate, UserResponse
from crud import (
    create_folder, get_folder, get_folders, update_folder, delete_folder,
    create_document, get_document, get_documents_by_folder, update_document, delete_document,
    create_user, get_user, set_access_rights, check_access_rights, get_user_by_username
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security import create_access_token, verify_password, get_password_hash, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

# Создание экземпляра приложения FastAPI
app = FastAPI()

# Разрешаем доступ к API с фронтенда (например, с React на localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Разрешаем доступ с фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Маршруты для пользователей (User) ---

@app.post("/users/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# --- Маршруты для папок (Folder) ---

@app.post("/folders/", response_model=FolderResponse)
def create_new_folder(folder: FolderCreate, db: Session = Depends(get_db), current_user: str = "admin"):
    return create_folder(db, folder, creator=current_user)

@app.get("/folders/{folder_id}", response_model=FolderResponse)
def read_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = get_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@app.get("/folders/", response_model=List[FolderResponse])
def read_all_folders(db: Session = Depends(get_db)):
    return get_folders(db)

@app.put("/folders/{folder_id}", response_model=FolderResponse)
def update_existing_folder(folder_id: int, folder: FolderCreate, db: Session = Depends(get_db), current_user: str = "admin"):
    updated_folder = update_folder(db, folder_id, folder, modifier=current_user)
    if not updated_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return updated_folder

@app.delete("/folders/{folder_id}")
def delete_folder_by_id(folder_id: int, db: Session = Depends(get_db)):
    deleted_folder = delete_folder(db, folder_id)
    if not deleted_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"detail": "Folder deleted"}

# --- Маршруты для документов (Document) ---

@app.post("/documents/", response_model=DocumentResponse)
def upload_document(document: DocumentCreate, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: str = "admin"):
    file_path = f"files/{file.filename}"  # Определяем путь для сохранения файла
    with open(file_path, "wb") as f:
        f.write(file.file.read())  # Сохраняем файл на диск
    return create_document(db, document, file_path=file_path, creator=current_user)

@app.get("/documents/{document_id}", response_model=DocumentResponse)
def read_document(document_id: int, db: Session = Depends(get_db)):
    document = get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.get("/folders/{folder_id}/documents/", response_model=List[DocumentResponse])
def get_documents_in_folder(folder_id: int, db: Session = Depends(get_db)):
    return get_documents_by_folder(db, folder_id)

@app.put("/documents/{document_id}", response_model=DocumentResponse)
def update_existing_document(document_id: int, document: DocumentCreate, db: Session = Depends(get_db), current_user: str = "admin"):
    updated_document = update_document(db, document_id, document, modifier=current_user)
    if not updated_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated_document

@app.delete("/documents/{document_id}")
def delete_document_by_id(document_id: int, db: Session = Depends(get_db)):
    deleted_document = delete_document(db, document_id)
    if not deleted_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"detail": "Document deleted"}

# --- Маршруты для прав доступа (Access Rights) ---

@app.post("/folders/{folder_id}/access/")
def set_access(folder_id: int, user_id: int, access_level: str, db: Session = Depends(get_db), current_user: str = "admin"):
    check_access_rights(db, folder_id, current_user, "write")  # Проверяем, есть ли у текущего пользователя права на запись
    return set_access_rights(db, folder_id, user_id, access_level)

# Настраиваем OAuth2 схему
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Маршрут для логина
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Функция для получения текущего пользователя
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Пример использования JWT для защиты маршрута
@app.post("/folders/", response_model=FolderResponse)
def create_new_folder(folder: FolderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_folder(db, folder, creator=current_user.username)