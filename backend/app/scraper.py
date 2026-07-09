"""
scraper.py
Fetches daily price data from NGX Pulse API for tracked NGX stocks.
One API call returns all 150+ stocks — we filter for our 5.
Called by scheduler.py daily at 17:00 WAT after market close.
"""

import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Dict

from datetime import datetime, date
import requests
from sqlalchemy.orm import Session

from app.database import settings
from app.models import Stock, DailyPrice


# ── Logging ───────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────────────

TICKERS = ["DANGCEM", "GTCO", "MTNN", "ZENITH", "BUA"]
API_SYMBOL_MAP = {
    "DANGCEM": "DANGCEM",
    "GTCO": "GTCO",
    "MTNN": "MTNN",
    "ZENITH": "ZENITHBANK",
    "BUA": "BUACEMENT",
}


# Single stock historical endpoint
NGX_PRICE_URL = "https://www.ngxpulse.ng/api/ngxdata/prices"


def fetch_stock_history(
    ticker: str,
    days: int = 365
) -> Optional[List[Dict]]:
    """Fetch historical prices for one ticker."""
    try:
        response = requests.get(
            f"{NGX_PRICE_URL}/{ticker}",
            headers={
                "X-API-Key":  settings.NGX_PULSE_API_KEY,
                "Accept":     "application/json",
            },
            params={"days": days},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("prices", [])
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {ticker}: {e}")
        return None


def parse_ngx_row(row: Dict) -> Optional[Dict]:
    """Parse one row from NGX Pulse historical response."""
    try:
        close = Decimal(str(row["close_price"] or row["open_price"]))
        if close <= 0:
            return None
        return {
            "date":   datetime.strptime(
                          row["trade_date"], "%Y-%m-%d"
                      ).date(),
            "open":   Decimal(str(row["open_price"]  or close)),
            "high":   Decimal(str(row["high_price"]  or close)),
            "low":    Decimal(str(row["low_price"]   or close)),
            "close":  close,
            "volume": int(row.get("volume") or 0),
        }
    except (KeyError, InvalidOperation, ValueError) as e:
        logger.warning(f"Skipping row: {e}")
        return None
    
def store_price(ticker: str, row: Dict, db: Session) -> bool:
    """
    Insert one DailyPrice row for a ticker.
    Skips if row for today already exists.
    Returns True if inserted, False if skipped.
    """
    stock = (
        db.query(Stock)
        .filter(Stock.ticker == ticker)
        .first()
    )
    if not stock:
        logger.warning(f"Stock '{ticker}' not found in DB.")
        return False

    exists = (
        db.query(DailyPrice)
        .filter(
            DailyPrice.stock_id == stock.id,
            DailyPrice.date     == row["date"],
        )
        .first()
    )
    if exists:
        return False

    db.add(DailyPrice(
        stock_id = stock.id,
        source   = "ngx_pulse",
        **row,
    ))
    return True
    



def run_scraper(db: Session) -> None:
    """Fetch and store latest prices for all tracked tickers."""
    logger.info("Scraper started.")
    inserted_total = 0

    for ticker in TICKERS:
        rows = fetch_stock_history(ticker, days=365)
        if not rows:
            continue

        count = 0
        for raw in rows:
            row = parse_ngx_row(raw)
            if row and store_price(ticker, row, db):
                count += 1

        db.commit()
        inserted_total += count
        logger.info(f"{ticker}: {count} rows inserted.")

    logger.info(f"Scraper finished. {inserted_total} total rows.")