from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.candle import Candle

router = APIRouter()


@router.get("/{timeframe}")
async def get_candles(
    timeframe: str,
    limit: int = Query(100, ge=1, le=5000),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Candle).filter(
        Candle.symbol == "XAUUSD",
        Candle.timeframe == timeframe
    )
    
    if start:
        query = query.filter(Candle.timestamp >= start)
    if end:
        query = query.filter(Candle.timestamp <= end)
    
    candles = query.order_by(Candle.timestamp.desc()).limit(limit).all()
    
    return [{
        "timestamp": candle.timestamp.isoformat(),
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume
    } for candle in reversed(candles)]


@router.get("/{timeframe}/gaps")
async def get_gaps(
    timeframe: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    candles = db.query(Candle).filter(
        Candle.symbol == "XAUUSD",
        Candle.timeframe == timeframe,
        Candle.timestamp >= start_time,
        Candle.timestamp <= end_time
    ).order_by(Candle.timestamp.asc()).all()
    
    if not candles:
        return {"gaps": [], "message": f"No data found for {timeframe} in the last {days} days"}
    
    timeframe_minutes = {
        "1min": 1, "5min": 5, "15min": 15, "30min": 30,
        "1h": 60, "4h": 240, "1d": 1440
    }
    
    interval = timeframe_minutes.get(timeframe, 5)
    gaps = []
    
    for i in range(len(candles) - 1):
        current = candles[i]
        next_candle = candles[i + 1]
        expected_next = current.timestamp + timedelta(minutes=interval)
        
        if next_candle.timestamp > expected_next:
            gap_minutes = (next_candle.timestamp - expected_next).total_seconds() / 60
            if gap_minutes >= interval:
                gaps.append({
                    "start": current.timestamp.isoformat(),
                    "end": next_candle.timestamp.isoformat(),
                    "missing_candles": int(gap_minutes / interval)
                })
    
    return {
        "gaps": gaps,
        "total_gaps": len(gaps),
        "timeframe": timeframe,
        "period_days": days
    }
