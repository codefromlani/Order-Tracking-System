from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from services import payment_service
import schemas
import models
import stripe


def create_order(order: schemas.OrderCreate, db: Session) -> models.Order:
    db_client = db.query(models.Client).filter(models.Client.id == order.client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    total_amount = 0.0

    order_products = []

    for item in order.products:
        db_product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        if db_product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {db_product.name}. Available: {db_product.stock}, Required: {item.quantity}"
            )

        
        price = db_product.price * item.quantity
        total_amount += price

        order_product = models.OrderProduct(
            product_id=item.product_id,
            quantity=item.quantity,
            price=price
        )
        order_products.append(order_product)

        db_product.stock -= item.quantity

    new_order = models.Order(
        client_id=order.client_id,
        total_amount=total_amount,
        status=models.OrderStatusEnum.PENDING
    )

    db.add(new_order)
    db.flush() 

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Convert to cents
            currency="usd",  # Change to the desired currency
            metadata={"order_id": new_order.id}  # Store order_id as metadata
        )
        new_order.payment_intent_id = payment_intent.id  # Save payment_intent_id in the order record
        db.commit()
    except stripe.error.StripeError as e:
        db.rollback()  # If there's an error with Stripe, rollback the transaction
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating PaymentIntent: {str(e)}"
        )

    for order_product in order_products:
        order_product.order_id = new_order.id 

    db.add_all(order_products)
    db.commit()

    return schemas.OrderResponse(
        id=new_order.id,
        client_id=order.client_id,
        total_amount=total_amount,
        status=new_order.status,
        payment_intent=new_order.payment_intent_id,
        products=order.products
    )

def get_orders(db: Session, skip: int = 0, limit: int = 10) -> List[schemas.OrderResponse]:
    db_orders = db.query(models.Order).options(
        joinedload(models.Order.order_product).joinedload(models.OrderProduct.product)
        ).offset(skip).limit(limit).all()
    if not db_orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orders not found"
        )
    
    order_responses= []
    for order in db_orders:
        order_response = schemas.OrderResponse(
            id=order.id,
            client_id=order.client_id,
            total_amount=order.total_amount,
            status=order.status,
            payment_intent=order.payment_intent_id,
            products=[
                schemas.OrderProductCreate(product_id=op.product_id, quantity=op.quantity)
                for op in order.order_product
            ]
        )
    
        order_responses.append(order_response)

    return order_responses

def edit_order(db: Session, order_id: int, order_update: schemas.OrderUpdate) -> models.Order:
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if db_order.status != models.OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only modify pending orders"
        )
    
    if db_order.payment_intent_id:
        pass

    db_product = db.query(models.Product).filter(models.Product.id == order_update.product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    total_amount = db_order.total_amount
    
    if order_update.action == schemas.ActionEnum.ADD:
        if db_product.stock < order_update.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock for this product"
            )

        order_product = db.query(models.OrderProduct).filter(
            models.OrderProduct.order_id == order_id,
            models.OrderProduct.product_id == order_update.product_id
        ).first()

        if order_product:
            order_product.quantity += order_update.quantity
        
        else:
            new_order_product = models.OrderProduct(
                order_id=order_id,
                product_id=order_update.product_id,
                quantity=order_update.quantity,
                price=db_product.price
            )

            db.add(new_order_product)
        db_product.stock -= order_update.quantity
        total_amount += (db_product.price * order_update.quantity)

    
    elif order_update.action == schemas.ActionEnum.REMOVE:
        order_product = db.query(models.OrderProduct).filter(
            models.OrderProduct.order_id == order_id,
            models.OrderProduct.product_id == order_update.product_id
        ).first()

        if not order_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in order"
            )
        
        db_product.stock += order_update.quantity
        total_amount -= (db_product.price * order_product.quantity)
        db.delete(order_product)

    elif order_update.action == schemas.ActionEnum.UPDATE:
        order_product = db.query(models.OrderProduct).filter(
            models.OrderProduct.order_id == order_id,
            models.OrderProduct.product_id == order_update.product_id
        ).first()

        if not order_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in order"
            )
        
        quantity_difference = order_update.quantity - order_product.quantity

        if db_product.stock < quantity_difference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for the updated quantity"
            )

        db_product.stock -= quantity_difference
        total_amount -= db_product.price * order_product.quantity
        total_amount += db_product.price * order_update.quantity
        order_product.quantity = order_update.quantity

    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action"
        )
    
    db_order.total_amount = total_amount

    db.commit()

    order_response = schemas.OrderResponse(
        id=db_order.id,
        client_id=db_order.client_id,
        total_amount=db_order.total_amount,
        status=db_order.status,
        payment_intent=db_order.payment_intent_id,
        products=[
            schemas.OrderProductCreate(
                product_id=op.product_id, quantity=op.quantity
            ) for op in db_order.order_product
        ]
    )

    return order_response

# For testing purposes
def manual_update_order_status(order_id: int, new_status: schemas.OrderStatusEnum, db: Session) -> dict:
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if new_status not in [
        schemas.OrderStatusEnum.PENDING,
        schemas.OrderStatusEnum.APPROVED,
        schemas.OrderStatusEnum.SHIPPED,
        schemas.OrderStatusEnum.DELIVERED,
        schemas.OrderStatusEnum.CANCELLED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    db_order.status = new_status

    order_history = models.OrderHistory(
        order_id=db_order.id,
        status=db_order.status,
        changed_at=datetime.utcnow()
    )
    db.add(order_history)

    db.commit()

    return {"message": f"Order status updated to {new_status}"}

def track_order_status(order_id: int, db: Session) -> dict:
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return {"order_id": order.id, "status": order.status}

def orders_history(db: Session, skip: int = 0, limit: int = 10, order_id: Optional[int] = None) -> List[schemas.OrderHistory]:
    orders = db.query(models.Order).all()

    for order in orders:
        existing_history = db.query(models.OrderHistory).filter(models.OrderHistory.order_id == order.id).first()

        if not existing_history:
            new_history = models.OrderHistory(
                order_id=order.id,
                status=order.status,
                changed_at=order.created_at
            )

            db.add(new_history)

    db.commit()

    query = db.query(models.OrderHistory).order_by(models.OrderHistory.changed_at.desc())

    if order_id:
        query = query.filter(models.OrderHistory.order_id == order_id)

        order_exists = db.query(models.Order).filter(models.Order.id == order_id).first()

        if not order_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )
        
    history_entries = query.offset(skip).limit(limit).all()

    return [
        schemas.OrderHistory(
            order_id=entry.order_id,
            status=entry.status,
            changed_at=entry.changed_at
        )for entry in history_entries
    ]