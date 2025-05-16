# app/db/repositories/customers.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db import models
from app.schemas.customers import CustomerCreate, CustomerUpdate, CustomerActivityCreate

class CustomerRepository:
    def create(self, db: Session, customer_in: CustomerCreate) -> models.Customer:
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
    
    def get_by_id(self, db: Session, customer_id: int) -> Optional[models.Customer]:
        return db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
        return db.query(models.Customer).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_customer: models.Customer, customer_in: CustomerUpdate) -> models.Customer:
        update_data = customer_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    def delete(self, db: Session, db_customer: models.Customer) -> None:
        db.delete(db_customer)
        db.commit()
    
    def create_activity(
        self, 
        db: Session, 
        customer_id: int, 
        activity_in: CustomerActivityCreate, 
        user_id: int
    ) -> models.CustomerActivity:
        db_activity = models.CustomerActivity(
            customer_id=customer_id,
            activity_date=activity_in.activity_date,
            activity_type=activity_in.activity_type,
            description=activity_in.description,
            result=activity_in.result,
            created_by=user_id
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        
        # Update customer last_contact_date
        customer = self.get_by_id(db, customer_id)
        if customer:
            customer.last_contact_date = activity_in.activity_date
            db.commit()
        
        return db_activity
    
    def get_activities(
        self, 
        db: Session, 
        customer_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.CustomerActivity]:
        return db.query(models.CustomerActivity).filter(
            models.CustomerActivity.customer_id == customer_id
        ).offset(skip).limit(limit).all()

customer_repository = CustomerRepository()