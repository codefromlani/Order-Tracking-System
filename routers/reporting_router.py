from fastapi import APIRouter, Depends
from services import reporting_service
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional
from datetime import datetime
import schemas


router = APIRouter(
    tags=["Report"]
)

@router.get("/reports/revenue/")
def get_total_revenue(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None, 
):
    return reporting_service.get_total_revenue(db=db, start_date=start_date, end_date=end_date)

@router.get("/reports/orders")
def get_no_of_orders(
        db: Session = Depends(get_db),
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
):
    return reporting_service.get_no_of_orders(db=db, start_date=start_date, end_date=end_date)

@router.get("/reports/popular_product")
def get_popular_product(db: Session = Depends(get_db)):
    return reporting_service.get_popular_product(db=db)

@router.get("/reports/expense/")
def get_expense_report(
        db: Session = Depends(get_db),
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
):
    return reporting_service.get_expense_report(db=db, start_date=start_date, end_date=end_date)

@router.get("/reports/client/")
def get_client_report(db: Session = Depends(get_db)):
    return reporting_service.get_client_report(db=db)

@router.get("/reports/client_history/")
def get_client_report_with_history(db: Session = Depends(get_db)):
    return reporting_service.get_client_report_with_history(db=db)

@router.get("/reports/vendor/")
def get_vendor_report(db: Session = Depends(get_db)):
    return reporting_service.get_vendor_report(db=db)