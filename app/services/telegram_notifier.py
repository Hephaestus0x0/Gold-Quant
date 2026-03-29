import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_signal(self, signal_data: dict):
        """Send trading signal alert to Telegram."""
        
        direction = signal_data.get("direction", "").upper()
        emoji = "🟢" if direction == "LONG" else "🔴"
        
        message = f"""
{emoji} **{direction} Signal** - {signal_data.get('strategy', 'Unknown')}

💵 Entry: ${signal_data.get('entry_price', 0):.2f}
🛑 SL: ${signal_data.get('stop_loss', 0):.2f}
🎯 TP1: ${signal_data.get('take_profit_1', 0):.2f}
🎯 TP2: ${signal_data.get('take_profit_2', 0):.2f}
📊 R:R: 1:{signal_data.get('risk_reward', 0):.1f}
⚡ Confidence: {signal_data.get('confidence', 0):.0f}%
        """
        
        await self._send_message(message)
    
    async def send_health_digest(self, health_data: dict):
        """Send daily health digest to Telegram."""
        
        message = f"""
💊 **Gold Quant Health Digest**

⏰ Uptime: {health_data.get('uptime', 'N/A')}
💾 Database: {health_data.get('database', 'N/A')}
📈 Active Signals: {health_data.get('active_signals', 0)}
📊 Win Rate: {health_data.get('win_rate', 0):.1f}%
💰 Total P&L: {health_data.get('total_pnl', 0):.1f} pips
        """
        
        await self._send_message(message)
    
    async def _send_message(self, text: str):
        """Send message via Telegram Bot API."""
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured, skipping notification")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": "Markdown"
                    }
                )
                response.raise_for_status()
                logger.info("Telegram notification sent")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")


telegram_notifier = TelegramNotifier()
