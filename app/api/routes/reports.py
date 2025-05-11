# app/api/routes/reports.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Get counts
    document_count = db.query(models.Document).count()
    customer_count = db.query(models.Customer).count()
    task_count = db.query(models.Task).count()
    error_count = db.query(models.ErrorReport).filter(models.ErrorReport.status == "open").count()
    
    # Get recent documents
    recent_documents = db.query(models.Document).order_by(models.Document.upload_date.desc()).limit(5).all()
    
    # Get recent tasks
    recent_tasks = db.query(models.Task).order_by(models.Task.start_time.desc()).limit(5).all()
    
    # Get customer status distribution
    customer_status = db.query(
        models.Customer.status,
        db.func.count(models.Customer.id).label("count")
    ).group_by(models.Customer.status).all()
    
    customer_status_data = {status: count for status, count in customer_status}
    
    # Get task status distribution
    task_status = db.query(
        models.Task.status,
        db.func.count(models.Task.id).label("count")
    ).group_by(models.Task.status).all()
    
    task_status_data = {status: count for status, count in task_status}
    
    return {
        "counts": {
            "documents": document_count,
            "customers": customer_count,
            "tasks": task_count,
            "errors": error_count
        },
        "recent_documents": [
            {
                "id": doc.id,
                "file_name": doc.file_name,
                "document_type": doc.document_type,
                "status": doc.status,
                "upload_date": doc.upload_date
            } for doc in recent_documents
        ],
        "recent_tasks": [
            {
                "id": task.id,
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "start_time": task.start_time
            } for task in recent_tasks
        ],
        "customer_status": customer_status_data,
        "task_status": task_status_data
    }

@router.get("/customers/status", response_model=Dict[str, int])
def get_customer_status_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    customer_status = db.query(
        models.Customer.status,
        db.func.count(models.Customer.id).label("count")
    ).group_by(models.Customer.status).all()
    
    return {status: count for status, count in customer_status}

@router.get("/tasks/status", response_model=Dict[str, int])
def get_task_status_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    task_status = db.query(
        models.Task.status,
        db.func.count(models.Task.id).label("count")
    ).group_by(models.Task.status).all()
    
    return {status: count for status, count in task_status}

@router.get("/documents/monthly", response_model=Dict[str, int])
def get_monthly_document_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Get documents uploaded in the last 12 months
    now = datetime.now()
    start_date = now - timedelta(days=365)
    
    documents = db.query(
        db.func.date_trunc('month', models.Document.upload_date).label("month"),
        db.func.count(models.Document.id).label("count")
    ).filter(
        models.Document.upload_date >= start_date
    ).group_by("month").order_by("month").all()
    
    return {month.strftime("%Y-%m"): count for month, count in documents}