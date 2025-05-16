# app/api/routes/documents.py
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from datetime import datetime

from app.db.database import get_db
from app.db import models
from app.schemas.documents import Document, DocumentCreate, DocumentUpdate, ProcessingResult
from app.schemas.tasks import Task, TaskCreate, TaskStatus
from app.core.security import get_current_active_user
from app.api.dependencies import get_document, get_task
from app.services.pdf_processing import run_pipeline

from app.db.database import SessionLocal

router = APIRouter()

@router.post("/upload", response_model=Document)
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    Path(output_dir).mkdir(exist_ok=True)
    
    # ① ファイル保存
    file_path = os.path.join(output_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # ② Document レコード作成(status は pending などに)
    db_document = models.Document(
        file_name=file.filename,
        file_path=file_path,
        document_type=document_type,
        uploaded_by=current_user.id,
        status="pending"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.get("/", response_model=List[Document])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=Document)
def read_document(
    document: models.Document = Depends(get_document)
):
    return document

@router.put("/{document_id}", response_model=Document)
def update_document(
    document_in: DocumentUpdate,
    document: models.Document = Depends(get_document),
    db: Session = Depends(get_db)
):
    # Update document
    if document_in.file_name is not None:
        document.file_name = document_in.file_name
    if document_in.document_type is not None:
        document.document_type = document_in.document_type
    if document_in.status is not None:
        document.status = document_in.status
    if document_in.processing_status is not None:
        document.processing_status = document_in.processing_status
    if document_in.error_message is not None:
        document.error_message = document_in.error_message
    
    db.commit()
    db.refresh(document)
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document: models.Document = Depends(get_document),
    db: Session = Depends(get_db)
):
    db.delete(document)
    db.commit()
    return {"ok": True}

@router.post("/{document_id}/process", response_model=TaskStatus)
def process_document(
    background_tasks: BackgroundTasks,
    document: models.Document = Depends(get_document),
    db: Session = Depends(get_db)
):
    # Create task record
    task_id = str(uuid.uuid4())
    db_task = models.Task(
        task_id=task_id,
        task_type="pdf_processing",
        status="queued"
    )
    db.add(db_task)
    db.commit()
    
    # Start background task
    background_tasks.add_task(
        process_document_task,
        document.id,
        task_id,
    )
    
    return TaskStatus(
        task_id=task_id,
        status="queued",
        message="Document processing has been queued"
    )


def process_document_task(document_id: int, task_id: str):
    """
    バックグラウンドで呼ばれる関数。
    自前で DB セッションを切り、OCR→CSV→DB 更新を行います。
    """
    db = SessionLocal()
    try:
        # 1) Document が存在するか確認
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
            if task:
                task.status = "failed"
                task.error_message = f"Document with ID {document_id} not found"
                db.commit()
            return

        # 2) Task ステータスを「processing」に更新
        task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
        if task:
            task.status = "processing"
            db.commit()

        # 3) 実際のパイプライン処理（OCR など）
        result = run_pipeline(document.file_path, task_id)

        # 4) Document のステータス更新
        document.processing_status = "completed"
        document.status = "processed"
        document.processed_at = datetime.utcnow()
        db.commit()

        # 5) Task のステータス更新
        if task:
            task.status = "completed"
            task.result = str(result)
            task.end_time = datetime.utcnow()
            db.commit()

    except Exception as e:
        # 失敗時のハンドリング
        # Document 側
        doc = db.query(models.Document).filter(models.Document.id == document_id).first()
        if doc:
            doc.processing_status = "failed"
            doc.error_message = str(e)
            db.commit()

        # Task 側
        task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.end_time = datetime.utcnow()
            db.commit()

    finally:
        # 最後に必ずセッションを閉じる
        db.close()

@router.get("/task/{task_id}", response_model=TaskStatus)
def get_task_status(
    task: models.Task = Depends(get_task)
):
    result = None
    if task.result:
        try:
            import json
            result = json.loads(task.result.replace("'", "\""))
        except:
            result = {"raw_result": task.result}
    
    return TaskStatus(
        task_id=task.task_id,
        status=task.status,
        message=f"Task is {task.status}",
        result=result
    )