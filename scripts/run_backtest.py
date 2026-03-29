import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.backtester import Backtester
from app.strategies.ema_momentum import EMAMomentumStrategy
from app.strategies.vwap_enhanced import VWAPEnhancedStrategy


async def run_comparison_backtest():
    """Run backtest comparing EMA vs VWAP Enhanced strategies."""
    
    print("=" * 80)
    print("GOLD QUANT BACKTEST - Strategy Comparison")
    print("=" * 80)
    print()
    
    symbol = "XAU/USD"
    interval = "1h"
    months = 6
    
    print(f"Symbol: {symbol}")
    print(f"Interval: {interval}")
    print(f"Period: {months} months")
    print(f"Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    print("-" * 80)
    
    print("\n🔄 Running EMA Momentum Strategy...")
    ema_backtester = Backtester(
        strategy_class=EMAMomentumStrategy,
        strategy_params={'fast_period': 9, 'slow_period': 21}
    )
    
    ema_results = await ema_backtester.run_backtest(
        symbol=symbol,
        interval=interval,
        months=months
    )
    
    print("\n✅ EMA Strategy Complete")
    
    print("\n" + "=" * 80)
    print("\n🔄 Running VWAP Enhanced Strategy...")
    
    vwap_backtester = Backtester(
        strategy_class=VWAPEnhancedStrategy,
        strategy_params={'fast_period': 9, 'slow_period': 21}
    )
    
    vwap_results = await vwap_backtester.run_backtest(
        symbol=symbol,
        interval=interval,
        months=months
    )
    
    print("\n✅ VWAP Enhanced Strategy Complete")
    
    print("\n" + "=" * 80)
    print("\n📊 BACKTEST RESULTS COMPARISON")
    print("=" * 80)
    
    print_comparison_report(ema_results, vwap_results)
    
    save_results(ema_results, vwap_results)
    
    print("\n" + "=" * 80)
    print("✅ Backtest complete! Results saved to backtest_results/")
    print("=" * 80)


def print_comparison_report(ema_results: dict, vwap_results: dict):
    """Print formatted comparison report."""
    
    if not ema_results or not vwap_results:
        print("❌ No results to compare")
        return
    
    ema_metrics = ema_results.get('metrics', {})
    vwap_metrics = vwap_results.get('metrics', {})
    
    print("\n📈 PERFORMANCE METRICS")
    print("-" * 80)
    print(f"{'Metric':<30} {'EMA Strategy':<20} {'VWAP Enhanced':<20} {'Improvement':<15}")
    print("-" * 80)
    
    metrics_to_compare = [
        ('Total Trades', 'total_trades', ''),
        ('Win Rate', 'win_rate', '%'),
        ('Profit Factor', 'profit_factor', 'x'),
        ('Total Pips', 'total_pips', ' pips'),
        ('Avg Win', 'avg_win_pips', ' pips'),
        ('Avg Loss', 'avg_loss_pips', ' pips'),
        ('Max Drawdown', 'max_drawdown', '%'),
        ('Sharpe Ratio', 'sharpe_ratio', ''),
        ('Expectancy', 'expectancy', ' pips'),
        ('Max Consecutive Losses', 'max_consecutive_losses', ''),
        ('Return', 'return_pct', '%')
    ]
    
    for label, key, unit in metrics_to_compare:
        ema_val = ema_metrics.get(key, 0)
        vwap_val = vwap_metrics.get(key, 0)
        
        if ema_val != 0:
            improvement = ((vwap_val - ema_val) / abs(ema_val) * 100)
            improvement_str = f"{improvement:+.1f}%"
        else:
            improvement_str = "N/A"
        
        print(f"{label:<30} {ema_val:>10.2f}{unit:<9} {vwap_val:>10.2f}{unit:<9} {improvement_str:>15}")
    
    print("\n📅 SESSION PERFORMANCE (VWAP Enhanced)")
    print("-" * 80)
    
    session_perf = vwap_metrics.get('session_performance', {})
    if session_perf:
        print(f"{'Session':<15} {'Total Trades':<15} {'Win Rate':<15} {'Avg Pips':<15}")
        print("-" * 80)
        for session, data in session_perf.items():
            print(f"{session:<15} {data['total_trades']:<15} {data['win_rate']:>10.1f}%{'':<4} {data['avg_pips']:>10.1f}")
    
    print("\n💰 PRICE POSITION ANALYSIS (VWAP Enhanced)")
    print("-" * 80)
    
    position_perf = vwap_metrics.get('price_position_performance', {})
    if position_perf:
        print(f"{'Position':<15} {'Total Trades':<15} {'Wins':<15} {'Win Rate':<15}")
        print("-" * 80)
        for position, data in position_perf.items():
            print(f"{position:<15} {data['total_trades']:<15} {data['wins']:<15} {data['win_rate']:>10.1f}%")
    
    print("\n🎯 KEY FINDINGS")
    print("-" * 80)
    
    win_rate_improvement = vwap_metrics.get('win_rate', 0) - ema_metrics.get('win_rate', 0)
    profit_factor_improvement = vwap_metrics.get('profit_factor', 0) - ema_metrics.get('profit_factor', 0)
    
    if win_rate_improvement > 5:
        print(f"✅ VWAP filter improved win rate by {win_rate_improvement:.1f}%")
    elif win_rate_improvement < -5:
        print(f"⚠️  VWAP filter reduced win rate by {abs(win_rate_improvement):.1f}%")
    else:
        print(f"➡️  VWAP filter had minimal impact on win rate ({win_rate_improvement:+.1f}%)")
    
    if profit_factor_improvement > 0.2:
        print(f"✅ VWAP filter improved profit factor by {profit_factor_improvement:.2f}x")
    elif profit_factor_improvement < -0.2:
        print(f"⚠️  VWAP filter reduced profit factor by {abs(profit_factor_improvement):.2f}x")
    
    if vwap_metrics.get('win_rate', 0) >= 60:
        print("✅ VWAP Enhanced strategy achieves target win rate (60%+)")
        print("✅ READY FOR DEPLOYMENT")
    elif vwap_metrics.get('win_rate', 0) >= 50:
        print("⚠️  VWAP Enhanced strategy shows promise (50-60% win rate)")
        print("⚠️  Consider additional filters before deployment")
    else:
        print("❌ VWAP Enhanced strategy below target (<50% win rate)")
        print("❌ Requires further optimization before deployment")
    
    if position_perf:
        discount_wr = position_perf.get('DISCOUNT', {}).get('win_rate', 0)
        premium_wr = position_perf.get('PREMIUM', {}).get('win_rate', 0)
        
        if discount_wr > 60:
            print(f"✅ Buying at discount (below VWAP) shows strong performance ({discount_wr:.1f}% WR)")
        if premium_wr > 60:
            print(f"✅ Selling at premium (above VWAP) shows strong performance ({premium_wr:.1f}% WR)")
    
    best_session = None
    best_wr = 0
    for session, data in session_perf.items():
        if data['win_rate'] > best_wr and data['total_trades'] >= 5:
            best_wr = data['win_rate']
            best_session = session
    
    if best_session:
        print(f"✅ Best performance during {best_session} session ({best_wr:.1f}% WR)")


def save_results(ema_results: dict, vwap_results: dict):
    """Save backtest results to JSON files."""
    
    output_dir = Path(__file__).parent.parent / "backtest_results"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    ema_file = output_dir / f"ema_strategy_{timestamp}.json"
    with open(ema_file, 'w') as f:
        json.dump(ema_results, f, indent=2, default=str)
    
    vwap_file = output_dir / f"vwap_enhanced_{timestamp}.json"
    with open(vwap_file, 'w') as f:
        json.dump(vwap_results, f, indent=2, default=str)
    
    comparison = {
        "timestamp": timestamp,
        "ema_strategy": ema_results.get('metrics', {}),
        "vwap_enhanced": vwap_results.get('metrics', {}),
        "improvement": {
            "win_rate": vwap_results.get('metrics', {}).get('win_rate', 0) - ema_results.get('metrics', {}).get('win_rate', 0),
            "profit_factor": vwap_results.get('metrics', {}).get('profit_factor', 0) - ema_results.get('metrics', {}).get('profit_factor', 0),
            "total_pips": vwap_results.get('metrics', {}).get('total_pips', 0) - ema_results.get('metrics', {}).get('total_pips', 0)
        }
    }
    
    comparison_file = output_dir / f"comparison_{timestamp}.json"
    with open(comparison_file, 'w') as f:
        json.dump(comparison, f, indent=2, default=str)
    
    print(f"\n💾 Results saved:")
    print(f"   - {ema_file}")
    print(f"   - {vwap_file}")
    print(f"   - {comparison_file}")


if __name__ == "__main__":
    asyncio.run(run_comparison_backtest())
