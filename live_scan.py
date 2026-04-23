import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from strategy_engine import run_full_scan

signals = run_full_scan()
print(f"Total signals: {len(signals)}")
print()
for s in signals:
    bt = s.get("backtest", {})
    d5 = bt.get("5d", {})
    wr   = d5.get("win_rate", "?")
    sh   = d5.get("sharpe", "?")
    pf   = d5.get("profit_factor", "?")
    dd   = d5.get("max_drawdown", "?")
    avg  = d5.get("avg_return", "?")
    line = (
        f"{s['direction']:<8} {s['ticker']:<10} {s['strategy']:<35} "
        f"conf={s['confidence']:>5} | wr={wr}% | avg={avg}% | sharpe={sh} | pf={pf} | maxdd={dd}%"
    )
    print(line)
