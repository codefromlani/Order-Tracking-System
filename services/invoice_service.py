from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import schemas
import models

def generate_invoice(order_id: int, db: Session) -> models.Invoice:
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != models.OrderStatusEnum.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only generate invoice for completed order"
        )
    
    else:
        new_invoice = models.Invoice(
            id=models.Invoice.id,
            order_id=order_id,
            amount=order.total_amount,
            status=models.InvoiceStatusEnum.PAID,
            due_date=order.created_at + timedelta(days=30)
        )

        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

        return schemas.InvoiceResponse(
            id=new_invoice.id,
            order_id=new_invoice.order_id,
            amount=new_invoice.amount,
            status=new_invoice.status,
            due_date=new_invoice.due_date
        )
    
def get_invoices(db: Session, skip: int = 0, limit: int = 10) ->List[models.Invoice]:
    db_invoices = db.query(models.Invoice).offset(skip).limit(limit).all()
    if not db_invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoices not found"
        )
    
    return db_invoices

def edit_invoice(invoice_id: int, invoice_update: schemas.InvoiceUpdate, db: Session) -> Optional[models.Invoice]:
    db_invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice_update.amount is not None:
        db_invoice.amount=invoice_update.amount

    if invoice_update.status is not None:
        db_invoice.status=invoice_update.status

    if invoice_update.due_date is not None:
        db_invoice.due_date=invoice_update.due_date

    db.commit()

    return db_invoice

# Soft delete by changing the status to cancelled
def delete_invoice(invoice_id: int, db: Session) -> None:
    db_invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    db_invoice.status = models.InvoiceStatusEnum.CANCELLED
    db.commit()
    db.refresh(db_invoice)

    return schemas.InvoiceResponse(
        id=db_invoice.id,
        order_id=db_invoice.order_id,
        amount=db_invoice.amount,
        status=db_invoice.status,
        due_date=db_invoice.due_date
    )

def track_invoice_payment_status(invoice_id: int, db: Session) -> dict:
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return {"order_id": invoice.id, "status": invoice.status}