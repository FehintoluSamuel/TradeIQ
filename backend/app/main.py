"""
main.py
FastAPI application entry point.
Creates DB tables, configures middleware, and registers routers.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database import Base, engine
from app.models import Stock, DailyPrice, User
from app.scheduler import create_scheduler
from app.scheduler import scraper_job

from app.auth import get_current_user

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# ── Create database tables ────────────────────────────────────────────────────
# Runs on startup — creates tables if they don't exist. Safe to run repeatedly.
Base.metadata.create_all(bind=engine)
logger = logging.getLogger(__name__)

# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="TradeIQ API",
    description="NGX market analysis and signals dashboard — backend API.",
    version="1.0.0",
    docs_url="/api/docs",       # Swagger UI at /api/docs
    redoc_url="/api/redoc",     # ReDoc at /api/redoc
)

@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    print("=== SCHEDULER STARTED ===")
    print(f"Jobs: {scheduler.get_jobs()}")
    logger.info("Scheduler started — scraper runs at 15:30 and 16:00 WAT daily.")



@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped.")    

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

scheduler = create_scheduler()


app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ── Routers ───────────────────────────────────────────────────────────────────
# Uncomment each router as it is built.
from app.routers.stocks  import router as stocks_router
from app.routers.prices  import router as prices_router
from app.routers.signals import router as signals_router
from app.routers.auth import router as auth_router

app.include_router(stocks_router,  prefix="/api/v1", tags=["stocks"])
app.include_router(prices_router,  prefix="/api/v1", tags=["prices"])
app.include_router(signals_router, prefix="/api/v1", tags=["signals"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def health_check():
    """Confirms the API is running — used by CI/CD pipeline."""
    return {"status": "ok", "app": "TradeIQ API", "version": "1.0.0"}



# ── Manual scraper trigger ──────────────────────────────────────────────────────────────
@app.get("/api/v1/admin/scrape", tags=["admin"])
def trigger_scrape(current_user: User = Depends(get_current_user)):
    """Manually trigger scraper — admin only."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
    scraper_job()
    return {"status": "scraper triggered", "triggered_by": current_user.email}


# ── Temporarily render the frontend──────────────────────────────────────────────────────────────
"""@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

app.mount("/static", StaticFiles(directory="frontend"), name="static")"""

@app.get("/dashboard", include_in_schema=False)
def serve_frontend():
    return FileResponse("frontend/index.html")