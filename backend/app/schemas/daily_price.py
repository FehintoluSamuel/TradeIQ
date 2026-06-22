"""
schemas/daily_price.py
Pydantic schemas for the DailyPrice resource.
Uses Decimal for price fields — never float — to avoid precision loss.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class DailyPriceBase(BaseModel):
    stock_id: int
    date:     date
    open:     Decimal
    high:     Decimal
    low:      Decimal
    close:    Decimal
    volume:   int
    source:   str = "scraper"


class DailyPriceCreate(DailyPriceBase):
    """Schema for creating a new daily price — inherits all fields from DailyPriceBase."""
    pass


class DailyPriceResponse(DailyPriceBase):
    """Schema for API responses — adds DB-generated fields."""
    id:         int
    created_at: datetime

    model_config = {"from_attributes": True}