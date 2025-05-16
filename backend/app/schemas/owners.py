# app/schemas/owners.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class OwnerBase(BaseModel):
    name: str
    address: str
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class OwnerCreate(OwnerBase):
    pass

class OwnerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class OwnerInDB(OwnerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Owner(OwnerInDB):
    pass