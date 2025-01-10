from fastapi import APIRouter, Depends, status
from services import order_service, payment_service
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import schemas
import models


router = APIRouter(
    tags=["Order"]
)

@router.get("/orders/", response_model=List[schemas.OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    return order_service.get_orders(db=db, skip=skip, limit=limit)

@router.post("/orders/", status_code=status.HTTP_201_CREATED)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    return order_service.create_order(db=db, order=order)

@router.put("/order/{order_id}/product/", response_model=schemas.OrderResponse)
def edit_order(
    order_id: int,
    order_update: schemas.OrderUpdate,
    db: Session = Depends(get_db)
):
    return order_service.edit_order(order_id=order_id, order_update=order_update, db=db)

@router.post("/orders/{order_id}/confirm_payment")
def confirm_payment(
    order_id: int, 
    payment_intent_id: str, 
    db: Session = Depends(get_db)
):
    return payment_service.update_order_status_to_approved(order_id=order_id, payment_intent_id=payment_intent_id, db=db)

@router.put("/orders/{order_id}/manual_status/")
def manual_update_order_status(
    order_id: int,
    new_status: schemas.OrderStatusEnum,
    db: Session = Depends(get_db)
):
    return order_service.manual_update_order_status(order_id=order_id, new_status=new_status, db=db)

@router.get("/order/{order_id}/status/")
def track_order_status(
    order_id: int,
    db: Session = Depends(get_db)
):
    return order_service.track_order_status(db=db, order_id=order_id)

@router.get("/orders/order_history/")
def orders_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10, 
    order_id: Optional[int] = None
):
    return order_service.orders_history(db=db, skip=skip, limit=limit, order_id=order_id)