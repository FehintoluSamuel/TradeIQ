"""
test_indicators.py
Unit tests for MA, RSI and signal computation.
No database or server needed — pure Python functions.
"""

from decimal import Decimal
import pytest
from app.indicators import compute_ma, compute_rsi, determine_signal


# ── compute_ma tests ──────────────────────────────────────────────────────────

def test_compute_ma_happy_path():
    # Arrange
    prices = [Decimal(str(i)) for i in range(100, 170, 10)]
    # prices = [100, 110, 120, 130, 140, 150, 160]
    # Act
    result = compute_ma(prices, 7)
    # Assert — calculate the expected value manually first
    assert result == Decimal("130")  # replace ??? with your calculation


def test_compute_ma_returns_none_when_insufficient_data():
    # Only 3 prices but asking for window=7
    prices = [Decimal("100"), Decimal("110"), Decimal("120")]
    result = compute_ma(prices, 7)
    assert result is None


def test_compute_ma_raises_on_zero_window():
    prices = [Decimal("100"), Decimal("110")]
    with pytest.raises(ValueError):
        compute_ma(prices, 0)


def test_compute_ma_uses_last_n_prices():
    # 8 prices, window=3 — should use LAST 3 not FIRST 3
    prices = [Decimal(str(i)) for i in range(100, 180, 10)]
    # prices = [100, 110, 120, 130, 140, 150, 160, 170]
    # Last 3 = [150, 160, 170] → average = ???
    result = compute_ma(prices, 3)
    assert result == Decimal("160")  # replace with correct value


# ── compute_rsi tests ─────────────────────────────────────────────────────────

def test_compute_rsi_returns_none_when_insufficient_data():
    # RSI needs period+1 prices minimum
    prices = [Decimal("100")] * 5  # only 5 prices, need 15
    result = compute_rsi(prices, period=14)
    assert result is None


def test_compute_rsi_returns_100_when_no_losses():
    # All prices increasing — no losing days — RSI should be 100
    prices = [Decimal(str(i)) for i in range(100, 116)]
    # 16 prices, all going up
    result = compute_rsi(prices, period=14)
    assert result == 100.0


def test_compute_rsi_returns_float():
    prices = [Decimal(str(i)) for i in range(100, 116)]
    result = compute_rsi(prices, period=14)
    assert isinstance(result, float)


# ── determine_signal tests ────────────────────────────────────────────────────

def test_determine_signal_bullish():
    # price above MA7 above MA30, RSI in bullish zone
    signal, reason = determine_signal(
        close=Decimal("150"),
        ma7=Decimal("140"),
        ma30=Decimal("130"),
        rsi=60.0,
    )
    assert signal == "bullish"
    assert len(reason) > 0  # reason is not empty


def test_determine_signal_bearish():
    signal, reason = determine_signal(
        close=Decimal("100"),
        ma7=Decimal("110"),
        ma30=Decimal("120"),
        rsi=40.0,
    )
    assert signal == "bearish"


def test_determine_signal_overbought():
    signal, reason = determine_signal(
        close=Decimal("200"),
        ma7=Decimal("190"),
        ma30=Decimal("180"),
        rsi=75.0,  # above 70
    )
    assert signal == "overbought"


def test_determine_signal_oversold():
    signal, reason = determine_signal(
        close=Decimal("100"),
        ma7=Decimal("110"),
        ma30=Decimal("120"),
        rsi=25.0,  # below 30
    )
    assert signal == "oversold"


def test_determine_signal_neutral():
    signal, reason = determine_signal(
        close=Decimal("130"),
        ma7=Decimal("128"),
        ma30=Decimal("132"),
        rsi=48.0,
    )
    assert signal == "neutral"


def test_determine_signal_reason_is_string():
    signal, reason = determine_signal(
        close=Decimal("150"),
        ma7=Decimal("140"),
        ma30=Decimal("130"),
        rsi=60.0,
    )
    assert isinstance(reason, str)
    assert len(reason) > 20  # not an empty or trivial string