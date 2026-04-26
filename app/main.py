from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Fraud Detection Platform")

# Geçici depo (veritabanı olmadan)
transactions_db: List[dict] = []

class Transaction(BaseModel):
    user_id: str
    amount: float
    location: str
    timestamp: Optional[datetime] = None

@app.get("/")
def root():
    return {"message": "Fraud Detection API is running"}

@app.post("/transactions")
def create_transaction(transaction: Transaction):
    # Eğer timestamp gelmezse şimdiki zamanı ata
    if transaction.timestamp is None:
        transaction.timestamp = datetime.now()
    # Sözlüğe çevirip listeye ekle
    transaction_dict = transaction.dict()
    transactions_db.append(transaction_dict)
    return {"status": "ok", "transaction": transaction_dict}

@app.get("/transactions")
def list_transactions():
    return {"transactions": transactions_db}