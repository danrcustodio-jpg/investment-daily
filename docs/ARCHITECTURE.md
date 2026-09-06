# Architecture — Investment Daily

## System Overview

Three independent runtimes + one shared library:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Windows Task Scheduler                       │
│                                                                  │
│  [7:30 AM daily]          [Every 30 min, market hours]          │
│  investment_daily.py       alert_system.py                       │
│        │                         │                               │
│        └────────┬────────────────┘                               │
│                 ▼                                                 │
│          strategy_engine.py   ◄── shared core library            │
│                 │                                                 │
│                 ▼                                                 │
│           yfinance API  (optional: Schwab daily OHLCV when enabled)   │
│           pandas-ta                                               │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│            Manual start: dashboard.py      │
│            Flask on port 5050             │
│                    │                       │
│     reads from  strategy_engine.py         │
│     reads from  investment_daily.py        │
│     triggers    investment_daily.py        │
│     triggers    alert_system.py            │
└───────────────────────────────────────────┘
```

---

## Data Flow

### Daily Newsletter (`investment_daily.py → main()`)

```
1. get_market_data()        → yfinance: 100+ tickers across 5 categories
2. get_news_feeds()         → feedparser: 9 RSS feeds, max 40 articles
3. get_polymarket_data()    → requests: Gamma API, filter by FINANCE_KEYWORDS
4. analyze_sentiment()      → keyword scoring against market returns
5. strategy_engine.run_full_scan()  → 28 tickers × 30 strategy detectors
6. build_email()            → combine all into HTML
7. send_email()             → Gmail SMTP, port 587, STARTTLS
```

### Intraday Alerts (`alert_system.py → main()`)

```
1. is_market_open()         → check NYSE hours (ET timezone, Mon-Fri)
2. load_state()             → read alert_state.json (12h cooldown per ticker+strategy)
3. strategy_engine.run_full_scan()  → same scan as newsletter
4. filter signals           → confidence >= MIN_CONFIDENCE (52.0)
5. filter already-sent      → skip if strategy+ticker emailed within last 12 hours
6. build_alert_email()      → HTML with signal cards (includes monotonic dispatch # in subject/body)
7. send_email()             → Gmail SMTP
8. save_state()             → write alert_state.json
```

### Federal Contract Alerts (`contract_alerts.py → main()`)

```
1. resolve_watchlist()       → contract_watchlist.WATCHLIST ∪ SCAN_TICKERS (~60 tickers)
2. load_state() + prune_state()  → contract_state.json (90d retention)
3. for ticker in resolved:
     fetch_contracts_for_ticker()  → POST api.usaspending.gov/api/v2/search/spending_by_award/
                                      (recipient_search_text=patterns, type A/B/C/D,
                                       amount >= MIN_AMOUNT, last N days)
     filter_new_awards()    → drop already-seen generated_internal_id
                              + defensive re-match against resolved patterns
4. if new awards:
     build_contract_email() → HTML, one section per ticker, one card per contract
     send_email()           → reuses alert_system.send_email (Gmail SMTP)
     save_state()           → persist new generated_internal_id values
```

Runs daily at 7:30 AM ET on weekdays via [.github/workflows/contracts.yml](../.github/workflows/contracts.yml). Lookback is 7 days by default so awards reported late on Fri/Sat/Sun (USAspending has a 1-3 day reporting lag) are still caught Monday.

### Alert Deduplication (`alert_state.json`)

```json
{
  "send_count": 47,
  "fired": {
    "NVDA::RSI Oversold": "2026-04-22T14:30:00-06:00",
    "TSLA::MACD Bullish Crossover": "2026-04-22T10:00:00-06:00"
  }
}
```
Key format: `"TICKER::Strategy Name"` with ISO timestamp of last email. The same key will not trigger another email until **12 hours** have passed (`ALERT_COOLDOWN_HOURS` in `alert_system.py`).
State file is at `C:\Users\Owner\InvestmentDaily\alert_state.json`.

---

## Module Reference

### `strategy_engine.py`

The core library. All other files import from here.

**Public API:**

| Function / Constant | Description |
|---|---|
| `run_full_scan(tickers=None)` | Scan all tickers, return signals sorted by confidence (≥45) |
| `scan_ticker(symbol, name)` | Single ticker: fetch data, compute indicators, run all 9 detectors |
| `backtest_signal(closes, signal_mask, forward_days)` | Compute Sharpe, Sortino, win rate, profit factor, max drawdown |
| `confidence_score(bt)` | 0–100 composite score from backtest results |
| `format_backtest_summary(bt)` | Human-readable one-line backtest string |
| `strategy_learn_link(strategy_name, style)` | HTML link to Investopedia for a strategy |
| `SCAN_TICKERS` | Dict of `{ticker: company_name}` — 28 tickers |
| `STRATEGY_LINKS` | Dict mapping strategy names to Investopedia URLs |

**Signal object shape** (returned by all `detect_*` functions):

```python
{
    "strategy":    "RSI Oversold",           # strategy name
    "direction":   "BULLISH",                # or "BEARISH"
    "ticker":      "NVDA",                   # Yahoo Finance symbol
    "name":        "NVIDIA",                 # human name
    "indicator":   "RSI = 29.3  (oversold)", # one-line indicator summary
    "detail":      "RSI dropped to...",      # paragraph explanation
    "implication": "Historical mean-reversion...",  # what to do
    "backtest": {
        "count": 23,
        "5d": {
            "win_rate": 65.2,
            "avg_return": 2.1,
            "std_return": 3.4,
            "sharpe": 1.43,
            "sortino": 1.87,
            "profit_factor": 2.1,
            "max_drawdown": -8.3,
            "count": 21
        },
        "20d": { ... same shape ... }
    },
    "confidence": 71.5       # 0-100 composite score
}
```

**Indicator column names** (from `pandas-ta`, used in detector functions):

| Indicator | Column Name | Threshold Used |
|---|---|---|
| RSI | `RSI_14` | < 32 oversold, > 68 overbought |
| Stochastic RSI | `STOCHRSIk_14_14_3_3` | < 20 oversold, > 80 overbought |
| MACD | `MACD_12_26_9`, `MACDs_12_26_9` | crossover |
| SMA 50 | `SMA_50` | Golden/Death Cross vs SMA_200 |
| SMA 200 | `SMA_200` | Golden/Death Cross vs SMA_50 |
| Bollinger Bands | `BBL_20_2.0`, `BBU_20_2.0` | price touches band |
| ADX | `ADX_14`, `DMP_14`, `DMN_14` | ADX > 25 = strong trend |

**9 Strategies (detector functions):**

| Function | Strategy Name | Signal Type |
|---|---|---|
| `detect_rsi()` | RSI Oversold / RSI Overbought | Momentum reversal |
| `detect_stoch_rsi()` | Stochastic RSI Oversold / Overbought | Fast momentum |
| `detect_macd()` | MACD Bullish/Bearish Crossover | Trend change |
| `detect_ma_cross()` | Golden Cross / Death Cross | Long-term trend |
| `detect_bollinger()` | Bollinger Lower/Upper Band Touch | Mean reversion |
| `detect_adx()` | ADX Strong Trend — Bullish/Bearish | Trend strength filter |
| `detect_vwap()` | VWAP Deviation Oversold/Overbought | Institutional anchor |
| `detect_breakout()` | 52-Week Breakout | Momentum breakout |
| `detect_volume_spike()` | Volume Spike + Surge/Drop | Unusual activity |

---

### `investment_daily.py`

**Key functions:**

| Function | What it does |
|---|---|
| `get_market_data()` | Returns dict of category → list of `{ticker, name, price, change_pct, ...}` |
| `get_news_feeds()` | Returns list of `{title, link, published, source, summary}` |
| `get_polymarket_data()` | Returns list of `{title, probability, volume, url}` filtered by finance keywords |
| `analyze_sentiment(news, market)` | Returns `{score, label, emoji}` — overall market sentiment |
| `fact_check_news(items, market_data)` | Cross-references news claims against actual price moves |
| `build_news_html(items)` | Returns HTML string for news section with "Read Full Article" buttons |
| `build_strategy_section(signals)` | Returns HTML table of strategy signals |
| `build_email(market, news, polymarket, signals)` | Returns full HTML email body |
| `send_email(subject, html_body)` | Gmail SMTP send |
| `main()` | Orchestrates all of the above |

**`MARKET_TICKERS` structure** (in `investment_daily.py`):

```python
{
    "Major Indices": { "^GSPC": "S&P 500", "^IXIC": "NASDAQ", ... },
    "Sector ETFs":   { "XLK": "Tech (XLK)", ... },
    "Commodities":   { "GC=F": "Gold", "CL=F": "Crude Oil", ... },
    "Crypto":        { "BTC-USD": "Bitcoin", ... },
    "Bonds & Rates": { "^TNX": "10-Yr Treasury", ... },
    "Hot Stocks":    { "NVDA": "NVIDIA", "TSLA": "Tesla", ... }
}
```

**`RSS_FEEDS` list** (9 feeds):
Reuters Business, CNBC Markets, MarketWatch, Yahoo Finance, Seeking Alpha, Investing.com, Barron's, Financial Times, WSJ Markets.

---

### `alert_system.py`

**Key functions:**

| Function | What it does |
|---|---|
| `is_market_open()` | Returns bool — NYSE hours, ET timezone |
| `load_state()` | Reads `alert_state.json`, returns `{ "fired": { key: iso_timestamp, ... } }` |
| `save_state(state)` | Writes `alert_state.json` |
| `make_state_key(signal)` | Returns `"TICKER::Strategy Name"` |
| `build_signal_card(signal)` | Returns HTML card for one signal |
| `build_alert_email(new, all, dispatch_seq=…)` | Returns `(subject, html)`; `dispatch_seq` labels each send |
| `main()` | Full orchestration: scan → filter → deduplicate → email → save state |

**`MIN_CONFIDENCE`** — from env `ALERT_MIN_CONFIDENCE` (default 50): only send alerts for signals at or above this score.

**Progressive intraday tracking** — tickers with any **active** signal at or above **`ALERT_HIGH_CONFIDENCE_15M`** (default 68) reset to 15m tracking, then decay when confidence cools: 30m → 60m → 120m → 240m → Daily. Alert emails include due 15m context blocks from this tracker (Schwab 15m when enabled, else yfinance).

---

### `contract_alerts.py` + `contract_watchlist.py`

Daily federal-contract scanner. Polls [USAspending.gov](https://www.usaspending.gov) for newly-awarded contracts to publicly-traded companies on the watchlist and emails a roundup.

**Key functions in `contract_alerts.py`:**

| Function | What it does |
|---|---|
| `fetch_contracts_for_ticker(ticker, patterns, ...)` | POST to `spending_by_award/` for one ticker; filters by type A/B/C/D, time period, amount, recipient text |
| `filter_new_awards(rows, state, resolved, ...)` | Drop already-seen `generated_internal_id`s and rows whose recipient doesn't actually map back to a watched ticker |
| `normalize_award(raw, ticker)` | Flatten raw API row into stable email-renderable dict |
| `load_state` / `save_state` / `prune_state` | Read/write `contract_state.json`; prune entries older than 90 days |
| `build_contract_card(award)` | HTML card for one contract: recipient, amount, agency, description, NAICS, view button |
| `build_contract_email(by_ticker, ...)` | Returns `(subject, html)` — subject includes top tickers + total $ for inbox preview |
| `scan(...)` | Full orchestration: resolve watchlist → loop tickers → load/update state → return new-awards dict |
| `main()` | CLI entrypoint; sends email via `alert_system.send_email` (Gmail SMTP) |

**`contract_watchlist.py`:**

| Symbol | Purpose |
|---|---|
| `WATCHLIST` | Curated `{ticker: [recipient_name_pattern, ...]}` dict for ~50 known federal contractors. Patterns are lowercase substrings of the USAspending Recipient Name field. |
| `resolve_watchlist()` | Returns the effective watchlist: `WATCHLIST ∪ SCAN_TICKERS` (fallback uses company name from `SCAN_TICKERS`). Crypto, futures, and broad-market ETFs are excluded. |
| `match_ticker(recipient_name, resolved)` | Reverse lookup: returns the ticker whose patterns best match a given recipient name, or `None`. Longest match wins on ambiguity. |

**Config (env vars):**

| Var | Default | Notes |
|---|---|---|
| `CONTRACT_MIN_AMOUNT` | `1000000` | Minimum award amount in USD. Smaller contracts ($5k purchase orders) are noise. |
| `CONTRACT_LOOKBACK_DAYS` | `7` | Days back from "today" to query. 7 covers weekend reporting lag. |
| `EMAIL_SENDER` / `EMAIL_PASSWORD` / `EMAIL_RECIPIENTS` | (shared) | Same Gmail App Password setup as the other entry points. |

**CLI flags:**

```bash
python contract_alerts.py --dry-run                    # parse + log, no email, no state write
python contract_alerts.py --ticker LMT                 # one ticker only (for testing)
python contract_alerts.py --days 30 --min-amount 5000000
```

**Dedup key** is `generated_internal_id` from the API (stable per award; modifications won't re-fire). State file is `contract_state.json`, tracked by git.

**Award types filtered** are USAspending codes A (BPA Call), B (Purchase Order), C (Delivery Order), D (Definitive Contract). Grants and loans are intentionally excluded.

---

### `dashboard.py`

**Flask routes:**

| Route | Method | Description |
|---|---|---|
| `/` | GET | Home: sentiment, top 5 signals, market overview |
| `/signals` | GET | Full signal list with backtest metrics |
| `/market` | GET | Full market snapshot by category |
| `/logs` | GET | Last 100 lines from both log files |
| `/run/newsletter` | POST | Trigger `python investment_daily.py` |
| `/run/alerts` | POST | Trigger `python alert_system.py` |
| `/refresh` | POST | Force-refresh in-memory cache |
| `/api/status` | GET | JSON: `{ok, signals_count, cache_age, loading}` |

**In-memory cache** (`_cache` dict):
- Refreshes every 30 minutes via background thread
- Keys: `market`, `signals`, `sentiment`, `fetched_at`, `loading`
- Populated by calling `investment_daily.get_market_data()` and `strategy_engine.run_full_scan()`

---

## Scheduling (Windows Task Scheduler)

```
Task Name: InvestmentDailyNewsletter
  Trigger: Daily at 7:30 AM
  Action:  python C:\Users\Owner\InvestmentDaily\investment_daily.py
  Registered by: schedule_daily.ps1

Task Name: InvestmentDailyAlerts
  Trigger: Every 30 minutes, starting 9:30 AM
  Action:  python C:\Users\Owner\InvestmentDaily\alert_system.py
  Registered by: schedule_alerts.ps1
  Note: alert_system.py self-guards via is_market_open() — does nothing outside NYSE hours
```

Contract alerts run on GitHub Actions only (no Windows Task Scheduler counterpart),
since they don't need market-hours timing:

```
GitHub Actions: .github/workflows/contracts.yml
  Trigger: cron '30 12 * * 1-5' (~7:30 AM ET weekdays)
  Action:  python contract_alerts.py
  Commits contract_state.json back to repo so dedup persists between runs.
```

---

## Local Release Gate Flow

Use one command to run the full local validation cycle before changing schedules or thresholds:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_full_cycle.ps1
```

This performs:
1. smoke tests (`tests/test_strategy.py`, `tests/test_run.py`, `tests/test_alerts.py`)
2. QA scenarios (`tests/qa_scenarios.py`)
3. report refresh (`generate_reports.py --alerts` and `--newsletter`)
4. eval snapshot write (`evals/runs/run_*.json`)
5. gate check (`scripts/check_eval_gates.py`) — compares snapshot metrics to `evals/gates.local.json`; exits non-zero on failure (CI-friendly)

`evals/gates.local.json` stores baseline thresholds for quick pass/fail checks. Use `-SkipGateCheck` on `run_full_cycle.ps1` when you intentionally skip thresholds (for example an empty `evals/runs/` on a fresh machine).

---

## Email Setup

- **Protocol:** Gmail SMTP, port 587, STARTTLS
- **Auth:** Gmail App Password (16 chars, no spaces in env var)
- **From:** `EMAIL_SENDER` env var
- **To:** `dan.r.custodio@gmail.com` (hardcoded in both scripts)
- **Format:** `MIMEMultipart("alternative")`, UTF-8, HTML part only (no plain-text fallback)

---

## Tunneling (Dashboard Access from Phone)

Two options, both work:

**Option 1: ngrok (if installed and in PATH)**
```powershell
# In one window
python dashboard.py

# In another window
ngrok http 5050
# Copy the https://xxxx.ngrok-free.app URL, open on phone
```

**Option 2: localhost.run (no install required)**
```powershell
# In one window
python dashboard.py

# In another window
ssh -R "80:localhost:5050" nokey@localhost.run
# Copy the https://xxxx.lhr.life URL, open on phone
```

**Option 3: Same WiFi only**
```
http://192.168.4.43:5050
```

---

## Important Notes for AI Agents

1. **`SCRIPT_DIR`** — Every file uses `os.path.dirname(os.path.abspath(__file__))` as its base. All log/state files use absolute paths from `SCRIPT_DIR`. Do not use relative paths.

2. **Windows Store Python** — This installation has a sandbox that prevents `subprocess.Popen` from launching external executables (like `ngrok.exe`) downloaded to the project folder. Use `ssh` (built into Windows) or `pyngrok` for tunneling.

3. **`pandas-ta` column names** — Always include the full parameter string: `RSI_14` not `RSI`, `MACD_12_26_9` not `MACD`. Check the column exists with `if col not in df.columns` before accessing.

4. **Confidence score range** — `confidence_score()` returns 0–100. Newsletter shows signals ≥ 45. Alert system sends emails for signals ≥ 52. These are in `run_full_scan()` and `alert_system.MIN_CONFIDENCE` respectively.

5. **Signal keys match `STRATEGY_LINKS`** — If you add a new strategy, add its name to both `STRATEGY_LINKS` and ensure the `_make_signal()` call uses the exact same string.

6. **Creator knowledge bases** (e.g. `docs/creators/nicholas-crown/`) are **notes**, not scan inputs. Do not copy gated newsletter setups into `strategy_engine.py`.
