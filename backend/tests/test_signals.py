"""
test_signals.py
Integration tests for signals endpoints.
"""

import pytest
from app.models import Stock, DailyPrice
from decimal import Decimal
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app


def seed_stock(db, ticker="DANGCEM"):
    stock = Stock(
        ticker=ticker,
        full_name="Dangote Cement Plc",
        sector="Industrial Goods"
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


def seed_prices(db, stock, days=30):
    """Seed N days of price data for a stock."""
    for i in range(days):
        db.add(DailyPrice(
            stock_id=stock.id,
            date=date.today() - timedelta(days=days - i),
            open=Decimal("1000"),
            high=Decimal("1050"),
            low=Decimal("950"),
            close=Decimal(str(1000 + i * 2)),
            volume=1000000,
            source="test",
        ))
    db.commit()


class TestGetSignal:
    """Tests for GET /api/v1/signals/{ticker}"""

    def test_happy_path_returns_signal(self, client, db):
        stock = seed_stock(db)
        seed_prices(db, stock, days=30)
        response = client.get("/api/v1/signals/DANGCEM")
        assert response.status_code == 200

    def test_response_shape(self, client, db):
        stock = seed_stock(db)
        seed_prices(db, stock, days=30)
        data = client.get("/api/v1/signals/DANGCEM").json()
        for field in ["ticker", "date", "close", "change_pct",
                      "ma7", "signal", "signal_reason"]:
            assert field in data

    def test_invalid_ticker_returns_404(self, client, db):
        response = client.get("/api/v1/signals/FAKECORP")
        assert response.status_code == 404

    def test_no_price_data_returns_404(self, client, db):
        """Stock exists but no prices — should return 404."""
        seed_stock(db)
        response = client.get("/api/v1/signals/DANGCEM")
        assert response.status_code == 404

    def test_insufficient_data_ma30_is_none(self, client, db):
        """Only 10 days — MA30 should be None."""
        stock = seed_stock(db)
        seed_prices(db, stock, days=10)
        data = client.get("/api/v1/signals/DANGCEM").json()
        assert data["ma30"] is None

    def test_signals_endpoint_is_public(self, client, db):
        """Signals endpoint is public — no auth required."""
        from fastapi.testclient import TestClient
        from app.main import app
        raw = TestClient(app)
        response = raw.get("/api/v1/signals/FAKECORP")
        assert response.status_code == 404  # public but stock not found

    def test_signal_value_is_valid(self, client, db):
        stock = seed_stock(db)
        seed_prices(db, stock, days=30)
        data = client.get("/api/v1/signals/DANGCEM").json()
        assert data["signal"] in [
            "bullish", "bearish", "neutral", "overbought", "oversold"
        ]

    def test_signal_reason_not_empty(self, client, db):
        stock = seed_stock(db)
        seed_prices(db, stock, days=30)
        data = client.get("/api/v1/signals/DANGCEM").json()
        assert len(data["signal_reason"]) > 20


class TestGetAllSignals:
    """Tests for GET /api/v1/signals/all"""
    def test_signals_all_publicly_accessible(self, client, db):
        raw = TestClient(app)
        response = raw.get("/api/v1/signals/all")
        assert response.status_code == 200  # public

    def test_returns_list(self, client, db):
        response = client.get("/api/v1/signals/all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_returns_empty_when_no_data(self, client, db):
        """No stocks or prices — returns empty list, not error."""
        response = client.get("/api/v1/signals/all")
        assert response.json() == []

    def test_returns_signals_for_seeded_stocks(self, client, db):
        stock = seed_stock(db)
        seed_prices(db, stock, days=30)
        data = client.get("/api/v1/signals/all").json()
        assert len(data) >= 1

    def test_signals_all_publicly_accessible(self, client, db):
        """Signals/all is public — returns 200 without token."""
        from fastapi.testclient import TestClient
        from app.main import app
        raw = TestClient(app)
        response = raw.get("/api/v1/signals/all")
        assert response.status_code == 200