from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.database import engine, Base, get_db
from app.models.transaction import Transaction as TransactionModel
from app.services.fraud_detector import detect_fraud
from pydantic import BaseModel
from typing import List, Optional

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fraud Detection Platform")

class TransactionCreate(BaseModel):
    user_id: str
    amount: float
    location: str
    timestamp: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: str
    amount: float
    location: str
    timestamp: datetime
    is_fraud: int

    class Config:
        from_attributes = True

@app.get("/")
def root():
    return {"message": "Fraud Detection API is running"}

@app.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    is_fraud = detect_fraud(transaction.user_id, transaction.amount)
    fraud_flag = 1 if is_fraud else 0
    
    db_transaction = TransactionModel(
        user_id=transaction.user_id,
        amount=transaction.amount,
        location=transaction.location,
        timestamp=transaction.timestamp or datetime.now(),
        is_fraud=fraud_flag
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions", response_model=List[TransactionResponse])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(TransactionModel).all()

@app.get("/frauds", response_model=List[TransactionResponse])
def list_frauds(db: Session = Depends(get_db)):
    return db.query(TransactionModel).filter(TransactionModel.is_fraud == 1).all()
