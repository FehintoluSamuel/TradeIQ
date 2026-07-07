"""
conftest.py
Shared fixtures for the TradeIQ test suite.
Uses in-memory SQLite — real database is never touched.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# In-memory test database — disappears after each test
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

@pytest.fixture(scope="function")
def db():
    """
    Fresh in-memory database for every single test.
    Tables created before test → session yielded → tables dropped after.
    scope="function" means this runs fresh for EVERY test function.
    """
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session       # test runs here
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)  # clean slate



@pytest.fixture(scope="function")
def client(db):
    """
    Test client with database dependency swapped to test DB.
    'db' is injected here — client and db share the same session.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

    
@pytest.fixture(scope="function")
def seeded_client(client, db):
    """
    Test client with 5 NGX stocks pre-seeded.
    Use this for any test that needs stocks to exist.
    """
    from app.models import Stock

    stocks = [
        Stock(ticker="DANGCEM", full_name="Dangote Cement Plc",        sector="Industrial Goods"),
        Stock(ticker="GTCO",    full_name="Guaranty Trust Holding Co.", sector="Financial Services"),
        Stock(ticker="MTNN",    full_name="MTN Nigeria Communications", sector="Telecommunications"),
        Stock(ticker="ZENITH",  full_name="Zenith Bank Plc",            sector="Financial Services"),
        Stock(ticker="BUA",     full_name="BUA Foods Plc",              sector="Consumer Goods"),
    ]
    db.add_all(stocks)
    db.commit()
    return client    