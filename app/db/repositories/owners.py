# app/db/repositories/owners.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import models
from app.schemas.owners import OwnerCreate, OwnerUpdate

class OwnerRepository:
    def create(self, db: Session, owner_in: OwnerCreate) -> models.Owner:
        db_owner = models.Owner(
            name=owner_in.name,
            address=owner_in.address,
            postal_code=owner_in.postal_code,
            phone_number=owner_in.phone_number,
            email=owner_in.email
        )
        db.add(db_owner)
        db.commit()
        db.refresh(db_owner)
        return db_owner
    
    def get_by_id(self, db: Session, owner_id: int) -> Optional[models.Owner]:
        return db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Owner]:
        return db.query(models.Owner).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_owner: models.Owner, owner_in: OwnerUpdate) -> models.Owner:
        update_data = owner_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_owner, field, value)
        
        db.commit()
        db.refresh(db_owner)
        return db_owner
    
    def delete(self, db: Session, db_owner: models.Owner) -> None:
        db.delete(db_owner)
        db.commit()

owner_repository = OwnerRepository()