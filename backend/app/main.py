"""
main.py
FastAPI application entry point.
Creates DB tables, configures middleware, and registers routers.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import Stock, DailyPrice, User

# ── Create database tables ────────────────────────────────────────────────────
# Runs on startup — creates tables if they don't exist. Safe to run repeatedly.
Base.metadata.create_all(bind=engine)

# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="TradeIQ API",
    description="NGX market analysis and signals dashboard — backend API.",
    version="1.0.0",
    docs_url="/api/docs",       # Swagger UI at /api/docs
    redoc_url="/api/redoc",     # ReDoc at /api/redoc
)

# ── CORS middleware ───────────────────────────────────────────────────────────
# Allows the React frontend (Vite, port 5173) to call this API.
# Lock allow_origins to your exact frontend URL in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # fallback
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
# Uncomment each router as it is built.
from app.routers.stocks  import router as stocks_router
from app.routers.prices  import router as prices_router
# from app.routers.signals import router as signals_router

app.include_router(stocks_router,  prefix="/api/v1", tags=["stocks"])
app.include_router(prices_router,  prefix="/api/v1", tags=["prices"])
# app.include_router(signals_router, prefix="/api/v1", tags=["signals"])

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def health_check():
    """Confirms the API is running — used by CI/CD pipeline."""
    return {"status": "ok", "app": "TradeIQ API", "version": "1.0.0"}