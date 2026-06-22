"""
schemas/stock.py
Pydantic schemas for the Stock resource.
Controls what data the API accepts and returns — separate from the DB model.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StockBase(BaseModel):
    ticker:    str
    full_name: str
    sector:    Optional[str] = None


class StockCreate(StockBase):
    """Schema for creating a new stock — inherits all fields from StockBase."""
    pass


class StockResponse(StockBase):
    """Schema for API responses — adds DB-generated fields."""
    id:         int
    created_at: datetime

    model_config = {"from_attributes": True}