from fastapi import APIRouter, Depends, status
from services import product_service
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import schemas


router = APIRouter(
    tags=["Product"]
)

@router.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db)
):
    return product_service.create_product(product=product, db=db)

@router.get("/products/", response_model=List[schemas.ProductResponse])
def get_products(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 10
):
    return product_service.get_products(db=db, skip=skip, limit=limit)

@router.patch("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    return product_service.update_product(product_id=product_id, product_update=product_update, db=db)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    return product_service.delete_product(product_id=product_id, db=db)

@router.get("/products/{product_id}/availability")
def product_availability(
    product_id: int,
    db: Session = Depends(get_db)
):
    return product_service.product_availability(product_id=product_id, db=db)