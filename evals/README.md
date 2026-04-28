# Evals

Use this folder to make signal quality checks repeatable before release.

## Files

- `gates.local.json` - local release gates (minimum thresholds)
- `runs/*.json` - timestamped eval snapshots from `scripts/write_eval_snapshot.py`

## Run a local eval

```powershell
cd "C:\Users\Owner\InvestmentDaily"
python scripts/write_eval_snapshot.py
```

Or run the full local gate cycle:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_full_cycle.ps1
```

## Compare two runs quickly

1. Open both `evals/runs/*.json` files.
2. Compare `metrics.total_signals`, `metrics.avg_confidence`, and `metrics.new_alert_candidates`.
3. Review `top_signals` for strategy or ticker drift.

## Suggested release gate policy

Treat a run as "release-ready" when:

- `total_signals >= min_total_signals`
- `avg_confidence >= min_avg_confidence`
- `new_alert_candidates >= min_new_alert_candidates`
- no smoke/QA step failed in `scripts/run_full_cycle.ps1`

If `min_new_alert_candidates` is too noisy (cooldown can drive this to 0), set it to `0` in `gates.local.json`.

## Gate check (CI / local)

After a snapshot exists, compare it to thresholds:

```powershell
python scripts/check_eval_gates.py --snapshot evals/runs/run_20260424_153000.json
```

Use the newest snapshot in `evals/runs/`:

```powershell
python scripts/check_eval_gates.py --latest
```

`scripts/run_full_cycle.ps1` runs the gate check automatically after writing a snapshot, or against `--latest` if you used `-SkipEvalSnapshot`. Use `-SkipGateCheck` to skip (for example when `evals/runs/` is still empty on a fresh clone).
