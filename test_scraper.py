import logging
logging.basicConfig(level=logging.INFO)

from app.database import SessionLocal
from scraper.scrape import run_scraper

db = SessionLocal()
try:
    run_scraper(db)
finally:
    db.close()