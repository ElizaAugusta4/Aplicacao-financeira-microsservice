from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import models, schemas
from database import get_db, engine

app = FastAPI(title="Transactions Service", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Transactions Service running!"}

@app.post("/transactions", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # Criar transação direto no próprio banco
    db_transaction = models.AccountTransaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions", response_model=List[schemas.TransactionOut])
def list_transactions(
    account_id: Optional[int] = Query(None, description="Filtrar por ID da conta"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    db: Session = Depends(get_db),
):
    q = db.query(models.AccountTransaction)
    if account_id is not None:
        q = q.filter(models.AccountTransaction.account_id == account_id)
    if category:
        q = q.filter(models.AccountTransaction.category == category)
    return q.order_by(models.AccountTransaction.occurred_at.desc(), models.AccountTransaction.id.desc()).all()

@app.get("/transactions/{tx_id}", response_model=schemas.TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(models.AccountTransaction).get(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return tx

@app.put("/transactions/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    tx = db.query(models.AccountTransaction).get(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    for field, value in transaction.dict().items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx

@app.delete("/transactions/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(models.AccountTransaction).get(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(tx)
    db.commit()
    return
