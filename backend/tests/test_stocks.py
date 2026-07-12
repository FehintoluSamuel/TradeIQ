"""
test_stocks.py
Integration tests for GET /api/v1/stocks endpoints.
"""

from datetime import datetime
import pytest


class TestGetAllStocks:
    """Tests for GET /api/v1/stocks"""

    def test_returns_empty_list_when_no_stocks(self, client):
        """No stocks seeded — should return empty list, not error."""
        response = client.get("/api/v1/stocks")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_all_stocks_when_seeded(self, seeded_client):
        """5 stocks seeded — should return all 5."""
        response = seeded_client.get("/api/v1/stocks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_response_shape_matches_schema(self, seeded_client):
        """Each stock must have required fields."""
        response = seeded_client.get("/api/v1/stocks")
        stock = response.json()[1]
        assert "id"         in stock
        assert "ticker"     in stock
        assert "full_name"  in stock
        assert "created_at" in stock




class TestGetOneStock:
    """Tests for GET /api/v1/stocks/{ticker}"""

    def test_returns_correct_stock(self, seeded_client):
        response = seeded_client.get("/api/v1/stocks/DANGCEM")
        assert response.status_code == 200
        assert response.json()["ticker"] == "DANGCEM"

    def test_returns_404_for_unknown_ticker(self, seeded_client):
        response = seeded_client.get("/api/v1/stocks/FAKECORP")
        assert response.status_code == 404

    def test_ticker_uppercased_automatically(self, seeded_client):
        """lowercase ticker should still work."""
        response = seeded_client.get("/api/v1/stocks/dangcem")
        assert response.status_code == 200
        assert response.json()["ticker"] == "DANGCEM"

