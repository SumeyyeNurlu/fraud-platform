from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    is_fraud = Column(Integer, default=0)   # 0 = normal, 1 = fraud