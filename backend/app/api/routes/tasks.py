# app/api/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import models
from app.schemas.tasks import Task, TaskStatus
from app.core.security import get_current_active_user
from app.api.dependencies import get_task

router = APIRouter()

@router.get("/", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskStatus)
def read_task(
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