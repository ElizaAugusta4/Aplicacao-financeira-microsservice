from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    transactions = relationship("AccountTransaction", back_populates="account", cascade="all, delete-orphan")

class AccountTransaction(Base):
    __tablename__ = "account_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)  # Adicione o ForeignKey aqui
    type = Column(String(20), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(255), nullable=True)
    occurred_at = Column(DateTime)
    category = Column(String(50), nullable=True)
    account = relationship("Account", back_populates="transactions")  # Adicione o relacionamento reverso
