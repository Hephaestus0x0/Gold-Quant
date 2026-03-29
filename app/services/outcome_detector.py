import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.signal import Signal
from app.models.outcome import Outcome
from app.models.candle import Candle
from app.core.config import settings

logger = logging.getLogger(__name__)


class OutcomeDetector:
    """Check if active signals have hit SL or TP."""
    
    async def check_outcomes(self, db: Session):
        """Check all active signals against latest price action."""
        
        active_signals = db.query(Signal).filter(
            Signal.status == "active"
        ).all()
        
        if not active_signals:
            return
        
        latest_candle = db.query(Candle).filter(
            and_(
                Candle.symbol == settings.SYMBOL,
                Candle.timeframe == "H1"
            )
        ).order_by(Candle.timestamp.desc()).first()
        
        if not latest_candle:
            logger.warning("No candles available for outcome detection")
            return
        
        checked = 0
        
        for signal in active_signals:
            result = self._check_signal_outcome(signal, latest_candle)
            
            if result:
                outcome = Outcome(
                    signal_id=signal.id,
                    result=result["result"],
                    pnl_pips=result["pnl_pips"],
                    exit_price=result["exit_price"],
                    exit_reason=result["reason"]
                )
                
                signal.status = result["result"]
                
                db.add(outcome)
                checked += 1
        
        if checked > 0:
            db.commit()
            logger.info(f"✅ Checked {checked} signal outcomes")
    
    def _check_signal_outcome(self, signal: Signal, candle: Candle) -> dict:
        """Determine if signal hit SL or TP."""
        
        if signal.direction == "LONG":
            if candle.low <= signal.stop_loss:
                pnl = (signal.stop_loss - signal.entry_price) * 100
                return {
                    "result": "sl_hit",
                    "pnl_pips": pnl,
                    "exit_price": signal.stop_loss,
                    "reason": "Stop loss triggered"
                }
            
            if candle.high >= signal.take_profit_2:
                pnl = (signal.take_profit_2 - signal.entry_price) * 100
                return {
                    "result": "tp2_hit",
                    "pnl_pips": pnl,
                    "exit_price": signal.take_profit_2,
                    "reason": "TP2 hit"
                }
            
            if candle.high >= signal.take_profit_1:
                pnl = (signal.take_profit_1 - signal.entry_price) * 100
                return {
                    "result": "tp1_hit",
                    "pnl_pips": pnl,
                    "exit_price": signal.take_profit_1,
                    "reason": "TP1 hit"
                }
        
        else:  # SHORT
            if candle.high >= signal.stop_loss:
                pnl = (signal.entry_price - signal.stop_loss) * 100
                return {
                    "result": "sl_hit",
                    "pnl_pips": pnl,
                    "exit_price": signal.stop_loss,
                    "reason": "Stop loss triggered"
                }
            
            if candle.low <= signal.take_profit_2:
                pnl = (signal.entry_price - signal.take_profit_2) * 100
                return {
                    "result": "tp2_hit",
                    "pnl_pips": pnl,
                    "exit_price": signal.take_profit_2,
                    "reason": "TP2 hit"
                }
            
            if candle.low <= signal.take_profit_1:
                pnl = (signal.entry_price - signal.take_profit_1) * 100
                return {
                    "result": "tp1_hit",
                    "pnl_pips": pnl,
                    "exit_price": signal.take_profit_1,
                    "reason": "TP1 hit"
                }
        
        return None


outcome_detector = OutcomeDetector()
