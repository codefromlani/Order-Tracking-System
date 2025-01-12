from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import schemas
import models


def create_expense(expense: schemas.ExpenseCreate, db: Session) -> models.Expense:
    
    new_expense = models.Expense(
        category=expense.category,
        amount=expense.amount,
        description=expense.description
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return schemas.ExpenseResponse(
        id=new_expense.id,
        category=new_expense.category,
        amount=new_expense.amount,
        description=expense.description,
        date=datetime.utcnow()
    )

def get_expense_categories():
    return [category.value for category in schemas.ExpensecategoryEnum]

def get_expenses(
        db: Session, 
        skip: int = 0, 
        limit: int = 10, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
        category: Optional[schemas.ExpensecategoryEnum] = None
    ):
    
    expense = db.query(models.Expense)
    if start_date and end_date:
        expense = expense.filter(models.Expense.date >= start_date, models.Expense.date <=end_date)

    if category:
        expense = expense.filter(models.Expense.category == category)

    return expense.offset(skip).limit(limit).all()

def get_expense_summary(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    expenses = get_expenses(db=db, start_date=start_date, end_date=end_date, skip=0, limit=10)

    summary = {
        "total_amount": sum(expense.amount for expense in expenses),
        "categories": {category.value: 0 for category in schemas.ExpensecategoryEnum}
    }

    for expense in expenses:
        summary["categories"][expense.category.value] += expense.amount

    return summary

def update_expense(db: Session, expense_id: int, expense_update: schemas.ExpenseUpdate) -> Optional[models.Expense]:
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    if expense_update.category is not None:
        db_expense.category=expense_update.category
        
    if expense_update.amount is not None:
        db_expense.amount=expense_update.amount

    if expense_update.description is not None:
        db_expense.description=expense_update.description

    if expense_update.date is not None:
        db_expense.date=expense_update.date

    db.commit()

    return db_expense

def delete_expense(db: Session, expense_id: int) -> None:
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    db.delete(db_expense)
    db.commit()

    return {"message": "Expense deleted successfully"}