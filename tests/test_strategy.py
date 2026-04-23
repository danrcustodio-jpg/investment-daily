"""Quick test of the strategy engine."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy_engine import run_full_scan

print("Running strategy scan (fetching 2 years of data per ticker) ...")
sigs = run_full_scan()
print(f"\nFound {len(sigs)} signals above confidence threshold:\n")

for s in sigs[:12]:
    bt   = s.get("backtest", {})
    d5   = bt.get("5d", {})
    wr   = d5.get("win_rate", 0) if d5 else 0
    ar   = d5.get("avg_return", 0) if d5 else 0
    conf = s.get("confidence", 0)
    dir_s = "BUY " if s["direction"] == "BULLISH" else "SELL"
    print(
        f"  {dir_s} | {s['ticker']:<10} | {s['strategy']:<30} "
        f"| conf={conf:4.0f} | {wr}% wins, {ar:+.1f}% avg (5d)"
    )

print("\nStrategy engine test passed.")
