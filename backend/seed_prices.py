"""
seed_prices.py
Seeds the daily_prices table from CSV files in the seed/ folder.
Run once from inside backend/: python seed_prices.py
Safe to run multiple times — skips existing rows.
"""

import csv
import os
from datetime import datetime
from decimal import Decimal

from app.database import SessionLocal, Base, engine
from app.models import Stock, DailyPrice
import logging



logging.disable(logging.INFO)

TICKER_MAP = {
    "DANGCEM":   "DANGCEM",
    "GTCO":      "GTCO",
    "MTNN":      "MTNN",
    "ZENITH": "ZENITHBANK",
    "BUA":  "BUACEMENT",
}

def clean(value: str) -> str:
    """Strip whitespace and commas from numeric CSV strings."""
    return value.strip().replace(",", "")

# ── Setup ─────────────────────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)

SEED_DIR = os.path.join(os.path.dirname(__file__), "seed")

db = SessionLocal()

# ── Seed ──────────────────────────────────────────────────────────────────────

try:
    all_files = [f for f in os.listdir(SEED_DIR) if f.endswith(".csv")]

    if not all_files:
        print("No CSV files found in seed/ folder.")

    for filename in all_files:
        csv_ticker = filename.replace(".csv", "").upper()
        ticker = TICKER_MAP.get(csv_ticker)
        if not ticker:
            print(f"  ✗ No mapping for {csv_ticker} — skipping.")
            continue
        inserted = 0
        skipped  = 0

        # ── Find stock in DB ─────────────────────────────────────────────────
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            print(f"  ✗ {ticker} not found in DB — run seed.py first. Skipping.")
            continue

        print(f"\nProcessing {ticker} (stock_id={stock.id})...")

        # ── Read CSV ─────────────────────────────────────────────────────────
        csv_path = os.path.join(SEED_DIR, filename)
        with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # ── Parse values ─────────────────────────────────────────────
                try:
                    parsed_date = datetime.strptime(
                        row["Date"].strip(), "%m/%d/%Y"
                    ).date()
                    open_price  = Decimal(clean(row["Open"]))
                    high_price  = Decimal(clean(row["High"]))
                    low_price   = Decimal(clean(row["Low"]))
                    close_price = Decimal(clean(row["Close"]))
                    volume      = int(float(clean(row["Volume"])))
                except (ValueError, KeyError, Exception) as e:
                    print(f"  ✗ Failed row: {row}")
                    print(f"    Error: {e}")
                    continue

                # ── Duplicate check ───────────────────────────────────────────
                exists = (
                    db.query(DailyPrice)
                    .filter(
                        DailyPrice.stock_id == stock.id,
                        DailyPrice.date == parsed_date,
                    )
                    .first()
                )
                if exists:
                    skipped += 1
                    continue

                # ── Insert ────────────────────────────────────────────────────
                db.add(DailyPrice(
                    stock_id = stock.id,
                    date     = parsed_date,
                    open     = open_price,
                    high     = high_price,
                    low      = low_price,
                    close    = close_price,
                    volume   = volume,
                    source   = "csv_seed",
                ))
                inserted += 1

        # ── Commit after each ticker ──────────────────────────────────────────
        db.commit()
        print(f"  ✓ {ticker}: {inserted} inserted, {skipped} skipped.")

    print("\nDone. All CSVs processed.")

except Exception as e:
    db.rollback()
    print(f"Error — rolled back: {e}")

finally:
    db.close()