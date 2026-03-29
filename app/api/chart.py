from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candle import Candle
from app.models.signal import Signal

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def chart_page(request: Request):
    return templates.TemplateResponse("chart.html", {"request": request})


@router.get("/candles")
async def get_chart_candles(
    limit: int = Query(500),
    timeframe: str = Query("5min"),
    db: Session = Depends(get_db)
):
    candles = db.query(Candle).filter(
        Candle.symbol == "XAUUSD",
        Candle.timeframe == timeframe
    ).order_by(Candle.timestamp.desc()).limit(limit).all()
    
    return [{
        "timestamp": candle.timestamp.isoformat(),
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume
    } for candle in reversed(candles)]


@router.get("/signals")
async def get_chart_signals(
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    signals = db.query(Signal).order_by(
        Signal.created_at.desc()
    ).limit(limit).all()
    
    return [{
        "id": signal.id,
        "direction": signal.direction,
        "entry_price": signal.entry_price,
        "stop_loss": signal.stop_loss,
        "take_profit_1": signal.take_profit_1,
        "take_profit_2": signal.take_profit_2,
        "risk_reward": signal.risk_reward,
        "confidence": signal.confidence,
        "created_at": signal.created_at.isoformat(),
        "status": signal.status
    } for signal in reversed(signals)]
