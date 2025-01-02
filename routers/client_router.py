from fastapi import APIRouter, Depends, status
from services import client_service
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import schemas


router = APIRouter(
    tags=["Client"]
)

@router.post("/clients/", status_code=status.HTTP_201_CREATED)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db)
):
    return client_service.create_client(client=client, db=db)

@router.get("/clients/", response_model=List[schemas.ClientResponse])
def get_clients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    return client_service.get_clients(db=db, skip=skip, limit=limit)

@router.patch("/clients/{client_id}", response_model=schemas.ClientResponse)
def update_client(
    client_id: int,
    client_update: schemas.ClientUpdate,
    db: Session = Depends(get_db)
):
    return client_service.update_client(client_id=client_id, client_update=client_update, db=db)

@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    return client_service.delete_client(client_id=client_id, db=db)

@router.get("/clients/{client_id}/order_history", response_model=List[schemas.ClientOrderResponse])
def client_order_history(
    client_id: int,
    db: Session = Depends(get_db)
):
    return client_service.client_order_history(client_id=client_id, db=db)