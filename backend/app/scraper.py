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

import requests
from sqlalchemy.orm import Session

from app.database import settings
from app.models import Stock, DailyPrice


# ── Logging ───────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────────────

TICKERS = ["DANGCEM", "GTCO", "MTNN", "ZENITH", "BUA"]

NGX_PULSE_URL = "https://www.ngxpulse.ng/api/ngxdata/stocks"


# ── Helpers ───────────────────────────────────────────────────────────────────

def clean(value) -> str:
    """Strip whitespace and commas from numeric strings."""
    return str(value).strip().replace(",", "")


# ── Core functions ────────────────────────────────────────────────────────────

def fetch_all_stocks() -> Optional[List[Dict]]:
    """
    Fetch all NGX stocks from NGX Pulse API.
    One call returns 150+ stocks — we filter afterwards.
    Returns None on any network or auth error.
    """
    try:
        response = requests.get(
            NGX_PULSE_URL,
            headers={
                "X-API-Key":  settings.NGX_PULSE_API_KEY,
                "User-Agent": "TradeIQ/1.0",
                "Accept":     "application/json",
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch NGX Pulse data: {e}")
        return None
    except ValueError as e:
        logger.error(f"Failed to parse NGX Pulse response: {e}")
        return None


def parse_stock_data(stock_data: Dict) -> Optional[Dict]:
    """
    Parse a single stock entry from NGX Pulse API response.
    Maps API fields to our DailyPrice schema.
    Returns None if data is invalid.
    """
    try:
        price = Decimal(clean(stock_data["current_price"]))

        if price <= 0:
            logger.warning(f"Invalid price for {stock_data.get('symbol')}: {price}")
            return None

        return {
            "date":   date.today(),
            "open":   price,   # API doesn't provide OHLC separately
            "high":   price,   # using current_price for all four
            "low":    price,   # documented limitation
            "close":  price,
            "volume": int(float(clean(stock_data.get("volume", 0)))),
        }
    except (KeyError, InvalidOperation, ValueError) as e:
        logger.warning(f"Failed to parse stock data: {e}")
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
        logger.info(f"{ticker}: price for {row['date']} already exists.")
        return False

    db.add(DailyPrice(
        stock_id = stock.id,
        source   = "ngx_pulse",
        **row,
    ))
    return True


def run_scraper(db: Session) -> None:
    """
    Main entry point — one API call, filter 5 tickers, store results.
    Called by scheduler.py daily at 17:00 WAT.
    """
    logger.info("Scraper started.")

    # One API call for all stocks
    all_stocks = fetch_all_stocks()
    print(type(all_stocks))
    print(all_stocks)

    if all_stocks:
        print(type(all_stocks[0]))
        print(all_stocks[0])
        
    if not all_stocks:
        logger.error("Scraper aborted — could not fetch data.")
        return

    # Build lookup dict by symbol for O(1) access
    stock_map = {s["symbol"]: s for s in all_stocks}

    inserted = 0
    for ticker in TICKERS:
        stock_data = stock_map.get(ticker)
        if not stock_data:
            logger.warning(f"{ticker} not found in NGX Pulse response.")
            continue

        row = parse_stock_data(stock_data)
        if not row:
            continue

        if store_price(ticker, row, db):
            inserted += 1
            logger.info(f"{ticker}: stored close={row['close']}")

    db.commit()
    logger.info(f"Scraper finished. {inserted}/{len(TICKERS)} tickers updated.")