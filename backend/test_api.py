import requests
import requests, json
from app.database import settings
from app.database import SessionLocal
from app.models import Stock

db = SessionLocal()
tickers = [
    'GTCO', 'ZENITHBANK', 'UBA', 'STANBIC', 'FIDELITYBK', 'FCMB',
    'MTNN', 'AIRTELAFRI', 'DANGCEM', 'JBERGER', 'NB', 'GUINNESS',
    'NESTLE', 'CADBURY', 'UNILEVER', 'PZ', 'NASCON', 'OKOMUOIL',
    'PRESCO', 'SEPLAT', 'GEREGU', 'TRANSCORP', 'BUACEMENT', 'BUAFOODS'
]
found   = [t for t in tickers if db.query(Stock).filter(Stock.ticker==t).first()]
missing = [t for t in tickers if not db.query(Stock).filter(Stock.ticker==t).first()]
print(f'In DB ({len(found)}): {found}')
print(f'Missing ({len(missing)}): {missing}')
db.close()