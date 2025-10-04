from pydantic import BaseModel, Field
from decimal import Decimal

class BalanceOut(BaseModel):
    account_id: int
    income: Decimal = Field(..., max_digits=12, decimal_places=2)
    expense: Decimal = Field(..., max_digits=12, decimal_places=2)
    balance: Decimal = Field(..., max_digits=12, decimal_places=2)
