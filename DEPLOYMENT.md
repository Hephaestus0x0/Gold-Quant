# Gold Quant - Deployment Guide

**GitHub:** https://github.com/Hephaestus0x0/Gold-Quant  
**Status:** ✅ Code pushed (main branch)

## Quick Deploy to Railway

### 1. Connect Repository
1. Go to: https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose: `Hephaestus0x0/Gold-Quant`

### 2. Add PostgreSQL Database
1. Click "New" → "Database" → "PostgreSQL"
2. Railway will auto-provision the database
3. Copy the `DATABASE_URL` from the database service

### 3. Set Environment Variables
Railway will auto-detect `.env` template, but verify:

```
DATABASE_URL=<from Railway PostgreSQL service>
TWELVE_DATA_API_KEY=74a55796c40c4b228242c015789543ff
TELEGRAM_BOT_TOKEN=8531867795:AAEtC0rFeUX9zf7zhAazyNdYyH3qmgI-9iM
TELEGRAM_CHAT_ID=1013555336
ENABLE_SCHEDULER=true
SYMBOL=XAUUSD
LOG_LEVEL=INFO
```

### 4. Deploy
Railway will automatically:
- Detect `railway.json` config
- Install Python dependencies
- Run database migrations
- Start uvicorn server

### 5. Initialize Database
After first deploy, run once:
```bash
# Via Railway CLI or connect to service:
python scripts/init_db.py
```

Or use Railway's "Run command" feature:
```
python scripts/init_db.py
```

### 6. Verify
- Check logs for "🚀 Starting Gold Quant..."
- Visit: `https://<your-app>.railway.app/health`
- Should return: `{"status":"ok","database":"ok",...}`

### 7. Test Telegram Bot
- Open: https://t.me/GoldQuantSignalBot
- Send `/start`
- Bot should respond (if configured)

## Manual Deployment (Alternative)

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
export DATABASE_URL="postgresql://localhost/goldquant"
python scripts/init_db.py

# Run locally
uvicorn app.main:app --reload
```

### Other Platforms
- **Heroku:** Use `Procfile`
- **Render:** Import from GitHub, use `railway.json` as reference
- **Docker:** Add `Dockerfile` if needed

## Monitoring

### Health Endpoints
- `/health` - Quick health check
- `/status` - Full system diagnostics (scheduler, circuit breaker, etc.)

### Telegram Alerts
You'll receive:
- 📊 Signal alerts (when generated)
- 💊 Daily health digest (06:00 UTC)

### Circuit Breaker
Monitor `/status` → `circuit_breaker.active`
- If `true`: System stopped generating signals after 8 losses
- Manual reset: requires code update or database edit

## Troubleshooting

### No signals generated?
- Check `/status` → circuit breaker might be active
- Check logs for Twelve Data API errors
- Verify H1 candles are being fetched

### Database errors?
- Ensure PostgreSQL is provisioned
- Run `python scripts/init_db.py`
- Check DATABASE_URL is set correctly

### Telegram not working?
- Verify bot token is correct
- Check chat ID matches your Telegram user
- Test bot manually: https://t.me/GoldQuantSignalBot

---

**Next Steps After Deploy:**
1. Monitor first candle refresh (check logs)
2. Wait for first signal scanner run (every 30 mins at :02 and :32)
3. Check Telegram for alerts
4. Review `/dashboard/` UI

**Expected Behavior:**
- Candles refresh automatically (M15 every 15 mins, H1 every hour)
- Signal scanner runs twice per hour (:02, :32)
- Outcome detector checks every 90 seconds
- Telegram alerts sent when signals generated
- Circuit breaker protects from losing streaks

---

**Built:** 2026-03-29 in 30 minutes  
**Status:** Production-ready MVP
