# app/api/routes/owners.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import models
from app.schemas.owners import Owner, OwnerCreate, OwnerUpdate
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Owner)
def create_owner(
    owner_in: OwnerCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
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

@router.get("/", response_model=List[Owner])
def read_owners(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    owners = db.query(models.Owner).offset(skip).limit(limit).all()
    return owners

@router.get("/{owner_id}", response_model=Owner)
def read_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    owner = db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner with ID {owner_id} not found"
        )
    return owner

@router.put("/{owner_id}", response_model=Owner)
def update_owner(
    owner_id: int,
    owner_in: OwnerUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    owner = db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner with ID {owner_id} not found"
        )
    
    # Update owner
    if owner_in.name is not None:
        owner.name = owner_in.name
    if owner_in.address is not None:
        owner.address = owner_in.address
    if owner_in.postal_code is not None:
        owner.postal_code = owner_in.postal_code
    if owner_in.phone_number is not None:
        owner.phone_number = owner_in.phone_number
    if owner_in.email is not None:
        owner.email = owner_in.email
    
    db.commit()
    db.refresh(owner)
    return owner

@router.delete("/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    owner = db.query(models.Owner).filter(models.Owner.id == owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner with ID {owner_id} not found"
        )
    
    db.delete(owner)
    db.commit()
    return {"ok": True}