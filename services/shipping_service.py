from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import uuid4
import schemas
import models


def create_shipments(order_id: int, db: Session):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != schemas.OrderStatusEnum.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Order must be approved to ship"
        )
    
    tracking_number = str(uuid4())

    estimated_delivery_date = datetime.utcnow() + timedelta(days=30)

    shipment = models.Shipment(
        order_id=order.id,
        tracking_number=tracking_number,
        status=schemas.ShipmentStatusEnum.PENDING,
        estimated_delivery_date=estimated_delivery_date
    )

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    return {
    "message": "Shipment created successfully",
    "shipment": {
        "order_id": shipment.order_id,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "estimated_delivery_date": shipment.estimated_delivery_date
    }
}

def track_shipments(order_id: int, db: Session):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    shipment = db.query(models.Shipment).filter(models.Shipment.tracking_number).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracking number not found for this order."
        )

    return {"tracking_number": shipment.tracking_number, "status": shipment.status}

def update_shipment(order_id: int, shipment_update: schemas.ShipmentUpdate, db: Session):
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
    
    if shipment_update.status is not None:
        shipment.status=shipment_update.status
    
    if shipment_update.tracking_number is not None:
        shipment.tracking_number=shipment_update.tracking_number

    if shipment_update.estimated_delivery_date is not None:
        shipment.estimated_delivery_date=shipment_update.estimated_delivery_date

    db.commit()

    return {
    "message": "Shipment updated successfully",
    "updated_shipment": {
        "order_id": shipment.order_id,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "estimated_delivery_date": shipment.estimated_delivery_date
    }
}
#8faf8d87-b7b9-470d-bb32-99dbea4fa5cd