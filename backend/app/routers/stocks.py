"""
routers/stocks.py
Endpoints for managing and retrieving NGX stock metadata.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Stock
from app.schemas import StockResponse


router = APIRouter()


@router.get("/stocks", response_model=List[StockResponse])
def get_stocks(db: Session = Depends(get_db)):
    """Return all tracked NGX stocks."""
    return db.query(Stock).all()


@router.get("/stocks/{ticker}", response_model=StockResponse)
def get_one_stock(ticker: str, db: Session = Depends(get_db)):
    """Return a single stock by ticker symbol. Returns 404 if not found."""
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()

    if not stock:
        raise HTTPException(
            status_code=404,
            detail=f"Stock '{ticker}' not found. "
                   f"Valid tickers are: DANGCEM, GTCO, MTNN, ZENITH, BUA."
        )
    return stock