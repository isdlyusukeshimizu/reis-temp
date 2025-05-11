# app/schemas/tasks.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    task_type: str
    status: str = "processing"

class TaskCreate(TaskBase):
    task_id: str

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[str] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class TaskInDB(TaskBase):
    id: int
    task_id: str
    result: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Task(TaskInDB):
    pass

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None