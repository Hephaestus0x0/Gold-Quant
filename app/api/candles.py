from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db

router = APIRouter()


@router.get("/{timeframe}")
async def get_candles(
    timeframe: str,
    limit: int = Query(100, ge=1, le=5000),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    return []


@router.get("/{timeframe}/gaps")
async def get_gaps(
    timeframe: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    return []
