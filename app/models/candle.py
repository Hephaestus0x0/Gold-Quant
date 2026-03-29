from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.core.database import Base


class Candle(Base):
    __tablename__ = "candles"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timeframe = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    
    __table_args__ = (
        Index("ix_candles_symbol_timeframe_timestamp", "symbol", "timeframe", "timestamp", unique=True),
    )
