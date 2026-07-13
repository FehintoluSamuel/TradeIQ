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
import httpx
from app.database import settings


router = APIRouter()

TICKERS = [
    # Financial Services
    "GTCO", "ZENITHBANK", "UBA", "STANBIC", "FIDELITYBK", "FCMB",
    # Telecoms
    "MTNN", "AIRTELAFRI",
    # Industrial Goods
    "DANGCEM", "JBERGER",
    # Consumer Goods
    "NB", "GUINNESS", "NESTLE", "CADBURY", "UNILEVER", "PZ", "NASCON",
    # Agriculture
    "OKOMUOIL", "PRESCO",
    # Energy
    "SEPLAT", "GEREGU",
    # Conglomerates
    "TRANSCORP",
    # Cement / Food
    "BUACEMENT", "BUAFOODS",
]



MARKET_INTEL_URL = "http://localhost:8001"  # your microservice

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
        .order_by(DailyPrice.date.desc())
        .limit(30)
        .all()
    )
    prices.reverse()  # oldest → newest for indicator calculations

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




        


@router.get("/signals/{ticker}/explain")
async def explain_ticker_signal(ticker: str, db: Session = Depends(get_db)):
    """
    Computes signal then forwards to market-intel microservice for AI explanation.
    """
    # Compute signal using existing logic
    signal = _compute_signal(ticker, db)

    # Forward to microservice
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                f"{settings.MARKET_INTEL_URL}/market/explain/signal",
                json={
                    "ticker":     signal.ticker,
                    "close":      str(signal.close),
                    "ma7":        str(signal.ma7)  if signal.ma7  else None,
                    "ma30":       str(signal.ma30) if signal.ma30 else None,
                    "rsi":        signal.rsi,
                    "signal":     signal.signal,
                    "change_pct": signal.change_pct,
                },
                timeout=30,
            )
            res.raise_for_status()
            return res.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Market intel service unavailable: {e}"
            )