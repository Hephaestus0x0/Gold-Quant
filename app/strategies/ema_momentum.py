import pandas as pd
from typing import Optional, Dict, Any


class EMAMomentumStrategy:
    """Simple EMA crossover strategy for gold."""
    
    def __init__(self, fast_period: int = 9, slow_period: int = 21):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.name = "EMA Momentum"
    
    def generate_signal(self, candles: list) -> Optional[Dict[str, Any]]:
        """Generate trading signal from candle data."""
        
        if len(candles) < self.slow_period + 5:
            return None
        
        df = pd.DataFrame(candles)
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        
        df['ema_fast'] = df['close'].ewm(span=self.fast_period).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow_period).mean()
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        direction = None
        
        if prev['ema_fast'] <= prev['ema_slow'] and current['ema_fast'] > current['ema_slow']:
            direction = "LONG"
        elif prev['ema_fast'] >= prev['ema_slow'] and current['ema_fast'] < current['ema_slow']:
            direction = "SHORT"
        
        if not direction:
            return None
        
        entry_price = current['close']
        atr = (current['high'] - current['low']) * 1.5
        
        if direction == "LONG":
            stop_loss = entry_price - atr
            take_profit_1 = entry_price + (atr * 1.5)
            take_profit_2 = entry_price + (atr * 2.5)
        else:
            stop_loss = entry_price + atr
            take_profit_1 = entry_price - (atr * 1.5)
            take_profit_2 = entry_price - (atr * 2.5)
        
        risk_reward = abs(take_profit_1 - entry_price) / abs(entry_price - stop_loss)
        
        confidence = min(abs(current['ema_fast'] - current['ema_slow']) / atr * 100, 95)
        
        return {
            "direction": direction,
            "entry_price": float(entry_price),
            "stop_loss": float(stop_loss),
            "take_profit_1": float(take_profit_1),
            "take_profit_2": float(take_profit_2),
            "risk_reward": float(risk_reward),
            "confidence": float(confidence),
            "strategy": self.name
        }
