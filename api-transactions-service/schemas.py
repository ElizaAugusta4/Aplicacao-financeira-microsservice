from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TransactionBase(BaseModel):
    account_id: int
    type: str = Field(..., pattern="^(INCOME|EXPENSE)$")
    amount: Decimal = Field(..., max_digits=12, decimal_places=2)
    description: Optional[str] = Field(None, max_length=255)
    occurred_at: Optional[datetime] = None
    category: Optional[str] = Field(None, max_length=50)

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int