from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas


def create_product(product: schemas.ProductCreate, db: Session) -> models.Product:
    db_product = db.query(models.Product).filter(
        models.Product.name == product.name,
        models.Product.vendor_id == product.vendor_id
    ).first()

    if db_product:
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists"
        )
    
    new_product = models.Product(
         name = product.name,
         description=product.description,
         price=product.price,
         stock=product.stock,
         category=product.category,
         vendor_id=product.vendor_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

def get_products(db: Session, skip: int = 0, limit: int = 10) -> List[models.Product]:
    db_products = db.query(models.Product).offset(skip).limit(limit).all()
    if not db_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Products Not found"
          )
    return db_products

def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session) -> Optional[models.Product]:
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not found"
          )
    
    if product_update.name is not None:
        db_product.name=product_update.name
        
    if product_update.description is not None:
        db_product.description=product_update.description

    if product_update.price is not None:
        db_product.price=product_update.price

    if product_update.stock is not None:
        db_product.stock=product_update.stock   

    if product_update.category is not None:
        db_product.category=product_update.category 

    if product_update.vendor_id is not None:
        db_product.vendor_id=product_update.vendor_id    

    db.commit()

    return db_product

def delete_product(product_id: int, db: Session) -> None:
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not found"
          )
    
    db.delete(db_product)
    db.commit()

    return {"message": "Product deleted successfully"}

def product_availability(product_id: int, db: Session) -> dict:
    available_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not available_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not found"
          )
    
    if available_product.stock > 0:
        return {"status": "available", "product": available_product}
    else:
        return {"message": f"Product with the ID {product_id} is out of stock and needs to be ordered"}