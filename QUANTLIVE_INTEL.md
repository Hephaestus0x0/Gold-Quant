# QuantLive Intelligence - Reverse Engineered

**Source:** Live system analysis (2026-03-29 08:26 UTC)

## System Status

- **Uptime:** 391,029 seconds (~4.5 days)
- **Database:** Connected
- **Scheduler:** Running (10 jobs)
- **Total Signals:** 26
- **Active Signals:** 0
- **Circuit Breaker:** ACTIVE (8 consecutive losses)

## Last Signal (Live Example)

**Signal #26 - Breakout Expansion Strategy**
```
Direction: SELL
Entry: $4,994.57
Stop Loss: $5,016.72
TP1: $4,961.34
TP2: $4,928.12
Risk:Reward: 1.5:1
Confidence: 75%
Result: SL HIT
P&L: -222.17 pips
Timestamp: 2026-03-16 01:32 UTC
```

## Strategy Insights

### Breakout Expansion (Observed)
- Uses dual TP levels (TP1 & TP2)
- R:R ratio: 1.5:1
- Confidence scoring system
- Currently underperforming (hit SL)

### Circuit Breaker Logic
- **Triggers after:** 8 consecutive losses
- **Status:** Currently ACTIVE
- **Behavior:** Blocks new signals until reset
- **Purpose:** Prevent drawdown during bad market conditions

## Scheduler Timing (Production)

```python
# More precise than my MVP:
M15 candles: cron[minute='1,16,31,46']  # Every 15 mins
H1 candles: cron[minute='1']             # Every hour at :01
H4 candles: cron[hour='0,4,8,12,16,20', minute='1']
D1 candles: cron[hour='0', minute='1']   # Daily at 00:01

Signal scanner: cron[minute='2,32']      # Twice per hour
Check outcomes: interval[0:01:30]        # Every 90 seconds
Backtests: cron[hour='1,5,9,13,17,21', minute='0']  # Every 4h
Param optimization: cron[hour='3,9,15,21', minute='30']  # Every 6h
Data retention: cron[hour='3', minute='0']  # Daily 03:00
Health digest: cron[hour='6', minute='0']   # Daily 06:00
```

## Key Observations

1. **Performance Issues:** 8 consecutive losses suggests strategies need tuning
2. **Risk Management:** Circuit breaker prevents runaway losses
3. **Multiple Strategies:** They have "breakout_expansion" + others
4. **Two TP Levels:** Scale out profits (partial exits)
5. **Outcome Tracking:** Automated P&L calculation every 90s

## What to Add to Gold Quant

### Priority 1 (Critical)
- ✅ Circuit breaker (8 consecutive losses)
- ✅ Outcome detector (check every 90s)
- ✅ Two TP levels per signal

### Priority 2 (Important)
- ⏸️ Precise scheduler timing (match their cron)
- ⏸️ Breakout Expansion strategy
- ⏸️ Confidence-based position sizing

### Priority 3 (Nice to Have)
- ⏸️ Walk-forward validation
- ⏸️ Parameter optimization
- ⏸️ Backtest runner

---

**Conclusion:** Their system is sophisticated but currently underperforming. My EMA Momentum strategy might outperform if tuned correctly. Adding circuit breaker is critical to avoid similar drawdowns.
