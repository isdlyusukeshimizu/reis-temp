# app/schemas/customers.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

class CustomerBase(BaseModel):
    name: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: str
    postal_code: Optional[str] = None
    property_address: str
    property_type: Optional[str] = None
    status: str = "new"
    assigned_to: Optional[int] = None
    last_contact_date: Optional[date] = None
    next_contact_date: Optional[date] = None
    notes: Optional[str] = None
    source: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    property_address: Optional[str] = None
    property_type: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    last_contact_date: Optional[date] = None
    next_contact_date: Optional[date] = None
    notes: Optional[str] = None
    source: Optional[str] = None

class CustomerInDB(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Customer(CustomerInDB):
    pass

class CustomerActivityBase(BaseModel):
    activity_date: date
    activity_type: str
    description: str
    result: Optional[str] = None

class CustomerActivityCreate(CustomerActivityBase):
    pass

class CustomerActivityInDB(CustomerActivityBase):
    id: int
    customer_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CustomerActivity(CustomerActivityInDB):
    pass