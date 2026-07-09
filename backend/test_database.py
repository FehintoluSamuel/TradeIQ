from app.database import SessionLocal, engine, Base
from app.models import Stock, DailyPrice

db = SessionLocal()

print("Running database tests...")
for stock in db.query(Stock).all():
    print(f"Stock: {stock.ticker} - {stock.full_name} - {stock.sector}")
    try:
        for price in stock.prices:
            print(f"  \nDailyPrice: {price.date} - Open: {price.open}, Close: {price.close}, Volume: {price.volume}, Stock ID: {price.stock_id}")
    except Exception as e:
        print(f"  Error fetching daily prices for {stock.ticker}: {e}")