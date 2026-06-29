"""
routers/signals.py
Computes and serves technical analysis signals for NGX stocks.
Combines price data from DB with indicators.py functions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Stock, DailyPrice
from app.schemas import SignalResponse
from app.indicators import compute_ma, compute_rsi, determine_signal
from app.routers.prices import get_stock_or_404


router = APIRouter()

TICKERS = ["DANGCEM", "GTCO", "MTNN", "ZENITH", "BUA"]


# ── Private helper ────────────────────────────────────────────────────────────

def _compute_signal(ticker: str, db: Session) -> SignalResponse:
    """
    Core signal computation logic.
    Reused by both get_all_signals and get_ticker_signal.
    """
    stock = get_stock_or_404(ticker, db)

    prices = (
        db.query(DailyPrice)
        .filter(DailyPrice.stock_id == stock.id)
        .order_by(DailyPrice.date.asc())
        .limit(30)
        .all()
    )

    if not prices:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for '{ticker}'. Seed the database first."
        )

    closes = [p.close for p in prices]

    # ── Compute indicators ───────────────────────────────────────────────────
    ma7  = compute_ma(closes, 7)
    ma30 = compute_ma(closes, 30)
    rsi  = compute_rsi(closes)

    # ── Determine signal ─────────────────────────────────────────────────────
    signal, reason = determine_signal(closes[-1], ma7, ma30, rsi)

    # ── Percentage change ────────────────────────────────────────────────────
    change_pct = (
        float((closes[-1] - closes[-2]) / closes[-2] * 100)
        if len(closes) >= 2
        else 0.0
    )

    return SignalResponse(
        ticker=stock.ticker,
        date=prices[-1].date,
        close=closes[-1],
        change_pct=round(change_pct, 2),
        ma7=ma7,
        ma30=ma30,
        rsi=round(rsi, 2) if rsi is not None else None,
        signal=signal,
        signal_reason=reason,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/signals/all", response_model=List[SignalResponse])
def get_all_signals(db: Session = Depends(get_db)):
    """Return signals for all 5 tracked NGX stocks."""
    results = []
    for ticker in TICKERS:
        try:
            result = _compute_signal(ticker, db)
            results.append(result)
        except HTTPException:
            continue  # skip tickers with no data — don't crash the whole response
    return results


@router.get("/signals/{ticker}", response_model=SignalResponse)
def get_ticker_signal(ticker: str, db: Session = Depends(get_db)):
    """Return the full technical signal for a single stock."""
    return _compute_signal(ticker, db)