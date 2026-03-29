from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON, func
from app.core.database import Base


class OptimizedParams(Base):
    __tablename__ = "optimized_params"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    params = Column(JSON, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    walk_forward_efficiency = Column(Float, nullable=True)
    combinations_tested = Column(Integer, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
