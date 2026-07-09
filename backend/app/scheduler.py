"""
scheduler.py
Schedules the NGX data scraper to run daily after market close.
Uses APScheduler — runs inside the FastAPI process.
Schedule: 15:30 WAT (UTC+1) = 14:30 UTC daily.
Retry: once at 16:00 WAT if first run fails.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import SessionLocal
from app.scraper import run_scraper

logger = logging.getLogger(__name__)


# ── Scraper job ───────────────────────────────────────────────────────────────

def scraper_job() -> None:
    """
    Wrapper around run_scraper() for the scheduler.
    Creates its own DB session — closes it when done.
    Logs success or failure clearly.
    """
    logger.info("Scheduled scraper job starting.")
    db = SessionLocal()
    try:
        run_scraper(db)
        logger.info("Scheduled scraper job completed successfully.")
    except Exception as e:
        logger.error(f"Scheduled scraper job failed: {e}")
    finally:
        db.close()


# ── Scheduler setup ───────────────────────────────────────────────────────────

def create_scheduler() -> BackgroundScheduler:
    """
    Create and configure the APScheduler instance.
    Returns configured scheduler — not yet started.
    """
    scheduler = BackgroundScheduler(timezone="Africa/Lagos")

    # Primary run — 15:30 WAT daily (after NGX market close)
    scheduler.add_job(
        scraper_job,
        trigger=CronTrigger(hour=15, minute=30),
        id="daily_scrape",
        name="Daily NGX price scrape",
        replace_existing=True,
    )

    # Retry run — 16:00 WAT daily (30 mins after primary)
    # Inserts 0 rows if primary succeeded (duplicate check handles it)
    scheduler.add_job(
        scraper_job,
        trigger=CronTrigger(hour=16, minute=0),
        id="daily_scrape_retry",
        name="Daily NGX price scrape — retry",
        replace_existing=True,
    )

    return scheduler