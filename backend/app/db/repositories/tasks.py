# app/db/repositories/tasks.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db import models
from app.schemas.tasks import TaskCreate, TaskUpdate

class TaskRepository:
    def create(self, db: Session, task_in: TaskCreate) -> models.Task:
        db_task = models.Task(
            task_id=task_in.task_id,
            task_type=task_in.task_type,
            status=task_in.status
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def get_by_id(self, db: Session, task_id: str) -> Optional[models.Task]:
        return db.query(models.Task).filter(models.Task.task_id == task_id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Task]:
        return db.query(models.Task).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_task: models.Task, task_in: TaskUpdate) -> models.Task:
        update_data = task_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def update_status(
        self, 
        db: Session, 
        db_task: models.Task, 
        status: str, 
        result: Optional[str] = None, 
        error_message: Optional[str] = None
    ) -> models.Task:
        db_task.status = status
        if status in ["completed", "failed"]:
            db_task.end_time = datetime.now()
        
        if result is not None:
            db_task.result = result
        
        if error_message is not None:
            db_task.error_message = error_message
        
        db.commit()
        db.refresh(db_task)
        return db_task

task_repository = TaskRepository()