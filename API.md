# TradeIQ API Reference

**Base URL:** `https://tradeiq-12gh.onrender.com/api/v1`  
**Interactive Docs:** `https://tradeiq-12gh.onrender.com/api/docs`  
**Auth:** Bearer JWT token - obtain via `POST /auth/login`

---

## Authentication

All protected endpoints require the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### POST /auth/signup
Register a new account.

**Request body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**Response 201:**
```json
{
  "id": 1,
  "username": "fehintolu",
  "email": "user@example.com",
  "role": "user",
  "is_active": true
}
```

**Errors:** `400` email/username already exists · `422` validation error

---

### POST /auth/login
Authenticate and receive JWT token.

**Request:** `application/x-www-form-urlencoded`
```
username=user@example.com&password=yourpassword
```

**Response 200:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Errors:** `401` invalid credentials · `403` account inactive

---

### GET /auth/me 
Returns the authenticated user's profile.

**Response 200:**
```json
{
  "id": 1,
  "username": "fehintolu",
  "email": "user@example.com",
  "role": "user",
  "is_active": true
}
```

---

## Stocks Endpoints

### GET /stocks 
Returns all 24 tracked NGX stocks.

**Response 200:**
```json
[
  {
    "id": 1,
    "ticker": "DANGCEM",
    "full_name": "Dangote Cement Plc",
    "sector": "Industrial Goods",
    "created_at": "2026-07-01T00:00:00"
  }
]
```

---

### GET /stocks/{ticker} 
Returns a single stock by ticker symbol.

**Path params:** `ticker` — NGX ticker e.g. `DANGCEM`

**Response 200:**
```json
{
  "id": 1,
  "ticker": "DANGCEM",
  "full_name": "Dangote Cement Plc",
  "sector": "Industrial Goods",
  "created_at": "2026-07-01T00:00:00"
}
```

**Errors:** `404` ticker not found

---

## Prices Endpoints

### GET /prices/{ticker}
Returns historical OHLCV prices.

**Path params:** `ticker`  
**Query params:** `limit` (int, default 30) — number of trading days

**Response 200:**
```json
[
  {
    "id": 1,
    "stock_id": 1,
    "date": "2026-07-10",
    "open": "1047.00",
    "high": "1047.00",
    "low": "1047.00",
    "close": "1047.00",
    "volume": 875147,
    "source": "ngx_pulse",
    "created_at": "2026-07-10T15:10:03"
  }
]
```

**Note:** `high` and `low` mirror `close` due to NGX Pulse free tier limitation.

---

### GET /prices/{ticker}/latest
Returns the most recent trading day price.

**Response 200:** Single `DailyPrice` object (same shape as above)

**Errors:** `404` no price data found

---

## Signals Endpoints

### GET /signals/{ticker}
Returns the full technical signal for a stock.

**Response 200:**
```json
{
  "ticker": "DANGCEM",
  "date": "2026-07-10",
  "close": "1047.00",
  "change_pct": 2.31,
  "ma7": "1020.00",
  "ma30": "980.00",
  "rsi": 58.4,
  "signal": "bullish",
  "signal_reason": "The price is above both its 7-day (₦1,020.00) and 30-day (₦980.00) averages. This suggests an upward trend with momentum behind it. RSI at 58.4 supports this."
}
```

**Signal values:** `bullish` · `bearish` · `neutral` · `overbought` · `oversold`

**Errors:** `404` ticker not found or no price data

---

### GET /signals/all
Returns signal snapshot for all 24 tracked stocks.

**Response 200:** Array of signal objects (same shape as above)

**Note:** Stocks with insufficient price history are silently skipped.

---

## Admin Endpoints

### GET /admin/scrape 
Manually trigger the NGX data scraper. **Admin role required.**

**Response 200:**
```json
{
  "status": "scraper triggered",
  "triggered_by": "admin@example.com"
}
```

**Errors:** `401` not authenticated · `403` not admin

---

## Error Response Format

All errors follow this shape:
```json
{
  "detail": "Human-readable error message"
}
```

---

## Currently Tracked Tickers

```
Financial:   GTCO, ZENITHBANK, UBA, STANBIC, FIDELITYBK, FCMB
Telecoms:    MTNN, AIRTELAFRI
Industrial:  DANGCEM, JBERGER
Consumer:    NB, GUINNESS, NESTLE, CADBURY, UNILEVER, PZ, NASCON
Agriculture: OKOMUOIL, PRESCO
Energy:      SEPLAT, GEREGU
Other:       TRANSCORP, BUACEMENT, BUAFOODS
```

---

## Rate Limits

No rate limiting is enforced in v1. Please be considerate with request frequency.

---

## Data Update Schedule

Market data is refreshed daily at **15:30 WAT** and **16:00 WAT** (retry) after NGX market close.
