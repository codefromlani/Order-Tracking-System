from fastapi import APIRouter, Depends
from services import shipping_service
from sqlalchemy.orm import Session
from database import get_db
import schemas


router = APIRouter(
    tags=["Shipment"]
)

@router.post("/orders/{order_id}/shipments/")
def create_shipment(
    order_id: int,
    db: Session = Depends(get_db)
):
    return shipping_service.create_shipments(order_id=order_id, db=db)

@router.get("/shipments/{order_id}/")
def track_shipments(
    order_id: int, 
    db: Session = Depends(get_db)
):
    return shipping_service.track_shipments(order_id=order_id, db=db)

@router.patch("/shipments/{order_id}/update")
def update_shipment(
    order_id: int, 
    shipment_update: schemas.ShipmentUpdate, 
    db: Session = Depends(get_db)
):
    return shipping_service.update_shipment(order_id=order_id, shipment_update=shipment_update, db=db)