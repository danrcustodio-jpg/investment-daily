# Investment Daily — Codebase Context for AI Chat

Paste this file into Claude (claude.ai) on your phone when you want to
design changes, describe new features, or troubleshoot. Claude will give
you exact code to implement when you get back to your PC.

---

## What this project does

A fully automated investment newsletter + intraday alert system running on
a Windows PC (C:\Users\Owner\InvestmentDaily\). It emails dan.r.custodio@gmail.com.

**Two scheduled jobs (Windows Task Scheduler):**
- `InvestmentDailyNewsletter` — runs daily at 7:30 AM
- `InvestmentDailyAlerts` — runs every 30 min, Mon–Fri 9:30 AM–4:00 PM ET

**Web dashboard** (mobile-friendly, run manually):
- Start: `python dashboard.py` in the project folder
- Access on phone (same WiFi): `http://<PC-IP>:5050`
- Access anywhere: run `start_dashboard.ps1` (requires free ngrok account)

---

## File map

| File | Purpose |
|---|---|
| `investment_daily.py` | Daily newsletter: fetches news, market data, Polymarket, fact-checks, emails |
| `alert_system.py` | Intraday alerts: runs strategy scan during market hours, emails high-confidence signals |
| `strategy_engine.py` | All trading strategy logic: indicators (pandas-ta), backtesting, signal detection |
| `dashboard.py` | Flask web dashboard for phone access |
| `.env` | Email credentials (Gmail sender + App Password) |
| `alert_state.json` | Tracks alert send times (12h cooldown per ticker+strategy) |
| `requirements.txt` | Python dependencies |
| `schedule_alerts.ps1` | Registers intraday alert task in Windows Task Scheduler |
| `schedule_daily.ps1` | Registers daily newsletter task in Windows Task Scheduler |
| `start_dashboard.ps1` | Starts dashboard + ngrok tunnel for phone access |

---

## Key dependencies

- `yfinance` — market price data (free, no API key)
- `pandas-ta` — 130+ technical indicators (RSI, MACD, Bollinger, ADX, StochRSI, VWAP, SMA)
- `feedparser` — RSS news from Reuters, CNBC, MarketWatch, WSJ, FT, Barron's, etc.
- `requests` — Polymarket API (free, no key)
- `flask` — web dashboard
- `python-dotenv` — loads .env credentials
- `numpy` / `pandas` — data processing and backtest math

---

## Strategy engine (strategy_engine.py)

**9 strategies scanned across 28 tickers:**

| Strategy | Signal | Library |
|---|---|---|
| RSI Oversold/Overbought | < 32 buy / > 68 sell | pandas-ta RSI_14 |
| Stochastic RSI | < 20 buy / > 80 sell | pandas-ta STOCHRSIk_14_14_3_3 |
| MACD Crossover | MACD crosses signal line | pandas-ta MACD_12_26_9 |
| Golden / Death Cross | 50-day SMA vs 200-day SMA | pandas-ta SMA_50, SMA_200 |
| Bollinger Band Touch | Price at upper/lower band | pandas-ta BBL_20_2.0, BBU_20_2.0 |
| ADX Trend Strength | ADX > 25 + DI direction | pandas-ta ADX_14 |
| VWAP Deviation | Price > 4% from 20-day VWAP | Manual (High+Low+Close)/3 × Volume |
| 52-Week Breakout | New annual high | Rolling 252-day max |
| Volume Spike | 2x avg volume + 2% price move | Volume vs rolling 20-day avg |

**Backtest stats computed per signal (numpy):**
- Win Rate, Avg Return, Sharpe Ratio, Sortino Ratio, Profit Factor, Max Drawdown
- Computed from 2 years of history
- Confidence score (0–100) = 40% 5d-win-rate + 20% Sharpe + 20% 20d-win-rate + 20% profit-factor

**Watchlist of 28 tickers:** NVDA, META, TSLA, AVGO, AAPL, MSFT, AMZN, GOOGL,
PLTR, IONQ, RKLB, SMCI, SPY, QQQ, IWM, SMH, ARKK, XBI, XLE, XLK,
TQQQ, UPRO, SOXL, BTC-USD, ETH-USD, SOL-USD, GC=F, CL=F

---

## Newsletter (investment_daily.py)

1. Pulls market data for 30+ assets (6 categories) via yfinance
2. Fetches news from 9 RSS feeds (last 24 hours, deduplicated)
3. Queries Polymarket API for financial prediction markets
4. Fact-checks news headlines against actual same-day price moves
   - Verdicts: CONFIRMED / CONTRADICTED / MIXED / UNVERIFIED
5. Runs full strategy scan (same as alerts)
6. Sends HTML email with:
   - Market sentiment banner
   - Live market table
   - Strategy signals section (with Learn More links to Investopedia)
   - News with Read More buttons + fact-check verdict
   - Polymarket prediction markets

---

## Alert system (alert_system.py)

- Only runs Mon–Fri 9:30 AM – 4:00 PM ET (exits immediately otherwise)
- Runs strategy scan → filters by confidence >= 52
- State file (alert_state.json) prevents repeat alerts for same strategy+ticker within 12 hours
- Alert email shows: strategy signal cards with full backtest table (Sharpe, Sortino, etc.)
- "Learn More" links → Investopedia for each strategy

---

## How to describe changes to AI

Use prompts like:

**"Add a new strategy..."**
> In strategy_engine.py, in the scan_ticker() function, I want to add a new
> strategy called [NAME]. It should fire when [CONDITION]. Add it as a new
> detect_X() function following the same pattern as detect_rsi().

**"Add a new ticker..."**
> In strategy_engine.py, add [TICKER] = "[NAME]" to the SCAN_TICKERS dict.
> Also add it to the WATCH_LIST in alert_system.py with threshold [X]%.

**"Change a threshold..."**
> In strategy_engine.py, in detect_rsi(), change the oversold threshold
> from 32 to [NEW VALUE].

**"Add a new section to the newsletter..."**
> In investment_daily.py, in the build_email() function, add a new section
> after the strategy signals section that shows [CONTENT]. Follow the same
> HTML card style as the existing sections.

**"Add a new page to the dashboard..."**
> In dashboard.py, add a new Flask route GET /[name] that shows [CONTENT].
> Add it to the nav_items list in the shell() function.

---

## Common commands (run in C:\Users\Owner\InvestmentDaily\)

```powershell
# Send newsletter manually
python investment_daily.py

# Run alert scan manually (ignores market hours check in test)
python test_strategy.py

# Start web dashboard (local WiFi only)
python dashboard.py

# Start dashboard + ngrok tunnel (phone access from anywhere)
powershell -ExecutionPolicy Bypass -File start_dashboard.ps1

# Check scheduled tasks
schtasks /query /tn "InvestmentDailyNewsletter" /fo list
schtasks /query /tn "InvestmentDailyAlerts" /fo list
```

---

## Environment (.env file)

```
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password (16 chars)
```

---

*Last updated: April 2026*
