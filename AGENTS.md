# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Investment Daily is a single-service Python 3.12 application providing:
- **Flask Dashboard** (`dashboard.py`, port 5050) — primary web UI
- **Strategy Engine** (`strategy_engine.py`) — shared core library (30 detectors, backtesting)
- **Newsletter** (`investment_daily.py`) — daily market email
- **Alert System** (`alert_system.py`) — intraday strategy alerts
- **Portfolio Simulation** (`portfolio_sim.py`) — paper trading vs SPY

No database, no Docker, no monorepo. All data comes from live external APIs (Yahoo Finance, RSS feeds, Polymarket).

### Running services

- **Dashboard:** `python3 dashboard.py` — starts Flask on port 5050. The `logs/` directory must exist (`mkdir -p logs`).
- Email features require `EMAIL_SENDER` and `EMAIL_PASSWORD` in `.env`, but the dashboard, strategy scans, and tests all work without them.

### Lint / Test / Build

- **Lint:** `python3 -m ruff check .` (config in `pyproject.toml`). There are ~15 pre-existing lint warnings in test files, `live_scan.py`, and `tunnel.py` — these are known.
- **Tests (smoke, live data):**
  - `python3 tests/test_strategy.py` — strategy engine scan (~10s, fetches 2yr data)
  - `python3 tests/test_run.py` — full newsletter pipeline without email
  - `python3 tests/test_alerts.py` — alert logic without email or market-hours check
  - `python3 tests/qa_scenarios.py` — QA scenario suite
- Tests are script-based (not pytest). They fetch live market data and require internet access.
- There is no build step; the app runs directly from source.

### Gotchas

- The `logs/` directory is gitignored and must be created before importing `investment_daily.py` or `alert_system.py` (they set up `FileHandler` at module level). Run `mkdir -p logs` first.
- `ruff` is not in `requirements.txt` — install it separately (`pip install ruff`).
- The pre-commit hook script at `scripts/pre_commit_check.py` runs ruff and other checks. It is not auto-installed; see `.git/hooks/` if you want to enable it.
- Architecture and change recipes are documented in `docs/ARCHITECTURE.md` and `docs/AGENT_GUIDE.md`.
