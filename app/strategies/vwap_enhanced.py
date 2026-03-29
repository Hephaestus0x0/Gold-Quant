import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Optional, Dict, Any, Tuple


class VWAPEnhancedStrategy:
    """EMA Momentum + VWAP + Session Analysis strategy for gold."""
    
    def __init__(self, fast_period: int = 9, slow_period: int = 21):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.name = "VWAP Enhanced EMA"
        
        self.asian_session = (time(0, 0), time(8, 0))
        self.london_session = (time(8, 0), time(16, 0))
        self.ny_session = (time(13, 0), time(22, 0))
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate VWAP (Volume Weighted Average Price)."""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        if 'volume' in df.columns:
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        else:
            vwap = typical_price.rolling(window=20).mean()
        
        return vwap
    
    def detect_session(self, timestamp: datetime) -> str:
        """Detect trading session (Asian/London/NY)."""
        t = timestamp.time()
        
        if self.asian_session[0] <= t < self.asian_session[1]:
            return "ASIAN"
        elif self.london_session[0] <= t < self.london_session[1]:
            return "LONDON"
        elif self.ny_session[0] <= t < self.ny_session[1]:
            return "NY"
        else:
            return "OTHER"
    
    def get_session_levels(self, df: pd.DataFrame, session: str) -> Tuple[float, float]:
        """Get session high and low."""
        df['session'] = df.index.to_series().apply(self.detect_session)
        session_data = df[df['session'] == session].tail(20)
        
        if len(session_data) == 0:
            return None, None
        
        session_high = session_data['high'].max()
        session_low = session_data['low'].min()
        
        return session_high, session_low
    
    def calculate_price_position(self, price: float, vwap: float) -> str:
        """Determine if price is at value, discount, or premium."""
        deviation = ((price - vwap) / vwap) * 100
        
        if abs(deviation) < 0.1:
            return "AT_VALUE"
        elif deviation < -0.1:
            return "DISCOUNT"
        else:
            return "PREMIUM"
    
    def generate_signal(self, candles: list) -> Optional[Dict[str, Any]]:
        """Generate trading signal with VWAP and session analysis."""
        
        if len(candles) < self.slow_period + 30:
            return None
        
        df = pd.DataFrame(candles)
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['open'] = pd.to_numeric(df['open'])
        
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
        
        df['ema_fast'] = df['close'].ewm(span=self.fast_period).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow_period).mean()
        df['vwap'] = self.calculate_vwap(df)
        
        df['atr'] = (df['high'] - df['low']).rolling(window=14).mean()
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        direction = None
        base_confidence = 50
        
        if prev['ema_fast'] <= prev['ema_slow'] and current['ema_fast'] > current['ema_slow']:
            direction = "LONG"
        elif prev['ema_fast'] >= prev['ema_slow'] and current['ema_fast'] < current['ema_slow']:
            direction = "SHORT"
        
        if not direction:
            return None
        
        current_session = self.detect_session(current.name if hasattr(current, 'name') else datetime.utcnow())
        session_high, session_low = self.get_session_levels(df, current_session)
        
        price_position = self.calculate_price_position(current['close'], current['vwap'])
        
        if direction == "LONG" and price_position == "PREMIUM":
            return None
        
        if direction == "SHORT" and price_position == "DISCOUNT":
            return None
        
        if direction == "LONG" and price_position == "DISCOUNT":
            base_confidence += 15
        elif direction == "SHORT" and price_position == "PREMIUM":
            base_confidence += 15
        
        entry_price = current['close']
        atr = current['atr']
        
        if pd.isna(atr) or atr <= 0:
            atr = (current['high'] - current['low']) * 1.5
        
        if direction == "LONG":
            stop_loss = entry_price - (atr * 1.5)
            take_profit_1 = entry_price + (atr * 2.0)
            take_profit_2 = entry_price + (atr * 3.0)
            
            if session_low and entry_price - session_low < atr:
                stop_loss = session_low - (atr * 0.5)
                base_confidence += 10
        else:
            stop_loss = entry_price + (atr * 1.5)
            take_profit_1 = entry_price - (atr * 2.0)
            take_profit_2 = entry_price - (atr * 3.0)
            
            if session_high and session_high - entry_price < atr:
                stop_loss = session_high + (atr * 0.5)
                base_confidence += 10
        
        risk_reward = abs(take_profit_1 - entry_price) / abs(entry_price - stop_loss)
        
        ema_strength = abs(current['ema_fast'] - current['ema_slow']) / atr * 50
        confidence = min(base_confidence + ema_strength, 95)
        
        vwap_distance = abs(current['close'] - current['vwap'])
        
        return {
            "direction": direction,
            "entry_price": float(entry_price),
            "stop_loss": float(stop_loss),
            "take_profit_1": float(take_profit_1),
            "take_profit_2": float(take_profit_2),
            "risk_reward": float(risk_reward),
            "confidence": float(confidence),
            "strategy": self.name,
            "session": current_session,
            "price_position": price_position,
            "vwap": float(current['vwap']),
            "vwap_distance": float(vwap_distance),
            "session_high": float(session_high) if session_high else None,
            "session_low": float(session_low) if session_low else None
        }
