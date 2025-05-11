# app/db/repositories/documents.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db import models
from app.schemas.documents import DocumentCreate, DocumentUpdate

class DocumentRepository:
    def create(self, db: Session, document_in: DocumentCreate, file_path: str, user_id: int) -> models.Document:
        db_document = models.Document(
            file_name=document_in.file_name,
            file_path=file_path,
            document_type=document_in.document_type,
            uploaded_by=user_id
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    def get_by_id(self, db: Session, document_id: int) -> Optional[models.Document]:
        return db.query(models.Document).filter(models.Document.id == document_id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Document]:
        return db.query(models.Document).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_document: models.Document, document_in: DocumentUpdate) -> models.Document:
        update_data = document_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_document, field, value)
        
        db.commit()
        db.refresh(db_document)
        return db_document
    
    def delete(self, db: Session, db_document: models.Document) -> None:
        db.delete(db_document)
        db.commit()
    
    def update_processing_status(
        self, 
        db: Session, 
        db_document: models.Document, 
        status: str, 
        error_message: Optional[str] = None
    ) -> models.Document:
        db_document.processing_status = status
        if status == "completed":
            db_document.status = "processed"
            db_document.processed_at = datetime.now()
        elif status == "failed":
            db_document.status = "error"
            db_document.error_message = error_message
        
        db.commit()
        db.refresh(db_document)
        return db_document

document_repository = DocumentRepository()