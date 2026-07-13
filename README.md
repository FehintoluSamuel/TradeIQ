# TradeIQ - NGX Market Analysis & Signals Dashboard

> A full-stack Nigerian Exchange (NGX) market analysis platform delivering real-time technical signals, moving averages, and RSI indicators for 24 NGX equities — built for Nigerian retail investors and trading students.

**Live API:** https://tradeiq-12gh.onrender.com/api/docs  
**Status:** Production · v1.0.0

---

## What TradeIQ Does

TradeIQ ingests daily OHLCV price data for 24 NGX-listed equities via the NGX Pulse API, computes technical indicators server-side, and serves a REST API powering a signals dashboard. Each stock gets a plain-English signal explanation — **Bullish**, **Bearish**, **Overbought**, **Oversold**, or **Neutral** — backed by MA crossover and RSI logic.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.9+) |
| Database | PostgreSQL (Supabase) · SQLite (local dev) |
| ORM | SQLAlchemy + Alembic |
| Auth | JWT via python-jose · bcrypt/argon2 password hashing |
| Data Pipeline | NGX Pulse API · APScheduler (daily at 15:30 WAT) |
| Testing | pytest · FastAPI TestClient · 41 tests |
| Temporary Deployment | Render (API) · Supabase (DB) |

---

## Project Structure

```
TradeIQ/
└── backend/
    ├── app/
    │   ├── main.py           # FastAPI entry point
    │   ├── database.py       # SQLAlchemy engine + session
    │   ├── auth.py           # JWT + password hashing
    │   ├── indicators.py     # MA + RSI computation
    │   ├── scraper.py        # NGX Pulse API client
    │   ├── scheduler.py      # APScheduler daily job
    │   ├── models/           # SQLAlchemy ORM models
    │   ├── schemas/          # Pydantic request/response schemas
    │   └── routers/          # API endpoint handlers
    ├── tests/                # pytest test suite (41 tests)
    ├── seed/                 # Historical CSV data (git-ignored)
    ├── frontend/             # Vanilla HTML/JS dashboard (prototype)
    ├── requirements.txt
    └── .env                  # Local environment variables (git-ignored)
```

---

## Local Setup

### Prerequisites
- Python 3.9+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/FehintoluSamuel/TradeIQ.git
cd TradeIQ/backend
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create `backend/.env`:
```
DATABASE_URL=sqlite:///./tradeiq.db
ENV=development
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
NGX_PULSE_API_KEY=your-ngx-pulse-key
```

### 5. Run the application
```bash
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/api/docs`

---

## Seed Data

Seed the 24 NGX stocks and backfill price history:

```bash
python seed.py          # Seeds stock metadata
python migrate.py       # Backfills price history via NGX Pulse API
```

---

## Running Tests

```bash
pytest tests/ -v
```

**Test coverage:**
```
test_indicators.py  → 13 tests  (unit — MA, RSI, signal logic)
test_auth.py        → 16 tests  (integration — signup, login, /me)
test_signals.py     → 12 tests  (integration — signal endpoints)
─────────────────────────────────
Total               → 41 tests
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✓ | PostgreSQL or SQLite connection string |
| `SECRET_KEY` | ✓ | JWT signing secret — use a strong random string in production |
| `ALGORITHM` | ✓ | JWT algorithm — `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✓ | Token expiry — `1440` (24 hours) |
| `NGX_PULSE_API_KEY` | ✓ | NGX Pulse API key for live market data |
| `ENV` | ✓ | `development` or `production` |

---

## API Overview

Full interactive documentation: `https://tradeiq-12gh.onrender.com/api/docs`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/signup` | Register a new account |
| POST | `/api/v1/auth/login` | Login — returns JWT token |
| GET | `/api/v1/auth/me` | Current user profile |
| GET | `/api/v1/stocks` | All 24 tracked NGX stocks |
| GET | `/api/v1/stocks/{ticker}` | Single stock metadata |
| GET | `/api/v1/prices/{ticker}` | Historical OHLCV prices |
| GET | `/api/v1/prices/{ticker}/latest` | Most recent price |
| GET | `/api/v1/signals/{ticker}` | Full technical signal |
| GET | `/api/v1/signals/all` | Signal snapshot — all stocks |

---

## Data Pipeline

```
NGX Pulse API
      ↓
scraper.py (fetch → parse → validate)
      ↓
daily_prices table (PostgreSQL)
      ↓
indicators.py (MA7, MA30, RSI computed on request)
      ↓
signals router (REST endpoint)
      ↓
Dashboard
```

Scraper runs automatically at **15:30 WAT** and **16:00 WAT** (retry) daily via APScheduler — triggered after NGX market close.

---

## Signal Logic

| Signal | Condition |
|---|---|
| **Overbought** | RSI > 70 |
| **Oversold** | RSI < 30 |
| **Bullish** | close > MA7 > MA30 AND RSI 50–70 |
| **Bearish** | close < MA7 < MA30 AND RSI < 50 |
| **Neutral** | Everything else |

Every signal includes a plain-English `signal_reason` field written for Nigerian retail investors.

---

## Current Temporary Deployment

### Render (API)
- Connect GitHub repo → Web Service
- Root directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add all environment variables in Render dashboard

### Supabase (Database)
- Create project → copy connection string → set as `DATABASE_URL`

---

## Known Limitations (V1)

- `high_price` and `low_price` from NGX Pulse are `null` for most entries — stored as `close` value. Full OHLC requires a paid data tier.
- Free Render instance spins down after inactivity i.e first request may take 50 seconds.
- News API requires NGX Pulse Starter plan which is deferred to v2.

---

## Roadmap

```
V2:
├── Blazor frontend (C# — in progress)
├── AI explain endpoint (Anthropic API microservice)
├── Market news microservice
├── JWT stored in httpOnly cookies
├── React Native mobile app
└── Docker + self-hosted deployment
```

---

## Author

**Fehintolu Samuel**  
Materials Engineer → Software Engineer  
[GitHub](https://github.com/FehintoluSamuel)

---

## Disclaimer

TradeIQ is built for **educational purposes only**. Signals and indicators are not financial advice. Always consult a licensed financial advisor before making investment decisions. Past market performance does not guarantee future results.
