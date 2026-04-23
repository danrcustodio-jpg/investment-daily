"""Test alert logic against live signals — no email sent, no market hours check."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy_engine import run_full_scan
from alert_system import (
    build_alert_email, load_state, make_state_key, already_fired_recently,
)

print("Running full strategy scan...")
signals = run_full_scan()
print(f"Total signals: {len(signals)}\n")

state    = load_state()
new_sigs = [s for s in signals if not already_fired_recently(state, make_state_key(s))]
fired    = [s for s in signals if already_fired_recently(state, make_state_key(s))]

print(f"New (not in cooldown): {len(new_sigs)}")
print(f"Suppressed (cooldown): {len(fired)}")

if new_sigs:
    print("\nNew signals:")
    for s in new_sigs:
        arrow = "^" if s["direction"] == "BULLISH" else "v"
        print(f"  {arrow} {s['ticker']:<10} {s['strategy']:<30} conf={s['confidence']:.0f}")

    subject, html = build_alert_email(new_sigs, signals, dispatch_seq=0)
    safe_subject  = subject.encode("ascii", errors="replace").decode("ascii")
    print(f"\nEmail subject would be: {safe_subject}")
    print(f"HTML size: {len(html):,} chars")
else:
    print("\nNo new signals outside cooldown.")
    if signals:
        top     = signals[0]
        subject, html = build_alert_email([top], signals, dispatch_seq=0)
        safe_subject  = subject.encode("ascii", errors="replace").decode("ascii")
        print(f"[Simulated with top signal] Subject: {safe_subject}")
        print(f"HTML size: {len(html):,} chars")

print("\nAlert logic test passed.")
