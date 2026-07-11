"""
routers/prices.py
Endpoints for retrieving historical OHLCV price data per stock.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Stock, DailyPrice
from app.schemas import DailyPriceResponse


router = APIRouter()


# ── Helper ────────────────────────────────────────────────────────────────────

def get_stock_or_404(ticker: str, db: Session) -> Stock:
    """Fetch a stock by ticker or raise 404. Reused across endpoints."""
    #To Normalize ticker
    ticker = ticker.replace("'", "").replace('"', "").strip()
    stock = (
        db.query(Stock)
        .filter(Stock.ticker == ticker.upper())
        .first()
    )
    if not stock:
        raise HTTPException(
            status_code=404,
            detail=f"Stock '{ticker}' not found. "
                   f"Valid tickers: DANGCEM, GTCO, MTNN, ZENITH, BUA."
        )
    return stock


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/prices/{ticker}", response_model=List[DailyPriceResponse])
def get_prices(
    ticker: str,
    limit: int = 30,
    db: Session = Depends(get_db),
):
    """
    Return historical OHLCV prices for a stock.
    Optional query param: ?limit=N (default 30, max sensible value: 365)
    """
    stock = get_stock_or_404(ticker, db)

    prices = (
        db.query(DailyPrice)
        .filter(DailyPrice.stock_id == stock.id)
        .order_by(DailyPrice.date.desc())
        .limit(limit)
        .all()
    )
    # Reverse so chart goes oldest → newest
    # prices.reverse()
    return prices


@router.get("/prices/{ticker}/latest", response_model=DailyPriceResponse)
def get_latest_price(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return the most recent trading day price for a stock."""
    stock = get_stock_or_404(ticker, db)

    latest = (
        db.query(DailyPrice)
        .filter(DailyPrice.stock_id == stock.id)
        .order_by(DailyPrice.date.desc())
        .first()
    )
    if not latest:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for '{ticker}'. "
                   f"Database may not be seeded yet."
        )
    return latest