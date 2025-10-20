from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import models, schemas
from database import get_db, engine
import os
import requests

_raw_accounts_url = os.getenv("ACCOUNTS_SERVICE_URL", "http://accounts-service.default.svc.cluster.local:8000")
ACCOUNTS_SERVICE_URL = _raw_accounts_url.rstrip('/')

app = FastAPI(title="Transactions Service", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Transactions Service running!"}

def _get_account_from_service(account_id: int):
    url = f"{ACCOUNTS_SERVICE_URL}/accounts/{account_id}"
    print("[transactions] requesting account:", url)
    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        msg = f"Erro ao contactar Accounts Service: {type(exc).__name__}: {str(exc)}"
        print("[transactions] request exception:", msg)
        raise HTTPException(status_code=502, detail=msg)

    print(f"[transactions] accounts service response: status={resp.status_code} body={resp.text}")

    if resp.status_code == 404:
        raise HTTPException(status_code=400, detail="Conta não encontrada")
    if not resp.ok:
        detail = f"Accounts Service retornou erro (status={resp.status_code}): {resp.text}"
        raise HTTPException(status_code=502, detail=detail)
    try:
        return resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Accounts Service retornou resposta inválida (não-JSON)")

@app.post("/transactions", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    _get_account_from_service(transaction.account_id)

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
