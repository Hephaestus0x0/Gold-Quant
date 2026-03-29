import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.services.twelve_data import twelve_data_client
from app.strategies.vwap_enhanced import VWAPEnhancedStrategy
from app.strategies.ema_momentum import EMAMomentumStrategy

logger = logging.getLogger(__name__)


class Backtester:
    """Backtest trading strategies on historical data."""
    
    def __init__(self, strategy_class, strategy_params: dict = None):
        self.strategy_params = strategy_params or {}
        self.strategy = strategy_class(**self.strategy_params)
        self.trades = []
        self.equity_curve = []
        self.initial_capital = 10000
        self.current_capital = self.initial_capital
    
    async def fetch_historical_data(
        self,
        symbol: str,
        interval: str,
        months: int = 6
    ) -> pd.DataFrame:
        """Fetch historical candle data from Twelve Data API."""
        
        outputsize = {
            "1min": months * 30 * 24 * 60,
            "5min": months * 30 * 24 * 12,
            "15min": months * 30 * 24 * 4,
            "1h": months * 30 * 24,
            "4h": months * 30 * 6,
            "1day": months * 30
        }.get(interval, 5000)
        
        outputsize = min(outputsize, 5000)
        
        logger.info(f"Fetching {outputsize} candles for {symbol} on {interval}")
        
        raw_data = await twelve_data_client.get_time_series(
            symbol=symbol,
            interval=interval,
            outputsize=outputsize
        )
        
        if not raw_data:
            logger.error("No data received from API")
            return pd.DataFrame()
        
        df = pd.DataFrame(raw_data)
        
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')
        
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col])
        
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
        
        df = df.set_index('datetime')
        
        logger.info(f"Loaded {len(df)} candles from {df.index[0]} to {df.index[-1]}")
        
        return df
    
    def simulate_trade(
        self,
        signal: Dict[str, Any],
        candles_after_signal: pd.DataFrame
    ) -> Dict[str, Any]:
        """Simulate a trade execution and outcome."""
        
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        tp1 = signal['take_profit_1']
        tp2 = signal['take_profit_2']
        direction = signal['direction']
        
        outcome = None
        exit_price = None
        pips = 0
        bars_held = 0
        
        for idx, candle in candles_after_signal.iterrows():
            bars_held += 1
            
            if bars_held > 100:
                outcome = "TIMEOUT"
                exit_price = candle['close']
                break
            
            if direction == "LONG":
                if candle['low'] <= stop_loss:
                    outcome = "LOSS"
                    exit_price = stop_loss
                    pips = (exit_price - entry_price) / 0.01
                    break
                elif candle['high'] >= tp2:
                    outcome = "WIN"
                    exit_price = tp2
                    pips = (exit_price - entry_price) / 0.01
                    break
                elif candle['high'] >= tp1:
                    outcome = "WIN"
                    exit_price = tp1
                    pips = (exit_price - entry_price) / 0.01
                    break
            else:
                if candle['high'] >= stop_loss:
                    outcome = "LOSS"
                    exit_price = stop_loss
                    pips = (entry_price - exit_price) / 0.01
                    break
                elif candle['low'] <= tp2:
                    outcome = "WIN"
                    exit_price = tp2
                    pips = (entry_price - exit_price) / 0.01
                    break
                elif candle['low'] <= tp1:
                    outcome = "WIN"
                    exit_price = tp1
                    pips = (entry_price - exit_price) / 0.01
                    break
        
        if outcome is None:
            outcome = "OPEN"
            exit_price = candles_after_signal.iloc[-1]['close']
            pips = (exit_price - entry_price) / 0.01 if direction == "LONG" else (entry_price - exit_price) / 0.01
        
        risk_amount = abs(entry_price - stop_loss) / entry_price * self.current_capital
        
        if outcome == "WIN":
            profit = abs(exit_price - entry_price) / abs(entry_price - stop_loss) * risk_amount
            self.current_capital += profit
        elif outcome == "LOSS":
            self.current_capital -= risk_amount
        
        return {
            "entry_time": signal.get('entry_time'),
            "direction": direction,
            "entry_price": entry_price,
            "exit_price": float(exit_price),
            "stop_loss": stop_loss,
            "take_profit_1": tp1,
            "take_profit_2": tp2,
            "outcome": outcome,
            "pips": float(pips),
            "bars_held": bars_held,
            "profit_loss": float(self.current_capital - self.initial_capital),
            "equity": float(self.current_capital),
            "confidence": signal.get('confidence'),
            "session": signal.get('session'),
            "price_position": signal.get('price_position')
        }
    
    async def run_backtest(
        self,
        symbol: str = "XAUUSD",
        interval: str = "1h",
        months: int = 6
    ) -> Dict[str, Any]:
        """Run backtest on historical data."""
        
        logger.info(f"Starting backtest: {self.strategy.name} on {symbol} {interval}")
        
        df = await self.fetch_historical_data(symbol, interval, months)
        
        if df.empty:
            logger.error("No data available for backtest")
            return {}
        
        self.trades = []
        self.equity_curve = []
        self.current_capital = self.initial_capital
        
        lookback_period = max(self.strategy.slow_period, 30) + 10
        
        for i in range(lookback_period, len(df) - 50):
            historical_candles = df.iloc[:i].reset_index()
            candles_list = historical_candles.to_dict('records')
            
            signal = self.strategy.generate_signal(candles_list)
            
            if signal:
                signal['entry_time'] = df.index[i]
                
                candles_after = df.iloc[i+1:i+101]
                
                trade_result = self.simulate_trade(signal, candles_after)
                
                self.trades.append(trade_result)
                self.equity_curve.append({
                    'datetime': df.index[i],
                    'equity': self.current_capital
                })
                
                logger.info(f"Trade #{len(self.trades)}: {trade_result['direction']} @ {trade_result['entry_price']:.2f} → {trade_result['outcome']} ({trade_result['pips']:.1f} pips)")
        
        metrics = self.calculate_metrics()
        
        return {
            "strategy": self.strategy.name,
            "symbol": symbol,
            "interval": interval,
            "start_date": df.index[0],
            "end_date": df.index[-1],
            "total_candles": len(df),
            "trades": self.trades,
            "equity_curve": self.equity_curve,
            "metrics": metrics
        }
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        
        if not self.trades:
            return {}
        
        trades_df = pd.DataFrame(self.trades)
        
        total_trades = len(trades_df)
        wins = len(trades_df[trades_df['outcome'] == 'WIN'])
        losses = len(trades_df[trades_df['outcome'] == 'LOSS'])
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        winning_trades = trades_df[trades_df['outcome'] == 'WIN']
        losing_trades = trades_df[trades_df['outcome'] == 'LOSS']
        
        avg_win = winning_trades['pips'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['pips'].mean()) if len(losing_trades) > 0 else 0
        
        total_wins_pips = winning_trades['pips'].sum() if len(winning_trades) > 0 else 0
        total_losses_pips = abs(losing_trades['pips'].sum()) if len(losing_trades) > 0 else 0
        
        profit_factor = (total_wins_pips / total_losses_pips) if total_losses_pips > 0 else 0
        
        equity_series = pd.Series([e['equity'] for e in self.equity_curve])
        peak = equity_series.expanding().max()
        drawdown = (equity_series - peak) / peak * 100
        max_drawdown = abs(drawdown.min())
        
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * avg_loss)
        
        session_performance = {}
        if 'session' in trades_df.columns:
            for session in trades_df['session'].unique():
                session_trades = trades_df[trades_df['session'] == session]
                session_wins = len(session_trades[session_trades['outcome'] == 'WIN'])
                session_total = len(session_trades)
                session_win_rate = (session_wins / session_total * 100) if session_total > 0 else 0
                
                session_performance[session] = {
                    "total_trades": int(session_total),
                    "wins": int(session_wins),
                    "losses": int(len(session_trades[session_trades['outcome'] == 'LOSS'])),
                    "win_rate": float(session_win_rate),
                    "avg_pips": float(session_trades['pips'].mean())
                }
        
        price_position_performance = {}
        if 'price_position' in trades_df.columns:
            for position in trades_df['price_position'].unique():
                pos_trades = trades_df[trades_df['price_position'] == position]
                pos_wins = len(pos_trades[pos_trades['outcome'] == 'WIN'])
                pos_total = len(pos_trades)
                pos_win_rate = (pos_wins / pos_total * 100) if pos_total > 0 else 0
                
                price_position_performance[position] = {
                    "total_trades": int(pos_total),
                    "wins": int(pos_wins),
                    "win_rate": float(pos_win_rate)
                }
        
        consecutive_losses = 0
        max_consecutive_losses = 0
        for trade in self.trades:
            if trade['outcome'] == 'LOSS':
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0
        
        return {
            "total_trades": int(total_trades),
            "wins": int(wins),
            "losses": int(losses),
            "win_rate": float(win_rate),
            "avg_win_pips": float(avg_win),
            "avg_loss_pips": float(avg_loss),
            "profit_factor": float(profit_factor),
            "max_drawdown": float(max_drawdown),
            "sharpe_ratio": float(sharpe_ratio),
            "expectancy": float(expectancy),
            "total_pips": float(trades_df['pips'].sum()),
            "final_capital": float(self.current_capital),
            "return_pct": float((self.current_capital - self.initial_capital) / self.initial_capital * 100),
            "max_consecutive_losses": int(max_consecutive_losses),
            "session_performance": session_performance,
            "price_position_performance": price_position_performance
        }
