"""
models/__init__.py
Imports all models so SQLAlchemy can register them
against Base.metadata when the app starts.
"""

from app.models.stock import Stock
from app.models.daily_price import DailyPrice
from app.models.user import User

__all__ = ["Stock", "DailyPrice", "User"]