from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from services import DHL_service
from typing import Optional
from datetime import datetime
import schemas
import models


def create_shipments():
    pass 

async def get_dhl_tracking_status(order_id: int, tracking_number: str, db: Session):
    try:
        tracking_status = await DHL_service.track_dhl_shipment(tracking_number=tracking_number)
        return {"order_id": order_id, "tracking_status": tracking_status}
    
    except HTTPException as e:
        raise e
    
async def get_shipment_status(order_id: int, db: Session):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    shipment = db.query(models.Shipment).filter(models.Shipment.order_id == order_id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    tracking_status = await DHL_service.track_dhl_shipment(shipment.tracking_number)

    shipment.status = tracking_status
    db.commit()

    return {
        "order_id": order.id,
        "shipment_status": shipment.status,
        "tracking_number": shipment.tracking_number
    }

async def update_shipment(order_id: int, shipment_update: schemas.ShipmentUpdate, db: Session):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    shipment = db.query(models.Shipment).filter(models.Shipment.order_id == order_id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    if shipment_update.tracking_number is not None:
        shipment.tracking_number=shipment_update.tracking_number

    if shipment_update.estimated_delivery_date is not None:
        shipment.estimated_delivery_date=shipment_update.estimated_delivery_date

    if shipment_update.tracking_number:
        new_status = await DHL_service.track_dhl_shipment(tracking_number=shipment_update.tracking_number)
        shipment.status = new_status

    db.commit()

    return {
        "order_id": order.id,
        "shipment_status": shipment.status,
        "tracking_number": shipment.tracking_number
    }