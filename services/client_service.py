from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import schemas
import models


def create_client(client: schemas.ClientCreate, db: Session) -> models.Client:
    db_client = db.query(models.Client).filter(
        models.Client.email == client.email
    ).first()
    if db_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client already exists"
        )
    
    new_client = models.Client(
        name=client.name,
        email=client.email,
        phone_number=client.phone_number
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client

def get_clients(db: Session, skip: int = 0, limit: int = 10) -> List[models.Client]:
    db_clients = db.query(models.Client).offset(skip).limit(limit).all()
    if not db_clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clients not found"
        )
     
    return db_clients

def update_client(client_id: int, client_update: schemas.ClientUpdate, db: Session) -> Optional[models.Client]:
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if client_update.name is not None:
        db_client.name=client_update.name

    if client_update.email is not None:
        db_client.email=client_update.email

    if client_update.phone_number is not None:
        db_client.phone_number=client_update.phone_number

    db.commit()

    return db_client

def delete_client(client_id: int, db: Session) -> None:
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db.delete(db_client)
    db.commit()

    return {"message": "Client deleted successfully"}

def client_order_history(client_id: int, db: Session) -> List[schemas.ClientOrderResponse]:
    """Retrieve order history for a specific client including related products"""
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    orders = (db.query(models.Order)
              .filter(models.Order.client_id == client_id)
              .options(joinedload(models.Order.order_product)
                       .joinedload(models.OrderProduct.product))
              .all())
    
    result = []
    for order in orders:
        products = [op.product for op in order.order_product]
        
        order_response = schemas.ClientOrderResponse(
            id=order.id,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at,
            products=[
                schemas.ProductBase(
                    name=product.name,
                    description=product.description,
                    price=product.price
                ) for product in products
            ]
        )
        result.append(order_response)
    
    return result