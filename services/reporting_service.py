from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
import models


def get_total_revenue(
        db: Session,
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
    ):

    result = db.query(func.sum(models.Order.total_amount))

    if start_date:
        result = result.filter(models.Order.created_at >= start_date)

    if end_date:
        result = result.filter(models.Order.created_at <= end_date)

    total_revenue = result.scalar()

    if total_revenue is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="No revenue found for the given time period."
            )

    return (f"Total Revenue: {total_revenue}")

def get_no_of_orders(
        db: Session,
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
):
    
    result = db.query(func.count(models.Order.id))

    if start_date:
        result = result.filter(models.Order.created_at >= start_date)

    if end_date:
        result = result.filter(models.Order.created_at <= end_date)

    total_orders = result.scalar()

    return (f"Total number of orders: {total_orders}")

def get_popular_product(db: Session):
    result = db.query(models.Product, func.sum(models.OrderProduct.quantity).label("total_quantity")).join(
        models.OrderProduct, models.OrderProduct.product_id == models.Product.id).group_by(
            models.Product.id).order_by(
                func.sum(models.OrderProduct.quantity).desc()).first()
    
    if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No popular product found.")
    
    product = result[0]
    total_quantity = result[1]

    return {
        "product_id": product.id,
        "product_name": product.name,
        "product_description": product.description,
        "total_quantity": total_quantity
    }

def get_expense_report(
        db: Session,
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
):
    
    result = db.query(models.Expense.category, func.sum(models.Expense.amount).label("total_expense"))

    if start_date:
        result = result.filter(models.Expense.date >= start_date)

    if end_date:
        result = result.filter(models.Expense.date <= end_date)

    result = result.group_by(models.Expense.category)
    result = result.order_by(func.sum(models.Expense.amount).desc())

    expense_report = result.all()

    return [
        {"category": category, "total_expense": total_expense}
            for category, total_expense in expense_report
    ]

def get_client_report(db: Session):
    
    result = db.query(models.Client.name, func.sum(models.Invoice.amount).label("total_spent")).join(
        models.Order, models.Order.client_id == models.Client.id).join(
            models.Invoice, models.Invoice.order_id == models.Order.id).group_by(
                models.Client.name).all()
    
    return [
            {"client_name": client_name, "total_spent": total_spent}
            for client_name, total_spent in result
        ]

def get_client_report_with_history(db: Session):

    result = db.query(models.Client.name,func.sum(models.Invoice.amount).label("total_spent"),
                      func.count(models.Order.id).label("total_orders"),
                      func.max(models.Order.created_at).label("latest_order_date")).join(
                          models.Order, models.Order.client_id == models.Client.id).join(
                              models.Invoice, models.Invoice.order_id == models.Order.id).group_by(
                                  models.Client.name).all()
    
    return [
            {
                "client_name": client_name,
                "total_spent": total_spent,
                "total_orders": total_orders,
                "latest_order_date": latest_order_date
            }
            for client_name, total_spent, total_orders, latest_order_date in result
        ]

def get_vendor_report(db: Session):
    result = db.query(models.Vendor.name, func.sum(models.Invoice.amount).label("total_sales")).join(
        models.Product, models.Product.vendor_id == models.Vendor.id).join(
            models.OrderProduct, models.OrderProduct.product_id == models.Product.id).join(
                models.Invoice, models.Invoice.order_id == models.OrderProduct.order_id).group_by(
                models.Vendor.name).all()
    
    return [
            {"vendor_name": vendor_name, "total_sales": total_sales}
            for vendor_name, total_sales in result
        ]