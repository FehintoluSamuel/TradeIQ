import requests
import requests, json
from app.database import settings
from app.database import SessionLocal
from app.database import SessionLocal
from app.models import DailyPrice, Stock

db = SessionLocal()
total = db.query(DailyPrice).count()
print(f'Total price rows in DB: {total}')

# Show count per stock
stocks = db.query(Stock).all()
for s in stocks:
    count = db.query(DailyPrice).filter(DailyPrice.stock_id == s.id).count()
    print(f'  {s.ticker}: {count} rows')
db.close()
