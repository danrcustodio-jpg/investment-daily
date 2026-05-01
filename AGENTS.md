# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Investment Daily is a single-service Python 3.12 application providing:
- **Flask Dashboard** (`dashboard.py`, port 5050) — primary web UI
- **Strategy Engine** (`strategy_engine.py`) — shared core library (30 detectors, backtesting)
- **Newsletter** (`investment_daily.py`) — daily market email
- **Alert System** (`alert_system.py`) — intraday strategy alerts
- **Portfolio Simulation** (`portfolio_sim.py`) — paper trading vs SPY

No database, no Docker, no monorepo. All data comes from live external APIs (Yahoo Finance, Schwab API, RSS feeds, Polymarket).

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

### Schwab API integration

`schwab_client.py` provides an optional supplemental data source via Schwab's Trader API. When configured, it provides batch quotes (for `get_market_data()`) and daily OHLCV price history (for `scan_ticker()`). All callers fall back to yfinance automatically when Schwab credentials are missing, the token has expired, or the symbol is unsupported (crypto, futures, forex, indices).

**Setup:** Requires `SCHWAB_API_KEY` and `SCHWAB_APP_SECRET` in `.env`, plus a token file created via `schwab-generate-token.py`. Tokens expire after 7 days and must be regenerated. See [schwab-py docs](https://schwab-py.readthedocs.io/en/latest/auth.html) for the OAuth flow. The app works fully without Schwab credentials — yfinance serves as the universal fallback.
