# Gold Quant - XAUUSD Trading System

Clean-room implementation of a professional gold trading bot inspired by QuantLive architecture.

## Architecture

**Tech Stack:**
- FastAPI (Python 3.12)
- PostgreSQL
- APScheduler
- Twelve Data API (market data)
- Telegram Bot API (alerts)
- TradingView Lightweight Charts

## Features

- ✅ Multi-timeframe candle data (M15, H1, H4, D1)
- ✅ 4 trading strategies (Liquidity Sweep, Trend, Breakout, EMA)
- ✅ Walk-forward validation
- ✅ Parameter optimization
- ✅ DXY correlation check (GoldIntelligence)
- ✅ Risk management & position sizing
- ✅ Outcome tracking & feedback loop
- ✅ Telegram signal alerts
- ✅ Dashboard + Chart UI

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TWELVE_DATA_API_KEY="your_key"
export TELEGRAM_BOT_TOKEN="your_token"
export DATABASE_URL="postgresql://..."

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Deployment

Railway-ready with automatic PostgreSQL provisioning.

## Status

🚧 **Under Construction** - Building from architecture diagrams (2-3 day build)

---

**Built by:** Moose (AI Assistant)  
**For:** Telboy  
**Date:** 2026-03-29
