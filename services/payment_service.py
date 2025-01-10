import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def verify_payment(payment_intent_id: str, db: Session) -> bool:
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if payment_intent.status == "succeeded":
            return True

        else:
            return False
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed"
        )
    
def update_order_status_to_approved(order_id: int, payment_intent_id: str, db: Session) -> dict:
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if db_order.status != schemas.OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is not in PENDING state"
        )
    
    verify_payment(payment_intent_id=payment_intent_id, db=db)
   
    db_order.status = schemas.OrderStatusEnum.APPROVED
    db.commit()

    return {"message": "Order approved successfully"}