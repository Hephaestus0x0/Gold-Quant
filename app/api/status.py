from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import time

from app.core.database import get_db
from app.core.scheduler import scheduler

router = APIRouter()

start_time = time.time()


@router.get("/status")
async def status(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    
    scheduler_status = "running" if scheduler.running else "stopped"
    
    jobs = [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time,
            "trigger": str(job.trigger)
        }
        for job in scheduler.get_jobs()
    ]
    
    return {
        "status": "ok",
        "uptime_seconds": time.time() - start_time,
        "database": db_status,
        "scheduler": scheduler_status,
        "jobs": jobs,
        "active_signals": 0,
        "last_candle_fetch": None,
        "last_signal_generated": None,
        "timestamp": datetime.utcnow()
    }
