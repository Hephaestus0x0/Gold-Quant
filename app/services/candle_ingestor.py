import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.services.twelve_data import twelve_data_client
from app.models.candle import Candle
from app.core.config import settings

logger = logging.getLogger(__name__)


class CandleIngestor:
    """Fetch and store OHLCV candles from Twelve Data."""
    
    async def refresh_candles(self, db: Session, timeframe: str = "1h", outputsize: int = 100):
        """Fetch latest candles and store in database."""
        
        logger.info(f"Refreshing {timeframe} candles for {settings.SYMBOL}")
        
        interval_map = {
            "M15": "15min",
            "H1": "1h",
            "H4": "4h",
            "D1": "1day"
        }
        
        api_interval = interval_map.get(timeframe, "1h")
        
        candles_data = await twelve_data_client.get_time_series(
            symbol=settings.SYMBOL,
            interval=api_interval,
            outputsize=outputsize
        )
        
        if not candles_data:
            logger.warning(f"No candle data received for {timeframe}")
            return 0
        
        inserted = 0
        
        for candle_data in candles_data:
            try:
                timestamp = datetime.fromisoformat(candle_data["datetime"].replace("Z", "+00:00"))
                
                existing = db.query(Candle).filter(
                    and_(
                        Candle.symbol == settings.SYMBOL,
                        Candle.timeframe == timeframe,
                        Candle.timestamp == timestamp
                    )
                ).first()
                
                if existing:
                    continue
                
                candle = Candle(
                    symbol=settings.SYMBOL,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    open=float(candle_data["open"]),
                    high=float(candle_data["high"]),
                    low=float(candle_data["low"]),
                    close=float(candle_data["close"]),
                    volume=float(candle_data.get("volume", 0))
                )
                
                db.add(candle)
                inserted += 1
                
            except Exception as e:
                logger.error(f"Error processing candle: {e}")
                continue
        
        if inserted > 0:
            db.commit()
            logger.info(f"Inserted {inserted} new {timeframe} candles")
        
        return inserted


candle_ingestor = CandleIngestor()
