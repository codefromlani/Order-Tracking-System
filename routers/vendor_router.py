from fastapi import APIRouter, Depends, status
from services import vendor_service
from sqlalchemy.orm import Session
from database import get_gb
from typing import List
import schemas


router = APIRouter(
    tags=["Vendor"]
)

@router.post("/vendors/", status_code=status.HTTP_201_CREATED)
def create_vendor(
    vendor: schemas.VendorCreate, 
    db: Session = Depends(get_gb)              
):
    return vendor_service.create_vendor(vendor=vendor, db=db)

@router.get("/vendors/", response_model=List[schemas.VendorResponse])
def get_vendors(
    db: Session = Depends(get_gb),
    skip: int = 0,
    limit: int = 10
):
    return vendor_service.get_vendors(db=db, skip=skip, limit=limit)

@router.patch("/vendors/{vendor_id}", response_model=schemas.VendorResponse)
def update_vendor(
    vendor_id: int,
    vendor_update: schemas.VendorUpdate,
    db: Session = Depends(get_gb)
):
    return vendor_service.update_vendor(vendor_id=vendor_id, vendor_update=vendor_update, db=db)

@router.delete("/vendors/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_gb)
):
    return vendor_service.delete_vendor(vendor_id=vendor_id, db=db)