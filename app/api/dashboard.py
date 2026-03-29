from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.scheduler import scheduler
from app.models.signal import Signal
from app.models.outcome import Outcome
from app.models.strategy import Strategy
from app.models.backtest import BacktestResult
from app.models.candle import Candle

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/data")
async def dashboard_data(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    active_signals = db.query(Signal).filter(Signal.status == "active").count()
    today_signals = db.query(Signal).filter(Signal.created_at >= today_start).count()
    
    completed_outcomes = db.query(Outcome).filter(Outcome.outcome.in_(["win", "loss"])).all()
    wins = sum(1 for o in completed_outcomes if o.outcome == "win")
    total = len(completed_outcomes)
    win_rate = round((wins / total * 100), 1) if total > 0 else 0
    
    total_pnl = sum((o.exit_price - o.entry_price) if o.outcome == "win" else (o.entry_price - o.stop_loss) for o in completed_outcomes)
    
    latest_candle = db.query(Candle).order_by(Candle.timestamp.desc()).first()
    last_data = latest_candle.timestamp.isoformat() if latest_candle else None
    
    recent_signals = db.query(Signal).order_by(Signal.created_at.desc()).limit(10).all()
    
    strategies = db.query(Strategy).all()
    
    backtest_results = db.query(BacktestResult).order_by(BacktestResult.end_date.desc()).limit(5).all()
    
    scheduler_jobs = [
        {
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        }
        for job in scheduler.get_jobs()
    ]
    
    return {
        "active_signals": active_signals,
        "today_signals": today_signals,
        "win_rate": win_rate,
        "total_pnl_pips": round(total_pnl, 1),
        "uptime": scheduler.state.name if scheduler.state else "unknown",
        "database": "ok",
        "last_data": last_data,
        "scheduler": scheduler.state.name if scheduler.state else "stopped",
        "recent_signals": [
            {
                "id": s.id,
                "direction": s.direction,
                "entry_price": s.entry_price,
                "confidence": s.confidence,
                "status": s.status,
                "created_at": s.created_at.isoformat()
            }
            for s in recent_signals
        ],
        "strategies": [
            {
                "id": st.id,
                "name": st.name,
                "enabled": st.enabled
            }
            for st in strategies
        ],
        "backtest_results": [
            {
                "id": br.id,
                "strategy": br.strategy,
                "win_rate": br.win_rate,
                "profit_factor": br.profit_factor,
                "start_date": br.start_date.isoformat(),
                "end_date": br.end_date.isoformat()
            }
            for br in backtest_results
        ],
        "scheduler_jobs": scheduler_jobs
    }
