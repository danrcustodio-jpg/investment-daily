#!/usr/bin/env python3
"""
Compare an eval snapshot to evals/gates.local.json.

Exit 0 = all gates pass. Exit 1 = one or more failures or missing files.

Usage:
  python scripts/check_eval_gates.py --snapshot evals/runs/run_20260424_153000.json
  python scripts/check_eval_gates.py --latest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _latest_snapshot_path(runs_dir: str) -> str | None:
    if not os.path.isdir(runs_dir):
        return None
    candidates = []
    for name in os.listdir(runs_dir):
        if not name.endswith(".json"):
            continue
        full = os.path.join(runs_dir, name)
        if os.path.isfile(full):
            candidates.append(full)
    if not candidates:
        return None
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]


def _check_gate(
    gates: dict,
    metrics: dict,
    key: str,
    min_key: str,
    label: str,
    failures: list[str],
) -> None:
    if min_key not in gates:
        return
    minimum = gates[min_key]
    actual = metrics.get(key)
    if actual is None:
        failures.append(f"{label}: snapshot missing metrics.{key}")
        return
    try:
        if float(actual) < float(minimum):
            failures.append(
                f"{label}: metrics.{key}={actual} is below gate {min_key}={minimum}"
            )
    except (TypeError, ValueError):
        failures.append(f"{label}: cannot compare metrics.{key}={actual!r} to {minimum!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check eval snapshot against local gates.")
    parser.add_argument(
        "--gates",
        default=os.path.join(SCRIPT_DIR, "evals", "gates.local.json"),
        help="Path to gates JSON (default: evals/gates.local.json).",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--snapshot",
        help="Path to a single eval snapshot JSON.",
    )
    group.add_argument(
        "--latest",
        action="store_true",
        help="Use the newest file in evals/runs/ by modification time.",
    )
    args = parser.parse_args()

    gates_path = os.path.normpath(
        args.gates if os.path.isabs(args.gates) else os.path.join(SCRIPT_DIR, args.gates)
    )
    if not os.path.isfile(gates_path):
        print(f"ERROR: gates file not found: {gates_path}", file=sys.stderr)
        return 1

    if args.latest:
        runs_dir = os.path.join(SCRIPT_DIR, "evals", "runs")
        snap_path = _latest_snapshot_path(runs_dir)
        if not snap_path:
            print(f"ERROR: no snapshot JSON files in {runs_dir}", file=sys.stderr)
            return 1
    else:
        snap_path = os.path.normpath(
            args.snapshot
            if os.path.isabs(args.snapshot)
            else os.path.join(SCRIPT_DIR, args.snapshot)
        )
        if not os.path.isfile(snap_path):
            print(f"ERROR: snapshot not found: {snap_path}", file=sys.stderr)
            return 1

    gates = _load_json(gates_path)
    snapshot = _load_json(snap_path)
    metrics = snapshot.get("metrics")
    if not isinstance(metrics, dict):
        print("ERROR: snapshot has no metrics object", file=sys.stderr)
        return 1

    failures: list[str] = []

    _check_gate(gates, metrics, "total_signals", "min_total_signals", "total_signals", failures)
    _check_gate(gates, metrics, "avg_confidence", "min_avg_confidence", "avg_confidence", failures)
    _check_gate(
        gates,
        metrics,
        "new_alert_candidates",
        "min_new_alert_candidates",
        "new_alert_candidates",
        failures,
    )

    print(f"Gates:    {gates_path}")
    print(f"Snapshot: {snap_path}")
    for k in ("total_signals", "avg_confidence", "new_alert_candidates"):
        if k in metrics:
            print(f"  metrics.{k} = {metrics[k]}")

    if failures:
        print("\nGATE FAILURES:", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        return 1

    print("\nAll configured gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
