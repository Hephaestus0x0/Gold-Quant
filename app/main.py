from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

from app.core.config import settings
from app.core.scheduler import scheduler
from app.api import health, status, candles, dashboard, chart

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Gold Quant...")
    
    if settings.ENABLE_SCHEDULER:
        scheduler.start()
        logger.info("✅ APScheduler started")
    
    yield
    
    if settings.ENABLE_SCHEDULER:
        scheduler.shutdown()
        logger.info("⏹️  APScheduler shutdown")


app = FastAPI(
    title="GoldQuant",
    version="0.1.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health.router, tags=["health"])
app.include_router(status.router, tags=["status"])
app.include_router(candles.router, prefix="/candles", tags=["candles"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(chart.router, prefix="/chart", tags=["chart"])


@app.get("/")
async def root():
    return {"message": "Gold Quant API", "version": "0.1.0"}
