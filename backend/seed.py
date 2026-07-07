"""
seed.py
Populates the database with the 5 tracked NGX stocks.
Run once from inside backend/: python seed.py
"""

from app.database import SessionLocal, engine, Base
from app.models import Stock, DailyPrice

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

stocks = [
    {"ticker": "DANGCEM", "full_name": "Dangote Cement Plc",          "sector": "Industrial Goods"},
    {"ticker": "GTCO",    "full_name": "Guaranty Trust Holding Co.",   "sector": "Financial Services"},
    {"ticker": "MTNN",    "full_name": "MTN Nigeria Communications",   "sector": "Telecommunications"},
    {"ticker": "ZENITH",  "full_name": "Zenith Bank Plc",              "sector": "Financial Services"},
    {"ticker": "BUA",     "full_name": "BUA Foods Plc",                "sector": "Consumer Goods"},
]

try:
    for s in stocks:
        exists = db.query(Stock).filter(Stock.ticker == s["ticker"]).first()
        if not exists:
            db.add(Stock(**s))
            print(f"Added {s['ticker']}")
        else:
            print(f"Skipped {s['ticker']} — already exists")
    db.commit()
    print("\nDone. Stocks seeded successfully.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()