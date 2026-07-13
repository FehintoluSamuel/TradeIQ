"""
TradeIQ Market Intelligence Microservice
=========================================

Serves four things behind a single FastAPI app:
  1. GET /market/snapshot            -> NGX daily market data
  2. GET /market/snapshot/explained  -> Same data, explained in plain English (Groq/Llama)
  3. GET /market/news                -> Raw NGX-related headlines (NewsAPI)
  4. GET /market/news/explained      -> Headlines rewritten in plain English (Groq/Llama)
  5. GET /healthz                    -> liveness/readiness probe

Design goals
------------
- Single file, easy to read top-to-bottom, easy to deploy (one process, one port).
- All secrets come from the environment. Nothing sensitive is hardcoded.
- Upstream calls are async (httpx) so the service stays responsive under load.
- Short-lived in-memory TTL cache in front of each upstream, so bursts of
  requests from your app don't multiply into bursts of requests to NGX /
  NewsAPI / Groq (which are rate-limited and/or billed per call).
- Every upstream failure is caught and turned into a clean HTTP error with a
  useful message instead of a stack trace leaking to the client.
- Structured logging with request IDs, so you can trace a slow/broken
  request through logs in production.

Running it
----------
    cp .env.example .env      # fill in your real keys
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

Or with the built-in dev runner:
    python main.py
"""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Callable, Coroutine

import httpx
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from groq import Groq
except ImportError:  # pragma: no cover - handled at startup, not import time
    Groq = None  # type: ignore


# ---------------------------------------------------------------------------
# Configuration — all from environment variables / .env, nothing hardcoded.
# ---------------------------------------------------------------------------
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # NGX market data provider
    ngx_base_url: str = Field(default="https://api.ngnmarket.com/v1")
    ngx_api_key: str = Field(..., description="NGX market data API key")

    # NewsAPI.org
    newsapi_key: str = Field(..., description="NewsAPI.org API key")
    newsapi_url: str = Field(default="https://newsapi.org/v2/everything")
    news_query: str = Field(default="NGX AND (stocks OR dividend OR economy)")
    news_page_size: int = Field(default=5, ge=1, le=20)

    # Groq (LLM plain-English explanations)
    groq_api_key: str = Field(..., description="Groq API key")
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    groq_max_articles: int = Field(default=3, ge=1, le=10)

    # Cache / networking behaviour
    cache_ttl_seconds: int = Field(default=60, description="How long to cache upstream responses")
    upstream_timeout_seconds: float = Field(default=10.0)

    # Service
    port: int = Field(default=8000)
    log_level: str = Field(default="INFO")


settings = Settings()  # raises a clear pydantic ValidationError at boot if a required key is missing


# ---------------------------------------------------------------------------
# Logging — structured enough to grep, no external dependency required.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("tradeiq")


# ---------------------------------------------------------------------------
# Tiny async-safe TTL cache helper.
# One cache instance per upstream so a slow news cache doesn't evict a hot
# market-snapshot entry. `maxsize` is generous since values here are small.
# ---------------------------------------------------------------------------
_snapshot_cache: TTLCache = TTLCache(maxsize=8, ttl=settings.cache_ttl_seconds)
_news_cache: TTLCache = TTLCache(maxsize=8, ttl=settings.cache_ttl_seconds)
_explained_cache: TTLCache = TTLCache(maxsize=8, ttl=settings.cache_ttl_seconds * 5)  # LLM calls are expensive; hold longer
_snapshot_explained_cache: TTLCache = TTLCache(maxsize=8, ttl=settings.cache_ttl_seconds * 5)


