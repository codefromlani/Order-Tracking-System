from fastapi import APIRouter, Depends, status
from services import shipping_service, DHL_service
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import schemas


router = APIRouter(
    tags=["Shipment"]
)

@router.post("/shipments/")
async def create_shipment(
    order_id: int,
    db: Session = Depends(get_db)
):
    return await DHL_service.create_shipment(order_id=order_id, db=db)

@router.get("/orders/{order_id}/shipment/dhl")
async def get_dhl_tracking_status(
    order_id: int, 
    tracking_number: str,
    db: Session = Depends(get_db)
):
    return shipping_service.get_dhl_tracking_status(order_id=order_id, tracking_number=tracking_number, db=db)

@router.get("/orders/{order_id}/shipment/status")
async def get_shipment_status(
    order_id: int, 
    db: Session = Depends(get_db)
):
    return await shipping_service.get_shipment_status(order_id=order_id, db=db)

@router.patch("/shipment/{order_id}")
async def update_shipment(
    order_id: int, 
    shipment_update: schemas.ShipmentUpdate, 
    db: Session = Depends(get_db)
):
    return shipping_service.update_shipment(order_id=order_id, shipment_update=shipment_update, db=db)