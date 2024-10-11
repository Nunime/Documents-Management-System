# routers/folders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Folder
from database import get_db
from schemas import FolderCreate

router = APIRouter()

@router.post("/folders/")
def create_folder(folder: FolderCreate, db: Session = Depends(get_db)):
    new_folder = Folder(name=folder.name)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder

@router.get("/folders/{folder_id}")
def get_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    db.delete(folder)
    db.commit()
    return {"detail": "Folder deleted"}
