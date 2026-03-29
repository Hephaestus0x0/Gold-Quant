from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, func
from app.core.database import Base


class Outcome(Base):
    __tablename__ = "outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False, unique=True)
    result = Column(String, nullable=False)
    pnl_pips = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    exit_reason = Column(String, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
