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
    {"ticker": "ZENITHBANK", "full_name": "Zenith Bank Plc",           "sector": "Financial Services"},
    {"ticker": "UBA",        "full_name": "United Bank for Africa",     "sector": "Financial Services"},
    {"ticker": "STANBIC",    "full_name": "Stanbic IBTC Holdings",      "sector": "Financial Services"},
    {"ticker": "FIDELITYBK", "full_name": "Fidelity Bank Plc",          "sector": "Financial Services"},
    {"ticker": "FCMB",       "full_name": "FCMB Group Plc",             "sector": "Financial Services"},
    {"ticker": "AIRTELAFRI", "full_name": "Airtel Africa Plc",          "sector": "ICT"},
    {"ticker": "JBERGER",    "full_name": "Julius Berger Nigeria",       "sector": "Industrial Goods"},
    {"ticker": "NB",         "full_name": "Nigerian Breweries Plc",     "sector": "Consumer Goods"},
    {"ticker": "GUINNESS",   "full_name": "Guinness Nigeria Plc",       "sector": "Consumer Goods"},
    {"ticker": "NESTLE",     "full_name": "Nestle Nigeria Plc",         "sector": "Consumer Goods"},
    {"ticker": "CADBURY",    "full_name": "Cadbury Nigeria Plc",        "sector": "Consumer Goods"},
    {"ticker": "UNILEVER",   "full_name": "Unilever Nigeria Plc",       "sector": "Consumer Goods"},
    {"ticker": "PZ",         "full_name": "PZ Cussons Nigeria Plc",     "sector": "Consumer Goods"},
    {"ticker": "NASCON",     "full_name": "NASCON Allied Industries",   "sector": "Consumer Goods"},
    {"ticker": "OKOMUOIL",   "full_name": "Okomu Oil Palm Plc",        "sector": "Agriculture"},
    {"ticker": "PRESCO",     "full_name": "Presco Plc",                 "sector": "Agriculture"},
    {"ticker": "SEPLAT",     "full_name": "Seplat Energy Plc",          "sector": "Energy"},
    {"ticker": "GEREGU",     "full_name": "Geregu Power Plc",           "sector": "Energy"},
    {"ticker": "TRANSCORP",  "full_name": "Transnational Corporation",  "sector": "Conglomerates"},
    {"ticker": "BUACEMENT",  "full_name": "BUA Cement Plc",             "sector": "Industrial Goods"},
    {"ticker": "BUAFOODS",   "full_name": "BUA Foods Plc",              "sector": "Consumer Goods"},
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