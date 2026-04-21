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
│           yfinance API                                            │
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
5. strategy_engine.run_full_scan()  → 28 tickers × 9 strategies
6. build_email()            → combine all into HTML
7. send_email()             → Gmail SMTP, port 587, STARTTLS
```

### Intraday Alerts (`alert_system.py → main()`)

```
1. is_market_open()         → check NYSE hours (ET timezone, Mon-Fri)
2. load_state()             → read alert_state.json (deduplicate today's alerts)
3. strategy_engine.run_full_scan()  → same scan as newsletter
4. filter signals           → confidence >= MIN_CONFIDENCE (52.0)
5. filter already-sent      → skip if strategy+ticker already fired today
6. build_alert_email()      → HTML with signal cards
7. send_email()             → Gmail SMTP
8. save_state()             → write alert_state.json
```

### Alert Deduplication (`alert_state.json`)

```json
{
  "2024-01-15": {
    "NVDA|RSI Oversold": true,
    "TSLA|MACD Bullish Crossover": true
  }
}
```
Key format: `"TICKER|Strategy Name"` under today's date string (`YYYY-MM-DD`).  
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
| `load_state()` | Reads `alert_state.json`, returns `{date_str: {key: True, ...}}` |
| `save_state(state)` | Writes `alert_state.json` |
| `make_state_key(signal)` | Returns `"TICKER|Strategy Name"` |
| `build_signal_card(signal)` | Returns HTML card for one signal |
| `build_alert_email(signals, all_signals)` | Returns HTML email body |
| `main()` | Full orchestration: scan → filter → deduplicate → email → save state |

**`MIN_CONFIDENCE = 52.0`** — only send alerts for signals above this score.

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
  Trigger: Every 30 minutes, starting 9:00 AM
  Action:  python C:\Users\Owner\InvestmentDaily\alert_system.py
  Registered by: schedule_alerts.ps1
  Note: alert_system.py self-guards via is_market_open() — does nothing outside NYSE hours
```

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
