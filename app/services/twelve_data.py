import httpx
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class TwelveDataClient:
    BASE_URL = "https://api.twelvedata.com"
    
    def __init__(self):
        self.api_key = settings.TWELVE_DATA_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_time_series(
        self,
        symbol: str,
        interval: str,
        outputsize: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch OHLCV data from Twelve Data API."""
        
        if not self.api_key:
            logger.error("Twelve Data API key not configured")
            return []
        
        params = {
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
            "outputsize": outputsize,
            "format": "JSON"
        }
        
        try:
            response = await self.client.get(f"{self.BASE_URL}/time_series", params=params)
            response.raise_for_status()
            data = response.json()
            
            if "values" not in data:
                logger.error(f"No values in response: {data}")
                return []
            
            return data["values"]
            
        except Exception as e:
            logger.error(f"Error fetching data from Twelve Data: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()


twelve_data_client = TwelveDataClient()
