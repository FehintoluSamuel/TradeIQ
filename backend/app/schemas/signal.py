"""
schemas/signal.py
Pydantic schema for computed signal responses.
Signals are never stored in the DB — computed fresh from DailyPrice data.
No Base or Create schema needed — this is a read-only computed response.
"""

from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class SignalResponse(BaseModel):
    """
    Computed technical analysis response for a single stock.
    Returned by GET /signals/{ticker} and GET /signals/all
    """
    ticker:        str
    date:          date
    close:         Decimal
    change_pct:    float
    ma7:           Decimal
    ma30:          Decimal
    rsi:           float
    signal:        str      # "bullish" | "neutral" | "bearish" | "overbought" | "oversold"
    signal_reason: str      # Plain English explanation for Nigerian retail investors

    model_config = {"from_attributes": True}