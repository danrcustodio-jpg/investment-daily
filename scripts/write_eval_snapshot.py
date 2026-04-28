#!/usr/bin/env python3
"""
Write a lightweight eval snapshot for Investment Daily.

Creates: evals/runs/<label>.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from alert_system import already_fired_recently, load_state, make_state_key  # noqa: E402
from strategy_engine import run_full_scan  # noqa: E402


def build_snapshot() -> dict:
    signals = run_full_scan()
    state = load_state()

    new_signals = [s for s in signals if not already_fired_recently(state, make_state_key(s))]
    suppressed = [s for s in signals if already_fired_recently(state, make_state_key(s))]

    bullish = [s for s in signals if s.get("direction") == "BULLISH"]
    bearish = [s for s in signals if s.get("direction") == "BEARISH"]
    avg_conf = round(sum(s.get("confidence", 0) for s in signals) / len(signals), 2) if signals else 0.0

    top = []
    for s in signals[:10]:
        top.append(
            {
                "ticker": s.get("ticker"),
                "strategy": s.get("strategy"),
                "direction": s.get("direction"),
                "confidence": s.get("confidence"),
                "win_rate_5d": s.get("backtest", {}).get("5d", {}).get("win_rate"),
            }
        )

    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "metrics": {
            "total_signals": len(signals),
            "bullish_signals": len(bullish),
            "bearish_signals": len(bearish),
            "new_alert_candidates": len(new_signals),
            "suppressed_by_cooldown": len(suppressed),
            "avg_confidence": avg_conf,
        },
        "top_signals": top,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--label",
        default=datetime.now().strftime("run_%Y%m%d_%H%M%S"),
        help="Output label (without .json), defaults to timestamp.",
    )
    args = parser.parse_args()

    snapshot = build_snapshot()

    out_dir = os.path.join(SCRIPT_DIR, "evals", "runs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{args.label}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Wrote eval snapshot: {out_path}")
    print(f"Signals: {snapshot['metrics']['total_signals']}  Avg confidence: {snapshot['metrics']['avg_confidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
