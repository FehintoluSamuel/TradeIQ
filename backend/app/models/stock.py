"""
models/stock.py
Defines the Stock model representing the 'stocks' table.
Stores metadata for each tracked NGX ticker.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Stock(Base):
    tablename = "stocks"

    id         = Column(Integer,     primary_key=True, index=True)
    ticker     = Column(String(10),  unique=True, nullable=False, index=True)
    full_name  = Column(String(100), nullable=False)
    sector     = Column(String(50),  nullable=True)
    created_at = Column(DateTime,    server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Stock(ticker='{self.ticker}', full_name='{self.full_name}')>"