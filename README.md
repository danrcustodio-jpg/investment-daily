# Investment Daily

Automated investment newsletter, intraday strategy alerts, and mobile web dashboard for **dan.r.custodio@gmail.com**.

**Location:** `C:\Users\Owner\InvestmentDaily\`  
**Python:** Microsoft Store Python 3.12 (important — has sandbox restrictions on launching executables)

---

## What it does

| Component | Trigger | Output |
|---|---|---|
| **Daily Newsletter** | 7:30 AM every day (Task Scheduler) | HTML email with market data, news, fact-checking, strategy signals, Polymarket |
| **Intraday Alerts** | Every 30 min, Mon–Fri 9:30 AM–4:00 PM ET (Task Scheduler) | Email alert when a strategy signal crosses confidence threshold |
| **Mobile Dashboard** | Manual (`python dashboard.py`) | Web UI at port 5050, accessible on phone via ngrok or local WiFi |

---

## Quick Start

```powershell
cd "C:\Users\Owner\InvestmentDaily"

# Send newsletter now
python investment_daily.py

# Run strategy scan (shows signals, no email)
python test_strategy.py

# Start mobile dashboard (local WiFi: http://192.168.4.43:5050)
python dashboard.py

# Expose dashboard to internet (phone from anywhere)
# In a second PowerShell window after dashboard is running:
ngrok http 5050
```

---

## Scheduled Tasks

```powershell
# View status
schtasks /query /tn "InvestmentDailyNewsletter" /fo list
schtasks /query /tn "InvestmentDailyAlerts" /fo list

# Run manually via scheduler
schtasks /run /tn "InvestmentDailyNewsletter"
schtasks /run /tn "InvestmentDailyAlerts"

# Remove and re-register
schtasks /delete /tn "InvestmentDailyAlerts" /f
powershell -ExecutionPolicy Bypass -File schedule_alerts.ps1
```

---

## File Map

```
InvestmentDaily/
├── investment_daily.py     # Daily newsletter — entry point
├── alert_system.py         # Intraday alerts — entry point
├── strategy_engine.py      # All trading strategies + backtesting
├── dashboard.py            # Flask mobile web dashboard (port 5050)
├── .env                    # Gmail credentials (never commit this)
├── alert_state.json        # Auto-generated: tracks alerts fired today
├── requirements.txt        # Python dependencies
│
├── schedule_daily.ps1      # Register daily newsletter in Task Scheduler
├── schedule_alerts.ps1     # Register intraday alert in Task Scheduler
├── start_dashboard.ps1     # Start dashboard + localhost.run tunnel
├── save_ngrok_token.ps1    # One-time: save ngrok auth token
├── tunnel.py               # Python ngrok tunnel (alternative to PS script)
│
├── test_strategy.py        # Smoke test: strategy scan, no email
├── test_run.py             # Smoke test: full newsletter pipeline, no email
├── test_alerts.py          # Smoke test: alert logic, no email
├── send_context.py         # One-off: email CONTEXT.md to user
│
├── investment_daily.log    # Newsletter run log
├── alert_system.log        # Alert run log
├── dashboard.log           # Dashboard log
│
├── README.md               # This file
├── ARCHITECTURE.md         # System design and data flow
├── AGENT_GUIDE.md          # AI agent change recipes and code patterns
└── CONTEXT.md              # Summary for pasting into AI chat on phone
```

---

## Dependencies

```
pip install yfinance feedparser requests python-dotenv pandas-ta backtesting flask
```

| Package | Purpose |
|---|---|
| `yfinance` | Market price data — free, no API key |
| `feedparser` | RSS news from 9 financial sources |
| `requests` | Polymarket API calls |
| `python-dotenv` | Load `.env` credentials |
| `pandas-ta` | 130+ technical indicators (RSI, MACD, BB, ADX, StochRSI, VWAP, SMA) |
| `numpy` / `pandas` | Data processing and backtest statistics |
| `flask` | Mobile web dashboard |
| `backtesting` | Installed, available for future use |

---

## Environment Variables (`.env`)

```
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

`EMAIL_PASSWORD` is a **Gmail App Password** (16 chars), NOT the account password.  
Generate at: Google Account → Security → 2-Step Verification → App passwords

---

## Data Sources

| Data | Source | Auth |
|---|---|---|
| Market prices | Yahoo Finance via `yfinance` | None |
| Financial news | RSS feeds (Reuters, CNBC, MarketWatch, WSJ, FT, Barron's, Yahoo Finance, Seeking Alpha, Investing.com) | None |
| Prediction markets | Polymarket Gamma API (`gamma-api.polymarket.com`) | None |
| Strategy indicators | `pandas-ta` + `yfinance` 2-year history | None |

---

## Key Configuration Values

All in `strategy_engine.py` unless noted:

| Setting | Location | Current Value |
|---|---|---|
| Tickers scanned | `SCAN_TICKERS` dict | 28 tickers |
| RSI oversold threshold | `detect_rsi()` | `< 32` |
| RSI overbought threshold | `detect_rsi()` | `> 68` |
| Stoch RSI oversold | `detect_stoch_rsi()` | `< 20` |
| Stoch RSI overbought | `detect_stoch_rsi()` | `> 80` |
| VWAP deviation threshold | `detect_vwap()` | `4%` |
| Minimum alert confidence | `alert_system.py → MIN_CONFIDENCE` | `52.0` |
| Data history for backtest | `scan_ticker()` | `2y` |
| Market hours | `alert_system.py` | `9:30–16:00 ET, Mon–Fri` |
| Dashboard port | `dashboard.py` | `5050` |
| Newsletter send time | Task Scheduler | `7:30 AM daily` |
| Alert check interval | Task Scheduler | `Every 30 min` |
