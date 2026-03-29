import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.candle import Candle
from app.models.signal import Signal
from app.models.strategy import Strategy
from app.strategies import EMAMomentumStrategy
from app.services.telegram_notifier import telegram_notifier
from app.services.circuit_breaker import circuit_breaker
from app.core.config import settings

logger = logging.getLogger(__name__)


class SignalPipeline:
    """Orchestrates signal generation from strategies."""
    
    def __init__(self):
        self.strategies = [
            EMAMomentumStrategy(fast_period=9, slow_period=21)
        ]
    
    async def run(self, db: Session):
        """Run signal scanner on latest candles."""
        
        logger.info("Running signal scanner...")
        
        if circuit_breaker.is_active(db):
            logger.warning("⚠️ Circuit breaker active - skipping signal generation")
            return
        
        candles = db.query(Candle).filter(
            Candle.symbol == settings.SYMBOL,
            Candle.timeframe == "H1"
        ).order_by(Candle.timestamp.desc()).limit(100).all()
        
        if len(candles) < 30:
            logger.warning(f"Not enough candles: {len(candles)}")
            return
        
        candles_data = [
            {
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume
            }
            for c in reversed(candles)
        ]
        
        for strategy in self.strategies:
            signal_data = strategy.generate_signal(candles_data)
            
            if signal_data:
                await self._save_and_notify(db, signal_data, strategy.name)
    
    async def _save_and_notify(self, db: Session, signal_data: dict, strategy_name: str):
        """Save signal to database and send Telegram alert."""
        
        strategy = db.query(Strategy).filter(Strategy.name == strategy_name).first()
        
        if not strategy:
            strategy = Strategy(
                name=strategy_name,
                description=f"Auto-generated {strategy_name}",
                enabled=True
            )
            db.add(strategy)
            db.commit()
            db.refresh(strategy)
        
        signal = Signal(
            strategy_id=strategy.id,
            direction=signal_data["direction"],
            entry_price=signal_data["entry_price"],
            stop_loss=signal_data["stop_loss"],
            take_profit_1=signal_data["take_profit_1"],
            take_profit_2=signal_data.get("take_profit_2"),
            risk_reward=signal_data["risk_reward"],
            confidence=signal_data["confidence"],
            status="active"
        )
        
        db.add(signal)
        db.commit()
        
        logger.info(f"✅ New {signal_data['direction']} signal generated")
        
        await telegram_notifier.send_signal(signal_data)


signal_pipeline = SignalPipeline()
