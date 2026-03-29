import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta

from app.models.signal import Signal
from app.models.outcome import Outcome

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Prevent signal generation during losing streaks."""
    
    def __init__(self, max_consecutive_losses: int = 8):
        self.max_consecutive_losses = max_consecutive_losses
    
    def is_active(self, db: Session) -> bool:
        """Check if circuit breaker should block new signals."""
        
        recent_signals = db.query(Signal).join(Outcome).order_by(
            desc(Signal.created_at)
        ).limit(self.max_consecutive_losses).all()
        
        if len(recent_signals) < self.max_consecutive_losses:
            return False
        
        consecutive_losses = 0
        
        for signal in recent_signals:
            outcome = db.query(Outcome).filter(
                Outcome.signal_id == signal.id
            ).first()
            
            if outcome and outcome.result == "sl_hit":
                consecutive_losses += 1
            else:
                break
        
        is_active = consecutive_losses >= self.max_consecutive_losses
        
        if is_active:
            logger.warning(f"🚨 Circuit breaker ACTIVE - {consecutive_losses} consecutive losses")
        
        return is_active
    
    def get_status(self, db: Session) -> dict:
        """Get circuit breaker status for diagnostics."""
        
        recent_signals = db.query(Signal).join(Outcome).order_by(
            desc(Signal.created_at)
        ).limit(self.max_consecutive_losses).all()
        
        consecutive_losses = 0
        for signal in recent_signals:
            outcome = db.query(Outcome).filter(Outcome.signal_id == signal.id).first()
            if outcome and outcome.result == "sl_hit":
                consecutive_losses += 1
            else:
                break
        
        return {
            "active": consecutive_losses >= self.max_consecutive_losses,
            "consecutive_losses": consecutive_losses,
            "threshold": self.max_consecutive_losses
        }


circuit_breaker = CircuitBreaker(max_consecutive_losses=8)
