from fastapi import APIRouter, Depends, status
from services import expense_service
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from datetime import datetime
import schemas


router = APIRouter(
    tags=["Expense"]
)

@router.post("/expenses/", status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db)
):
    return expense_service.create_expense(expense=expense, db=db)

@router.get("/expenses/categories/")
def get_expense_categories():
    return expense_service.get_expense_categories()

@router.get("/expenses/")
def get_expenses(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 10, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None, 
    category: Optional[schemas.ExpensecategoryEnum] = None
):
    return expense_service.get_expenses(
    db=db,
    skip=skip,
    limit=limit,
    start_date=start_date,
    end_date=end_date,
    category=category
    )

@router.get("/expenses/summary/")
def get_expense_summary(
    db: Session = Depends(get_db), 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
):
    return expense_service.get_expense_summary(db=db, start_date=start_date, end_date=end_date)

@router.patch("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: int, 
    expense_update: schemas.ExpenseUpdate,
    db: Session = Depends(get_db), 
):
    return expense_service.update_expense(expense_id=expense_id, expense_update=expense_update, db=db)

@router.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    return expense_service.delete_expense(expense_id=expense_id, db=db)