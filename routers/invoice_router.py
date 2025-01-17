from fastapi import APIRouter, Depends
from services import invoice_service
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import schemas


router = APIRouter(
    tags=["Invoice"]
)

@router.get("/invoices/{order_id}", response_model=schemas.InvoiceResponse)
def generate_invoice(
    order_id: int,
    db: Session = Depends(get_db)
):
    return invoice_service.generate_invoice(order_id=order_id, db=db)

@router.get("/invoices/", response_model=List[schemas.InvoiceResponse])
def get_invoices(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    return invoice_service.get_invoices(db=db, skip=skip, limit=limit)

@router.patch("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
def edit_invoice(
    invoice_id: int,
    invoice_update: schemas.InvoiceUpdate,
    db: Session = Depends(get_db)
):
    return invoice_service.edit_invoice(invoice_id=invoice_id, invoice_update=invoice_update, db=db)

@router.delete("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    return invoice_service.delete_invoice(invoice_id=invoice_id, db=db)

@router.get("/invoices/{invoice_id}/status/")
def track_invoice_payment_status(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    return invoice_service.track_invoice_payment_status(db=db, invoice_id=invoice_id)