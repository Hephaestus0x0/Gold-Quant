from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, func
from app.core.database import Base


class StrategyPerformance(Base):
    __tablename__ = "strategy_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    period = Column(String, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    total_signals = Column(Integer, nullable=False)
    winning_signals = Column(Integer, nullable=False)
    losing_signals = Column(Integer, nullable=False)
    total_pnl_pips = Column(Float, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
