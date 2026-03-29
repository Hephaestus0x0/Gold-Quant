from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, func
from app.core.database import Base


class BacktestResult(Base):
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    timeframe = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=False)
    expectancy = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    params_used = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
