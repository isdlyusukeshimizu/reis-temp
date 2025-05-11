# app/api/routes/customers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import models
from app.schemas.customers import Customer, CustomerCreate, CustomerUpdate, CustomerActivity, CustomerActivityCreate
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Customer)
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_customer = models.Customer(
        name=customer_in.name,
        phone_number=customer_in.phone_number,
        email=customer_in.email,
        address=customer_in.address,
        postal_code=customer_in.postal_code,
        property_address=customer_in.property_address,
        property_type=customer_in.property_type,
        status=customer_in.status,
        assigned_to=customer_in.assigned_to,
        last_contact_date=customer_in.last_contact_date,
        next_contact_date=customer_in.next_contact_date,
        notes=customer_in.notes,
        source=customer_in.source
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[Customer])
def read_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=Customer)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    return customer

@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    # Update customer
    for key, value in customer_in.dict(exclude_unset=True).items():
        setattr(customer, key, value)
    
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    db.delete(customer)
    db.commit()
    return {"ok": True}

@router.post("/{customer_id}/activities", response_model=CustomerActivity)
def create_customer_activity(
    customer_id: int,
    activity_in: CustomerActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    db_activity = models.CustomerActivity(
        customer_id=customer_id,
        activity_date=activity_in.activity_date,
        activity_type=activity_in.activity_type,
        description=activity_in.description,
        result=activity_in.result,
        created_by=current_user.id
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Update customer last_contact_date
    customer.last_contact_date = activity_in.activity_date
    db.commit()
    
    return db_activity

@router.get("/{customer_id}/activities", response_model=List[CustomerActivity])
def read_customer_activities(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    activities = db.query(models.CustomerActivity).filter(
        models.CustomerActivity.customer_id == customer_id
    ).offset(skip).limit(limit).all()
    
    return activities