# app/api/routes/reports.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    ダッシュボード用の集計データを返します。
    - counts: 各リソースの総件数
    - recent_documents: 最新アップロード文書 5 件
    - recent_tasks: 最新タスク実行 5 件
    - customer_status: 顧客ステータスごとの件数
    - task_status: タスクステータスごとの件数
    """

    # 各テーブルの総件数を取得
    document_count = db.query(func.count(models.Document.id)).scalar()
    customer_count = db.query(func.count(models.Customer.id)).scalar()
    task_count = db.query(func.count(models.Task.id)).scalar()
    error_count = (
        db.query(func.count(models.ErrorReport.id))
        .filter(models.ErrorReport.status == "open")
        .scalar()
    )

    # 最新アップロード文書 5 件
    recent_documents = (
        db.query(models.Document)
        .order_by(models.Document.upload_date.desc())
        .limit(5)
        .all()
    )

    # 最新タスク実行 5 件
    recent_tasks = (
        db.query(models.Task)
        .order_by(models.Task.start_time.desc())
        .limit(5)
        .all()
    )

    # 顧客ステータスごとの分布
    customer_status_rows = (
        db.query(models.Customer.status, func.count(models.Customer.id))
        .group_by(models.Customer.status)
        .all()
    )
    customer_status_data: Dict[str, int] = {
        status: count for status, count in customer_status_rows
    }

    # タスクステータスごとの分布
    task_status_rows = (
        db.query(models.Task.status, func.count(models.Task.id))
        .group_by(models.Task.status)
        .all()
    )
    task_status_data: Dict[str, int] = {
        status: count for status, count in task_status_rows
    }

    return {
        "counts": {
            "documents": document_count,
            "customers": customer_count,
            "tasks": task_count,
            "errors": error_count,
        },
        "recent_documents": [
            {
                "id": doc.id,
                "file_name": doc.file_name,
                "document_type": doc.document_type,
                "status": doc.status,
                "upload_date": doc.upload_date,
            }
            for doc in recent_documents
        ],
        "recent_tasks": [
            {
                "id": task.id,
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "start_time": task.start_time,
            }
            for task in recent_tasks
        ],
        "customer_status": customer_status_data,
        "task_status": task_status_data,
    }

@router.get("/customers/status", response_model=Dict[str, int])
def get_customer_status_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    顧客ステータスごとのレコード数を返します。
    """
    rows = (
        db.query(
            models.Customer.status,
            func.count(models.Customer.id).label("count"),
        )
        .group_by(models.Customer.status)
        .all()
    )
    return {status: count for status, count in rows}


@router.get("/tasks/status", response_model=Dict[str, int])
def get_task_status_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    タスクステータスごとのレコード数を返します。
    """
    rows = (
        db.query(
            models.Task.status,
            func.count(models.Task.id).label("count"),
        )
        .group_by(models.Task.status)
        .all()
    )
    return {status: count for status, count in rows}


@router.get("/documents/monthly", response_model=Dict[str, int])
def get_monthly_document_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    過去12か月間の月単位アップロード件数を "YYYY-MM" : count の辞書で返します。
    """
    now = datetime.utcnow()
    start_date = now - timedelta(days=365)

    rows = (
        db.query(
            func.date_trunc("month", models.Document.upload_date).label("month"),
            func.count(models.Document.id).label("count"),
        )
        .filter(models.Document.upload_date >= start_date)
        .group_by("month")
        .order_by("month")
        .all()
    )

    # month は datetime.datetime 型。%Y-%m 形式の文字列キーに変換
    return {row.month.strftime("%Y-%m"): row.count for row in rows}