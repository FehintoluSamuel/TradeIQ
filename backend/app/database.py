"""
database.py
Manages the SQLAlchemy engine, session factory, 
declarative base, and the FastAPI database dependency.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


# ── Settings ────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str
    ENV: str = "development"

    model_config = ConfigDict(env_file=".env")


# ── Engine ───────────────────────────────────────────────────────────────────
# echo=True prints all SQL queries to the terminal in development.
# Automatically silenced in production.

settings = Settings()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only — remove for PostgreSQL
    echo=settings.ENV == "development",
)


# ── Session factory ──────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ── Declarative base ─────────────────────────────────────────────────────────
# All models in models/ inherit from this Base.

Base = declarative_base()


# ── FastAPI dependency ────────────────────────────────────────────────────────
# Injected into every router that needs DB access.
# The finally block guarantees the session closes even if a request crashes.

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Public interface ──────────────────────────────────────────────────────────
#This is everything that gets imported when you do `from database import *`.

all = ["Base", "engine", "get_db", "SessionLocal", "settings"]