def cached(cache: TTLCache, key: str):
    """Decorator: memoize an async function's result in `cache` under `key` for its TTL."""

    def decorator(fn: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            if key in cache:
                logger.debug("cache hit key=%s", key)
                return cache[key]
            result = await fn(*args, **kwargs)
            cache[key] = result
            return result

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Shared HTTP client — created once at startup, reused across requests.
# Reusing a client (instead of `requests.get` per call, or a fresh httpx
# client per call) keeps connections pooled and is the main thing that makes
# this scale under concurrent load.
# ---------------------------------------------------------------------------
http_client: httpx.AsyncClient | None = None
groq_client: "Groq | None" = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global http_client, groq_client
    http_client = httpx.AsyncClient(timeout=settings.upstream_timeout_seconds)
    if Groq is None:
        raise RuntimeError("groq package not installed. Run: pip install groq")
    groq_client = Groq(api_key=settings.groq_api_key)
    logger.info("TradeIQ microservice starting up (cache_ttl=%ss)", settings.cache_ttl_seconds)
    yield
    await http_client.aclose()
    logger.info("TradeIQ microservice shut down cleanly")


app = FastAPI(
    title="TradeIQ Market Intelligence Service",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request-ID + timing middleware — makes every log line traceable and every
# response tell you how long it took, without extra dependencies.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.monotonic()
    logger.info("[%s] -> %s %s", request_id, request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("[%s] unhandled error", request_id)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "request_id": request_id},
        )
    duration_ms = (time.monotonic() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info("[%s] <- %s (%.1fms)", request_id, response.status_code, duration_ms)
    return response


# ---------------------------------------------------------------------------
# Upstream: NGX market snapshot
# ---------------------------------------------------------------------------
class UpstreamError(Exception):
    """Raised when a third-party API fails or returns something unexpected."""

    def __init__(self, service: str, detail: str, status_code: int = 502):
        self.service = service
        self.detail = detail
        self.status_code = status_code
        super().__init__(f"{service}: {detail}")


@cached(_snapshot_cache, key="snapshot")
async def fetch_ngx_snapshot() -> dict:
    assert http_client is not None
    url = f"{settings.ngx_base_url}/market/snapshot"
    headers = {
        "Authorization": f"Bearer {settings.ngx_api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = await http_client.get(url, headers=headers)
    except httpx.RequestError as e:
        raise UpstreamError("ngx", f"network error contacting NGX API: {e}") from e

    if resp.status_code != 200:
        raise UpstreamError("ngx", f"NGX API returned {resp.status_code}: {resp.text[:200]}", resp.status_code)

    payload = resp.json()
    market = payload.get("data", {})
    if not market:
        raise UpstreamError("ngx", "NGX API returned an empty payload")

    mcap = market.get("market_cap", {}) or {}
    breadth = market.get("breadth", {}) or {}

    # Normalize into a stable shape your app can rely on, defaulting missing
    # numeric fields to 0 instead of letting `None` blow up downstream
    # formatting/consumers.
    return {
        "date": (market.get("date") or "")[:10],
        "all_share_index": market.get("asi") or 0,
        "asi_change": market.get("asi_change") or 0,
        "asi_change_percent": market.get("asi_change_percent") or 0,
        "ytd_change_percent": market.get("ytd_asi_change_percent") or 0,
        "deals": market.get("deals") or 0,
        "volume": market.get("volume") or 0,
        "value_traded": market.get("value_traded") or 0,
        "market_cap": {
            "equities": mcap.get("equity") or 0,
            "total": mcap.get("total") or 0,
        },
        "breadth": {
            "advancers": breadth.get("advancers") or 0,
            "decliners": breadth.get("decliners") or 0,
            "unchanged": breadth.get("unchanged") or 0,
        },
    }


# ---------------------------------------------------------------------------
# Upstream: NewsAPI headlines
# ---------------------------------------------------------------------------
@cached(_news_cache, key="news")
async def fetch_market_news() -> list[dict]:
    assert http_client is not None
    headers = {
        "X-Api-Key": settings.newsapi_key,
        "User-Agent": "TradeIQ/1.0",
    }
    params = {
        "q": settings.news_query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": settings.news_page_size,
    }
    try:
        resp = await http_client.get(settings.newsapi_url, headers=headers, params=params)
    except httpx.RequestError as e:
        raise UpstreamError("newsapi", f"network error contacting NewsAPI: {e}") from e

    content_type = resp.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise UpstreamError("newsapi", f"expected JSON, got '{content_type}': {resp.text[:200]}")

    payload = resp.json()
    if resp.status_code != 200:
        raise UpstreamError(
            "newsapi",
            f"{payload.get('code', 'error')}: {payload.get('message', resp.text[:200])}",
            resp.status_code,
        )

    articles = payload.get("articles", [])
    return [
        {
            "title": a.get("title") or "Market Update",
            "description": a.get("description") or "No brief excerpt provided.",
            "source": (a.get("source") or {}).get("name") or "Local Press",
            "published_at": (a.get("publishedAt") or "")[:10],
            "url": a.get("url"),
        }
        for a in articles
    ]


# ---------------------------------------------------------------------------
# Upstream: Groq plain-English explanation
# ---------------------------------------------------------------------------
def _build_explainer_prompt(title: str, description: str) -> str:
    return (
        "You are an expert financial educator. Take this headline and summary:\n"
        f"Headline: {title}\n"
        f"Snippet: {description}\n\n"
        "Rewrite and expand this into a complete, self-contained, 8-to-10 sentence "
        "paragraph for everyday retail-app users who don't know Wall Street jargon. "
        "Fix any broken or truncated sentences, and explain briefly why this matters "
        "to an average person. Aim for at least 80 words. Return only the paragraph, "
        "no preamble."
    )


async def _explain_one(article: dict) -> dict:
    """Runs the (sync) Groq SDK call in a worker thread so it doesn't block the event loop."""
    import asyncio

    assert groq_client is not None
    prompt = _build_explainer_prompt(article["title"], article["description"])

    def _call() -> str:
        response = groq_client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    try:
        explanation = await asyncio.to_thread(_call)
    except Exception as e:
        logger.warning("groq explanation failed for '%s': %s", article["title"], e)
        explanation = article["description"]  # graceful fallback, never fail the whole request

    return {**article, "explanation": explanation}


@cached(_explained_cache, key="explained")
async def fetch_explained_news() -> list[dict]:
    import asyncio

    articles = await fetch_market_news()
    top = articles[: settings.groq_max_articles]
    # Fan out the LLM calls concurrently instead of one-by-one.
    return list(await asyncio.gather(*(_explain_one(a) for a in top)))


def _build_snapshot_prompt(snapshot: dict) -> str:
    return (
        "You are an expert financial educator explaining the Nigerian Stock "
        "Exchange (NGX) to an everyday retail-app user with no finance background.\n\n"
        "Here is today's market snapshot as structured data:\n"
        f"{snapshot}\n\n"
        "Write a self-contained, 8-to-10 sentence plain-English explanation of what "
        "this means. Cover: whether the market went up or down and by how much, what "
        "the year-to-date trend suggests, whether more stocks rose or fell today "
        "(market sentiment), and one sentence on why this matters to an average "
        "investor. Avoid jargon; explain any financial term you use in the same "
        "sentence. Return only the paragraph, no preamble."
    )


async def _explain_snapshot(snapshot: dict) -> str:
    """Runs the (sync) Groq SDK call in a worker thread so it doesn't block the event loop."""
    import asyncio

    assert groq_client is not None
    prompt = _build_snapshot_prompt(snapshot)

    def _call() -> str:
        response = groq_client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    try:
        return await asyncio.to_thread(_call)
    except Exception as e:
        logger.warning("groq snapshot explanation failed: %s", e)
        # Graceful fallback: a short factual sentence instead of failing the whole request.
        return (
            f"The All-Share Index moved {snapshot.get('asi_change')} "
            f"({snapshot.get('asi_change_percent')}%) today."
        )


@cached(_snapshot_explained_cache, key="snapshot_explained")
async def fetch_explained_snapshot() -> dict:
    snapshot = await fetch_ngx_snapshot()
    explanation = await _explain_snapshot(snapshot)
    return {**snapshot, "explanation": explanation}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/market/snapshot")
async def market_snapshot():
    try:
        return await fetch_ngx_snapshot()
    except UpstreamError as e:
        logger.error("snapshot fetch failed: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@app.get("/market/snapshot/explained")
async def market_snapshot_explained():
    try:
        return await fetch_explained_snapshot()
    except UpstreamError as e:
        logger.error("explained snapshot fetch failed: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@app.get("/market/news")
async def market_news():
    try:
        return {"articles": await fetch_market_news()}
    except UpstreamError as e:
        logger.error("news fetch failed: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@app.get("/market/news/explained")
async def market_news_explained():
    try:
        return {"articles": await fetch_explained_news()}
    except UpstreamError as e:
        logger.error("explained news fetch failed: %s", e)
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ---------------------------------------------------------------------------
# Dev entrypoint. In production, run via:
#   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)