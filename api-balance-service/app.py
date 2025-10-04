from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from database import get_db, engine

app = FastAPI(title="Balance Service", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Balance Service running!"}

@app.get("/accounts/{account_id}/balance", response_model=schemas.BalanceOut)
def get_balance(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(models.Account).get(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    income_sum = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0))
        .filter(models.Transaction.account_id == account_id)
        .filter(models.Transaction.type == "INCOME")
        .scalar()
    )
    expense_sum = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0))
        .filter(models.Transaction.account_id == account_id)
        .filter(models.Transaction.type == "EXPENSE")
        .scalar()
    )
    return schemas.BalanceOut(
        account_id=account_id,
        income=income_sum,
        expense=expense_sum,
        balance=income_sum - expense_sum,
    )
