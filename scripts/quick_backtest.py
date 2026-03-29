import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.backtester import Backtester
from app.strategies.ema_momentum import EMAMomentumStrategy
from app.strategies.vwap_enhanced import VWAPEnhancedStrategy


async def run_quick_backtest():
    """Run quick backtest with both strategies."""
    
    symbol = "XAU/USD"
    interval = "1h"
    months = 6
    
    print("=" * 80)
    print(f"GOLD QUANT BACKTEST - {months} Month Analysis")
    print("=" * 80)
    print(f"\nSymbol: {symbol}")
    print(f"Interval: {interval}")
    print(f"Period: {months} months")
    print(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    print("🔄 Running EMA Momentum Strategy...")
    ema_bt = Backtester(EMAMomentumStrategy, {'fast_period': 9, 'slow_period': 21})
    ema_result = await ema_bt.run_backtest(symbol, interval, months)
    ema_metrics = ema_result.get('metrics', {})
    
    print(f"✅ EMA Complete: {ema_metrics.get('total_trades', 0)} trades, "
          f"{ema_metrics.get('win_rate', 0):.1f}% WR, "
          f"{ema_metrics.get('profit_factor', 0):.2f} PF")
    
    print("\n🔄 Running VWAP Enhanced Strategy...")
    vwap_bt = Backtester(VWAPEnhancedStrategy, {'fast_period': 9, 'slow_period': 21})
    vwap_result = await vwap_bt.run_backtest(symbol, interval, months)
    vwap_metrics = vwap_result.get('metrics', {})
    
    print(f"✅ VWAP Complete: {vwap_metrics.get('total_trades', 0)} trades, "
          f"{vwap_metrics.get('win_rate', 0):.1f}% WR, "
          f"{vwap_metrics.get('profit_factor', 0):.2f} PF")
    
    print("\n" + "=" * 80)
    print("📊 COMPARISON REPORT")
    print("=" * 80)
    
    print(f"\n{'Metric':<25} {'EMA':<20} {'VWAP Enhanced':<20} {'Change':<15}")
    print("-" * 80)
    
    comparisons = [
        ("Total Trades", 'total_trades', ''),
        ("Win Rate", 'win_rate', '%'),
        ("Profit Factor", 'profit_factor', 'x'),
        ("Total Pips", 'total_pips', ' pips'),
        ("Avg Win", 'avg_win_pips', ' pips'),
        ("Avg Loss", 'avg_loss_pips', ' pips'),
        ("Max Drawdown", 'max_drawdown', '%'),
        ("Expectancy", 'expectancy', ' pips'),
        ("Max Consecutive Loss", 'max_consecutive_losses', ''),
        ("Return", 'return_pct', '%')
    ]
    
    for label, key, unit in comparisons:
        ema_val = ema_metrics.get(key, 0)
        vwap_val = vwap_metrics.get(key, 0)
        
        if ema_val != 0 and key not in ['max_drawdown', 'avg_loss_pips', 'max_consecutive_losses']:
            change = ((vwap_val - ema_val) / abs(ema_val) * 100)
            change_str = f"{change:+.1f}%"
        elif key in ['max_drawdown', 'max_consecutive_losses']:
            change = vwap_val - ema_val
            change_str = f"{change:+.1f}"
        else:
            change_str = "N/A"
        
        print(f"{label:<25} {ema_val:>8.2f}{unit:<11} {vwap_val:>8.2f}{unit:<11} {change_str:>15}")
    
    session_perf = vwap_metrics.get('session_performance', {})
    if session_perf:
        print(f"\n📅 SESSION PERFORMANCE (VWAP Enhanced)")
        print("-" * 80)
        print(f"{'Session':<15} {'Trades':<10} {'Wins':<10} {'Win Rate':<12} {'Avg Pips':<12}")
        print("-" * 80)
        for session in ['ASIAN', 'LONDON', 'NY', 'OTHER']:
            if session in session_perf:
                data = session_perf[session]
                print(f"{session:<15} {data['total_trades']:<10} {data['wins']:<10} "
                      f"{data['win_rate']:>8.1f}%{'':3} {data['avg_pips']:>8.1f}")
    
    position_perf = vwap_metrics.get('price_position_performance', {})
    if position_perf:
        print(f"\n💰 PRICE POSITION ANALYSIS (VWAP Enhanced)")
        print("-" * 80)
        print(f"{'Position':<15} {'Trades':<10} {'Wins':<10} {'Win Rate':<12}")
        print("-" * 80)
        for position in ['DISCOUNT', 'AT_VALUE', 'PREMIUM']:
            if position in position_perf:
                data = position_perf[position]
                print(f"{position:<15} {data['total_trades']:<10} {data['wins']:<10} "
                      f"{data['win_rate']:>8.1f}%")
    
    print(f"\n🎯 DEPLOYMENT READINESS ASSESSMENT")
    print("-" * 80)
    
    vwap_wr = vwap_metrics.get('win_rate', 0)
    vwap_pf = vwap_metrics.get('profit_factor', 0)
    vwap_dd = vwap_metrics.get('max_drawdown', 0)
    
    score = 0
    
    print(f"\n✓ Win Rate: {vwap_wr:.1f}%", end="")
    if vwap_wr >= 60:
        print(" (EXCELLENT)")
        score += 3
    elif vwap_wr >= 50:
        print(" (GOOD)")
        score += 2
    elif vwap_wr >= 40:
        print(" (ACCEPTABLE)")
        score += 1
    else:
        print(" (NEEDS IMPROVEMENT)")
    
    print(f"✓ Profit Factor: {vwap_pf:.2f}x", end="")
    if vwap_pf >= 2.0:
        print(" (EXCELLENT)")
        score += 3
    elif vwap_pf >= 1.5:
        print(" (GOOD)")
        score += 2
    elif vwap_pf >= 1.2:
        print(" (ACCEPTABLE)")
        score += 1
    else:
        print(" (NEEDS IMPROVEMENT)")
    
    print(f"✓ Max Drawdown: {vwap_dd:.1f}%", end="")
    if vwap_dd <= 10:
        print(" (EXCELLENT)")
        score += 3
    elif vwap_dd <= 20:
        print(" (GOOD)")
        score += 2
    elif vwap_dd <= 30:
        print(" (ACCEPTABLE)")
        score += 1
    else:
        print(" (HIGH RISK)")
    
    wr_improvement = vwap_wr - ema_metrics.get('win_rate', 0)
    print(f"✓ Win Rate Improvement: {wr_improvement:+.1f}%", end="")
    if wr_improvement >= 10:
        print(" (SIGNIFICANT)")
        score += 2
    elif wr_improvement >= 5:
        print(" (MODERATE)")
        score += 1
    elif wr_improvement >= 0:
        print(" (SLIGHT)")
    else:
        print(" (NEGATIVE - ISSUE)")
        score -= 2
    
    print(f"\n{'─' * 80}")
    print(f"OVERALL SCORE: {score}/11")
    
    if score >= 9:
        print("\n✅ RECOMMENDATION: READY FOR DEPLOYMENT")
        print("   - Strong performance across all metrics")
        print("   - VWAP filter provides significant improvement")
        print("   - Consider deploying with real-time monitoring")
    elif score >= 6:
        print("\n⚠️  RECOMMENDATION: DEPLOY WITH CAUTION")
        print("   - Adequate performance but room for improvement")
        print("   - Monitor closely during first week")
        print("   - Consider adding multi-timeframe confirmation")
    elif score >= 3:
        print("\n⚠️  RECOMMENDATION: FURTHER OPTIMIZATION NEEDED")
        print("   - Win rate below target")
        print("   - Add multi-timeframe confirmation")
        print("   - Add ranging market filter")
        print("   - Test for additional 1-2 weeks")
    else:
        print("\n❌ RECOMMENDATION: NOT READY FOR DEPLOYMENT")
        print("   - Performance below minimum viable")
        print("   - Requires significant strategy improvements")
        print("   - Consider alternative approaches")
    
    output_dir = Path(__file__).parent.parent / "backtest_results"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    report = {
        "timestamp": timestamp,
        "symbol": symbol,
        "interval": interval,
        "months": months,
        "ema_strategy": ema_metrics,
        "vwap_enhanced": vwap_metrics,
        "score": score,
        "recommendation": "DEPLOY" if score >= 9 else "CAUTION" if score >= 6 else "OPTIMIZE" if score >= 3 else "NOT_READY"
    }
    
    report_file = output_dir / f"backtest_report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Full report saved: {report_file}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_quick_backtest())
