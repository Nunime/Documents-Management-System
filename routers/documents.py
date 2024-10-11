# routers/documents.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from models import Document
from database import get_db
from schemas import DocumentCreate

router = APIRouter()

@router.post("/folders/{folder_id}/documents/")
def upload_document(folder_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Логика загрузки документа
    new_document = Document(name=file.filename, folder_id=folder_id)
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return {"filename": file.filename}

@router.get("/documents/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"detail": "Document deleted"}
