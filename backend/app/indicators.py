"""
indicators.py
Pure Python technical indicator computation — no database access.
Takes lists of prices, returns computed values.
Kept separate from DB logic so functions are independently testable.
"""

from decimal import Decimal
from typing import Optional


def compute_ma(prices: list[Decimal], window: int) -> Optional[Decimal]:
    """
    Compute the moving average over the last N prices.

    Args:
        prices: Chronologically ordered list of closing prices.
        window: Number of periods (e.g. 7 for MA7, 30 for MA30).

    Returns:
        Moving average as Decimal, or None if insufficient data.
    """
    if window <= 0:
        raise ValueError("Window size must be a positive integer.")
    if len(prices) < window:
        return None
    return sum(prices[-window:]) / Decimal(window)


def compute_rsi(prices: list[Decimal], period: int = 14) -> Optional[float]:
    """
    Compute the Relative Strength Index (RSI) over the last N periods.

    Args:
        prices: Chronologically ordered list of closing prices.
        period: Lookback period — default 14 (industry standard).

    Returns:
        RSI as float between 0–100, or None if insufficient data.
    """
    if period <= 0:
        raise ValueError("Period must be a positive integer.")
    if len(prices) < period + 1:
        return None

    relevant = prices[-(period + 1):]
    gains  = []
    losses = []

    for i in range(1, len(relevant)):
        change = relevant[i] - relevant[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(Decimal(0))
        else:
            gains.append(Decimal(0))
            losses.append(abs(change))

    avg_gain = sum(gains) / Decimal(period)
    avg_loss = sum(losses) / Decimal(period)

    if avg_loss == 0:
        return 100.0

    rs  = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))


def determine_signal(
    close: Decimal,
    ma7:   Optional[Decimal],
    ma30:  Optional[Decimal],
    rsi:   Optional[float],
) -> tuple[str, str]:
    """
    Determine the market signal from computed indicator values.
    Checks RSI extremes first, then MA crossover, then defaults to neutral.

    Args:
        close: Latest closing price.
        ma7:   7-day moving average.
        ma30:  30-day moving average.
        rsi:   14-day RSI value.

    Returns:
        Tuple of (signal, reason) where signal is one of:
        'overbought' | 'oversold' | 'bullish' | 'bearish' | 'neutral'
    """
    # ── RSI extremes — checked first ────────────────────────────────────────
    if rsi is not None:
        if rsi > 70:
            return (
                "overbought",
                f"RSI is at {rsi:.1f} — above 70, which suggests the recent "
                f"rally may be overextended. Momentum could slow soon.",
            )
        if rsi < 30:
            return (
                "oversold",
                f"RSI is at {rsi:.1f} — below 30, which means the stock has "
                f"been falling sharply. A reversal is possible but not guaranteed.",
            )

    # ── MA crossover — primary trend signal ─────────────────────────────────
    if ma7 is not None and ma30 is not None:
        if close > ma7 > ma30:
            return (
                "bullish",
                f"The price is above both its 7-day (₦{ma7:,.2f}) and 30-day "
                f"(₦{ma30:,.2f}) averages. This suggests an upward trend with "
                f"momentum behind it."
                + (f" RSI at {rsi:.1f} supports this." if rsi else ""),
            )
        if close < ma7 < ma30:
            return (
                "bearish",
                f"The price has fallen below both its 7-day (₦{ma7:,.2f}) and "
                f"30-day (₦{ma30:,.2f}) averages. This points to a downward "
                f"trend with weakening momentum."
                + (f" RSI at {rsi:.1f} confirms this." if rsi else ""),
            )

    # ── Default ─────────────────────────────────────────────────────────────
    return (
        "neutral",
        "No strong directional signal at this time. The price is moving "
        "within its recent averages without a clear trend.",
    )