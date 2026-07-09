import logging
logging.basicConfig(level=logging.INFO)

from app.database import SessionLocal
from app.scraper import run_scraper

db = SessionLocal()
try:
    run_scraper(db)
finally:
    db.close()