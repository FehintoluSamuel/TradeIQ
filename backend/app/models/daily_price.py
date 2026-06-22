"""
models/daily_price.py
Defines the DailyPrice model representing the 'daily_prices' table.
One row per stock per trading day — stores OHLCV data.
"""

from sqlalchemy import (
    Column, Integer, String, Numeric,
    BigInteger, Date, DateTime, ForeignKey,
    UniqueConstraint, func,
)
from sqlalchemy.orm import relationship
from app.database import Base


class DailyPrice(Base):
    tablename = "daily_prices"
    table_args = (
        UniqueConstraint("stock_id", "date", name="uix_stock_date"),
    )

    id         = Column(Integer,          primary_key=True, index=True)
    stock_id   = Column(Integer,          ForeignKey("stocks.id"), nullable=False, index=True)
    date       = Column(Date,             nullable=False, index=True)
    open       = Column(Numeric(12, 2),   nullable=False)
    high       = Column(Numeric(12, 2),   nullable=False)
    low        = Column(Numeric(12, 2),   nullable=False)
    close      = Column(Numeric(12, 2),   nullable=False)
    volume     = Column(BigInteger,       nullable=False)
    source     = Column(String(30),       nullable=False, default="scraper")
    created_at = Column(DateTime,         server_default=func.now(), nullable=False)

    # Relationship — navigates to the parent Stock object
    stock = relationship("Stock", back_populates="prices")

    def __repr__(self):
        return (
            f"<DailyPrice("
            f"stock_id={self.stock_id}, "
            f"date={self.date}, "
            f"close={self.close}"
            f")>"
        )