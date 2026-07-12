"""
migrate.py
Seeds all 24 tickers into Supabase and backfills price history.
Run once: python migrate.py
"""
import logging
logging.basicConfig(level=logging.INFO)

from app.database import SessionLocal, Base, engine
from app.models import Stock
from app.scraper import run_scraper, TICKERS
from app.scraper import fetch_stock_history, parse_ngx_row, store_price

# Only scrape tickers NOT already in DB with price data
from app.models import DailyPrice

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Seed missing stocks
stocks = [
    {"ticker": "DANGCEM",   "full_name": "Dangote Cement Plc",          "sector": "Industrial Goods"},
    {"ticker": "GTCO",      "full_name": "Guaranty Trust Holding Co.",   "sector": "Financial Services"},
    {"ticker": "MTNN",      "full_name": "MTN Nigeria Communications",   "sector": "Telecommunications"},
    {"ticker": "ZENITHBANK","full_name": "Zenith Bank Plc",              "sector": "Financial Services"},
    {"ticker": "BUACEMENT", "full_name": "BUA Cement Plc",               "sector": "Industrial Goods"},
    {"ticker": "UBA",       "full_name": "United Bank for Africa",       "sector": "Financial Services"},
    {"ticker": "STANBIC",   "full_name": "Stanbic IBTC Holdings",        "sector": "Financial Services"},
    {"ticker": "FIDELITYBK","full_name": "Fidelity Bank Plc",            "sector": "Financial Services"},
    {"ticker": "FCMB",      "full_name": "FCMB Group Plc",               "sector": "Financial Services"},
    {"ticker": "AIRTELAFRI","full_name": "Airtel Africa Plc",            "sector": "ICT"},
    {"ticker": "JBERGER",   "full_name": "Julius Berger Nigeria",        "sector": "Industrial Goods"},
    {"ticker": "NB",        "full_name": "Nigerian Breweries Plc",       "sector": "Consumer Goods"},
    {"ticker": "GUINNESS",  "full_name": "Guinness Nigeria Plc",         "sector": "Consumer Goods"},
    {"ticker": "NESTLE",    "full_name": "Nestle Nigeria Plc",           "sector": "Consumer Goods"},
    {"ticker": "CADBURY",   "full_name": "Cadbury Nigeria Plc",          "sector": "Consumer Goods"},
    {"ticker": "UNILEVER",  "full_name": "Unilever Nigeria Plc",         "sector": "Consumer Goods"},
    {"ticker": "PZ",        "full_name": "PZ Cussons Nigeria Plc",       "sector": "Consumer Goods"},
    {"ticker": "NASCON",    "full_name": "NASCON Allied Industries",     "sector": "Consumer Goods"},
    {"ticker": "OKOMUOIL",  "full_name": "Okomu Oil Palm Plc",          "sector": "Agriculture"},
    {"ticker": "PRESCO",    "full_name": "Presco Plc",                   "sector": "Agriculture"},
    {"ticker": "SEPLAT",    "full_name": "Seplat Energy Plc",            "sector": "Energy"},
    {"ticker": "GEREGU",    "full_name": "Geregu Power Plc",             "sector": "Energy"},
    {"ticker": "TRANSCORP", "full_name": "Transnational Corporation",    "sector": "Conglomerates"},
    {"ticker": "BUAFOODS",  "full_name": "BUA Foods Plc",                "sector": "Consumer Goods"},
]

try:
    for s in stocks:
        exists = db.query(Stock).filter(Stock.ticker == s["ticker"]).first()
        if not exists:
            db.add(Stock(**s))
            print(f"Added {s['ticker']}")
    db.commit()
    print("Stocks seeded. Running scraper...")
    print("Backfilling missing tickers only...")
    for stock in db.query(Stock).all():
        has_prices = db.query(DailyPrice).filter(
            DailyPrice.stock_id == stock.id
        ).first()
        if has_prices:
            print(f"Skipping {stock.ticker} — already has data")
            continue
        print(f"Backfilling {stock.ticker}...")
        rows = fetch_stock_history(stock.ticker, days=365)
        if not rows:
            continue
        count = 0
        for raw in rows:
            row = parse_ngx_row(raw)
            if row and store_price(stock.ticker, row, db):
                count += 1
        db.commit()
        print(f"  {stock.ticker}: {count} rows inserted")
    print("Done.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()