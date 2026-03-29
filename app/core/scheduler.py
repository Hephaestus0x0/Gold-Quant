from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="UTC")


def refresh_candles():
    logger.info("📊 Refreshing candles...")


def run_signal_scanner():
    logger.info("🔍 Running signal scanner...")


def check_outcomes():
    logger.info("📈 Checking outcomes...")


def run_backtests():
    logger.info("🧪 Running backtests...")


def param_optimizer():
    logger.info("⚡ Optimizing parameters...")


def data_retention():
    logger.info("🗑️  Data retention cleanup...")


def health_digest():
    logger.info("💊 Sending health digest...")


scheduler.add_job(
    refresh_candles,
    trigger=IntervalTrigger(minutes=30),
    id="refresh_candles_H1",
    name="Refresh Candles",
    replace_existing=True
)

scheduler.add_job(
    run_signal_scanner,
    trigger=IntervalTrigger(minutes=30),
    id="run_signal_scanner",
    name="Signal Scanner",
    replace_existing=True
)

scheduler.add_job(
    check_outcomes,
    trigger=IntervalTrigger(seconds=90),
    id="check_outcomes",
    name="Check Outcomes",
    replace_existing=True
)

scheduler.add_job(
    run_backtests,
    trigger=IntervalTrigger(hours=4),
    id="run_backtests",
    name="Run Backtests",
    replace_existing=True
)

scheduler.add_job(
    param_optimizer,
    trigger=IntervalTrigger(hours=6),
    id="param_optimizer",
    name="Param Optimizer",
    replace_existing=True
)

scheduler.add_job(
    data_retention,
    trigger=CronTrigger(hour=3, minute=0),
    id="data_retention",
    name="Data Retention",
    replace_existing=True
)

scheduler.add_job(
    health_digest,
    trigger=CronTrigger(hour=6, minute=0),
    id="health_digest",
    name="Health Digest",
    replace_existing=True
)
