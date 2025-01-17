from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas


def create_vendor(vendor: schemas.VendorCreate, db: Session) -> models.Vendor:
    db_vendor = db.query(models.Vendor).filter(
        models.Vendor.name == vendor.name,
        models.Vendor.email == vendor.email
    ).first()
    
    if db_vendor:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vendor already exists"
        )
    
    new_vendor = models.Vendor(
        name=vendor.name,
        email=vendor.email,
        phone_number=vendor.phone_number,
        address=vendor.address,
        type=vendor.type,
        is_deleted = vendor.is_deleted
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return new_vendor

def get_vendors(db: Session, skip: int = 0, limit: int = 10) -> List[models.Vendor]:
    db_vendors = db.query(models.Vendor).offset(skip).limit(limit).all()
    if not db_vendors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor Not found"
        )
    return db_vendors

def update_vendor(vendor_id: int, vendor_update: schemas.VendorUpdate, db: Session) -> Optional[models.Vendor]:
    db_vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor Not found"
        )
    
    if vendor_update.name is not None:
        db_vendor.name=vendor_update.name

    if vendor_update.email is not None:
        db_vendor.email=vendor_update.email

    if vendor_update.phone_number is not None:
        db_vendor.phone_number=vendor_update.phone_number

    if vendor_update.address is not None:
        db_vendor.address=vendor_update.address

    db.commit()
    return db_vendor

def delete_vendor(vendor_id: int, db: Session) -> None:
    db_vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()

    if db_vendor:
        db_vendor.is_deleted = True

        for vendor in db_vendor.products:
            vendor.vendor_id = None

        db.commit()

        return {"message": "Vendor marked as deleted and products updated"}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor Not found"
        )

    