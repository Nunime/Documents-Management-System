from auth import get_current_user
from crud import create_folder, create_document, create_user, update_folder, update_document, delete_folder, delete_document
from schemas import FolderCreate, DocumentCreate, UserCreate
from security import require_folder_access, require_document_access
from database import Base, engine
from models import AccessLevel
from routers import folders, documents
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from auth import authenticate_user, create_access_token
from datetime import timedelta
from fastapi import HTTPException, status


app = FastAPI()

# Регистрация маршрутов
app.include_router(folders.router)
app.include_router(documents.router)

Base.metadata.create_all(bind=engine)

@app.post("/users/")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user.username, user.password, user.email)
    return db_user


@app.post("/folders/")
def create_new_folder(folder: FolderCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_folder(db, folder, user_id)

@app.post("/documents/{folder_id}/")
@require_folder_access(access_level=AccessLevel.write)
def create_new_document(folder_id: int, document: DocumentCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_document(db, document, user_id)

@app.put("/folders/{folder_id}")
@require_folder_access(access_level=AccessLevel.write)
def update_folder_details(folder_id: int, folder: FolderCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_folder = update_folder(db, folder_id, folder.dict(), user_id)
    if updated_folder:
        return updated_folder
    raise HTTPException(status_code=404, detail="Folder not found or not enough permissions")

@app.put("/documents/{document_id}")
@require_document_access(access_level=AccessLevel.write)
def update_document_details(document_id: int, document: DocumentCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_document = update_document(db, document_id, document.dict(), user_id)
    if updated_document:
        return updated_document
    raise HTTPException(status_code=404, detail="Document not found or not enough permissions")


@app.delete("/folders/{folder_id}")
@require_folder_access(access_level=AccessLevel.write)
def delete_folder_endpoint(folder_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    if delete_folder(db, folder_id, user_id):
        return {"message": "Folder deleted"}
    raise HTTPException(status_code=404, detail="Folder not found or not enough permissions")


@app.delete("/documents/{document_id}")
@require_document_access(access_level=AccessLevel.write)
def delete_document_endpoint(document_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    if delete_document(db, document_id, user_id):
        return {"message": "Document deleted"}
    raise HTTPException(status_code=404, detail="Document not found or not enough permissions")

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}