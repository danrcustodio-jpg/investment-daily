# Agent Guide â€” Investment Daily

**For AI assistants:** This file contains copy-paste recipes for the most common changes.
Read `ARCHITECTURE.md` first for system design context, then use this file for implementation.

**Location:** `C:\Users\Owner\InvestmentDaily\`
**Run all commands from:** `C:\Users\Owner\InvestmentDaily\` in PowerShell

---

## How to Test Any Change

```powershell
# Quick strategy scan (no email, shows signal count and top signals)
python test_strategy.py

# Full newsletter pipeline (no email)
python test_run.py

# Alert logic (no email, no market-hours check)
python test_alerts.py

# Send a real test newsletter right now
python investment_daily.py
```

### One-command local release gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_full_cycle.ps1
```

What it runs:
- smoke tests (`tests/test_strategy.py`, `tests/test_run.py`, `tests/test_alerts.py`)
- QA suite (`tests/qa_scenarios.py`)
- report generation (`generate_reports.py --alerts`, `--newsletter`)
- eval snapshot (`evals/runs/run_*.json`)
- gate check (`scripts/check_eval_gates.py` vs `evals/gates.local.json`)

Useful flags:
- `-SkipQA` (faster loop)
- `-SkipReports` (logic-only run)
- `-SkipEvalSnapshot` (no eval artifact)
- `-SkipGateCheck` (skip `scripts/check_eval_gates.py`; use if `evals/runs/` is empty)
- `-EvalLabel my_label` (custom run file name)

After a snapshot is written, the script runs `python scripts/check_eval_gates.py --snapshot evals/runs/<label>.json`. If you skipped the snapshot step, it runs `--latest` instead.

---

## Recipe 1: Add a New Ticker to Watch

Edit `strategy_engine.py` â†’ `SCAN_TICKERS` dict:

```python
SCAN_TICKERS: Dict[str, str] = {
    # ... existing tickers ...
    "NEWT":    "New Ticker Name",   # â† add here
}
```

That's all â€” the ticker is automatically included in newsletter, alerts, and dashboard.

Also add to `investment_daily.py` â†’ `MARKET_TICKERS["Hot Stocks"]` if you want it in the market snapshot:

```python
"Hot Stocks": {
    # ... existing ...
    "NEWT": "New Ticker Name",   # â† add here
}
```

---

## Recipe 2: Add a New Trading Strategy

**Step 1:** Add it to `STRATEGY_LINKS` in `strategy_engine.py`:

```python
STRATEGY_LINKS: Dict[str, str] = {
    # ... existing ...
    "My New Strategy":
        "https://www.investopedia.com/terms/x/xxxx.asp",
}
```

**Step 2:** Write a detector function following this exact pattern:

```python
def detect_my_strategy(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    signals = []

    # Check the column exists (pandas-ta column names use full parameter strings)
    col = "INDICATOR_COLUMN_NAME"
    if col not in df.columns or df[col].isna().iloc[-1]:
        return signals

    price = df["Close"]
    val   = df[col]
    cur   = float(val.iloc[-1])

    # Define the boolean mask of historical signal dates for backtesting
    signal_mask = val < SOME_THRESHOLD   # e.g. RSI < 30
    bt = backtest_signal(price, signal_mask)

    if cur < SOME_THRESHOLD:
        signals.append(_make_signal(
            symbol, name,
            "My New Strategy",    # MUST match STRATEGY_LINKS key exactly
            "BULLISH",            # or "BEARISH"
            f"Column = {cur:.1f}  (description of trigger)",
            "Long paragraph explaining what the indicator means and why it triggered.",
            "What action to consider. What confirmation to wait for.",
            bt,
        ))

    return signals
```

**Step 3:** Register it in `scan_ticker()`:

```python
def scan_ticker(symbol: str, name: str) -> List[Dict]:
    # ... existing code ...

    # Add your new indicator computation if needed
    df.ta.your_indicator(length=14, append=True)   # only if not already computed

    # Add your detector call
    signals += detect_my_strategy(symbol, name, df)

    return signals
```

**Step 4:** Update the strategy count in `run_full_scan()` log message:

```python
logger.info(f"Scanning {len(tickers)} tickers across 30 strategy detectors (pandas-ta) ...")
```

---

## Recipe 3: Change Alert Sensitivity

In `alert_system.py`:

```python
MIN_CONFIDENCE = 52.0   # â† lower to get more alerts, raise to get fewer
```

In `strategy_engine.py` â†’ `run_full_scan()`:

```python
filtered = [s for s in all_signals if s.get("confidence", 0) >= 45]
#                                                                ^^ this is the newsletter threshold
```

---

## Recipe 4: Add a New RSS News Feed

In `investment_daily.py` â†’ `RSS_FEEDS` list:

```python
RSS_FEEDS = [
    # ... existing ...
    ("Source Name", "https://example.com/feed.rss"),  # â† add here
]
```

No other changes needed â€” all feeds are processed uniformly.

---

## Recipe 5: Change the Newsletter Schedule

Re-register the task. From PowerShell:

```powershell
schtasks /delete /tn "InvestmentDailyNewsletter" /f

# Then edit schedule_daily.ps1 â€” change the time:
# /ST 07:30   â† change this value (HH:MM format)

powershell -ExecutionPolicy Bypass -File schedule_daily.ps1
```

---

## Recipe 6: Change the Confidence Score Formula

In `strategy_engine.py` â†’ `confidence_score()`:

```python
def confidence_score(bt: Dict) -> float:
    """
    Composite 0-100 score. Current weights:
      40% â†’ 5-day win rate
      20% â†’ 5-day Sharpe (capped at 2.0 â†’ 20pts)
      20% â†’ 20-day win rate
      20% â†’ profit factor (capped at 3.0 â†’ 20pts)
    """
    if bt.get("insufficient_data") or "5d" not in bt:
        return 0.0
    d5  = bt["5d"]
    d20 = bt.get("20d", {})

    score  = d5["win_rate"] * 0.40
    score += min(max(d5["sharpe"], 0), 2.0) / 2.0 * 20
    if d20:
        score += d20["win_rate"] * 0.20
    pf     = d5.get("profit_factor", 1.0)
    score += min(max(pf - 1.0, 0), 2.0) / 2.0 * 20

    return round(score, 1)
```

To add a new metric (e.g., Sortino), adjust the weights to still sum to 100:

```python
score  = d5["win_rate"] * 0.30          # was 0.40
score += min(max(d5["sharpe"], 0), 2.0) / 2.0 * 20
score += min(max(d5["sortino"], 0), 2.0) / 2.0 * 10  # new: 10 pts
if d20:
    score += d20["win_rate"] * 0.20
pf     = d5.get("profit_factor", 1.0)
score += min(max(pf - 1.0, 0), 2.0) / 2.0 * 20
```

---

## Recipe 7: Add a New Dashboard Page

In `dashboard.py`:

**Step 1:** Add a route:

```python
@app.route("/mypage")
def mypage():
    data = _cache.get("signals") or []
    html = """<!DOCTYPE html>..."""   # or use render_template_string(TEMPLATE, ...)
    return render_template_string(html, data=data)
```

**Step 2:** Add a link in the nav bar. Find the nav HTML in `HOME_TEMPLATE` (the large `render_template_string` string) and add:

```html
<a href="/mypage" class="nav-link">My Page</a>
```

---

## Recipe 8: Add a New Polymarket Filter Keyword

In `investment_daily.py` â†’ `FINANCE_KEYWORDS` list:

```python
FINANCE_KEYWORDS = [
    # ... existing keywords ...
    "my new keyword",   # â† add here, lowercase
]
```

Markets are filtered if any keyword appears in `title.lower() + " " + question.lower()`.

---

## Recipe 9: Change Email Recipient

The recipient is hardcoded in two files:

```python
# investment_daily.py line ~39
EMAIL_RECIPIENT = "dan.r.custodio@gmail.com"   # â† change here

# alert_system.py line ~41
EMAIL_RECIPIENT = "dan.r.custodio@gmail.com"   # â† change here
```

---

## Recipe 10: Add a pandas-ta Indicator to the Strategy Scan

`pandas-ta` docs: https://github.com/twopirllc/pandas-ta

All available indicators (200+): run `print(ta.Category)` in Python.

To add to the scan, in `scan_ticker()`:

```python
# Example: add ATR (Average True Range) for volatility
df.ta.atr(length=14, append=True)
# This creates column: ATR_14
```

Then use the column in a detector:

```python
atr_val = float(df["ATR_14"].iloc[-1]) if "ATR_14" in df.columns else None
```

---

## Recipe 11: Add a New Contractor to the Federal Contract Watchlist

The contract-alert scanner (`contract_alerts.py`) checks the USAspending.gov API for newly-awarded federal contracts to a curated list of publicly-traded companies. To add a new ticker:

**Step 1:** Add it to `WATCHLIST` in `contract_watchlist.py`:

```python
WATCHLIST: Dict[str, List[str]] = {
    # ... existing ...
    "TICKER": [
        "primary legal entity name",     # how the parent appears on contracts
        "well-known subsidiary",         # subsidiaries that receive their own awards
    ],
}
```

**Pattern rules:**
- All lowercase substrings; matching is case-insensitive `pat in recipient_name.lower()`
- Be specific enough to avoid false positives. `"general"` would match too many companies; `"general dynamics"` is safe.
- Look up the company on https://www.usaspending.gov/recipient to see how its name is actually recorded.
- Subsidiary mismatches are okay — a `BA` contract awarded to "Spirit AeroSystems" (a Boeing supplier, not subsidiary) will not match, which is correct behavior for ticker mapping.

**Step 2:** Test it with a dry-run, no email:

```powershell
python contract_alerts.py --dry-run --ticker TICKER --days 30 --min-amount 1000000
```

This calls the API once and prints any matched contracts. The smoke test in `tests/test_contracts.py` also validates the resolver — re-run it after editing:

```powershell
python tests/test_contracts.py
```

**Step 3 (optional):** If the ticker is also worth tracking technically, add it to `SCAN_TICKERS` in `strategy_engine.py` (see Recipe 1). Any ticker in `SCAN_TICKERS` without a curated `WATCHLIST` entry auto-gets its company name as the sole pattern.

To **remove** a ticker from contract scanning:
- If it's only in `WATCHLIST`: delete the entry.
- If it's in `SCAN_TICKERS` and you want to keep it for strategy alerts but stop contract scanning: set `WATCHLIST["TICKER"] = []` (empty list — `scan()` skips empty-pattern tickers explicitly, and an existing key in `WATCHLIST` blocks the SCAN_TICKERS company-name fallback).
- If you want to opt out everywhere: add it to `_NON_RECIPIENT_TICKERS` in `contract_watchlist.py`.

---

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `KeyError: 'RSI_14'` | pandas-ta failed silently | Wrap in `if "RSI_14" not in df.columns: return signals` |
| `UnicodeEncodeError` in PowerShell | Emoji in log output, console uses cp1252 | Add `encoding="utf-8"` to `FileHandler` â€” already done |
| `Access is denied` running exe | Windows Store Python sandbox | Use SSH tunnel instead of ngrok exe |
| Task Scheduler `Access is denied` | Needs admin for `Register-ScheduledTask` | Use `schtasks.exe` instead â€” already done in `schedule_alerts.ps1` |
| `alert_state.json` grows forever | State file never trimmed | State is keyed by date string, old dates are harmless but can be deleted manually |
| `yfinance` returns empty DataFrame | Network or Yahoo rate-limit | `if raw.empty or len(raw) < 50: return []` â€” already handled |
| Dashboard shows stale data | Cache not refreshed | POST to `/refresh` or wait 30 min for auto-refresh |

---

## File Encoding Notes

- All `.py` files: UTF-8, no BOM
- All `FileHandler` calls use `encoding="utf-8"` to handle emoji in log messages
- PowerShell `.ps1` scripts: UTF-8 with BOM (saved by VS Code default)
- `alert_state.json`: UTF-8, auto-managed by `json.dump`/`json.load`

---

## Environment Setup (Fresh Machine)

```powershell
cd "C:\Users\Owner\InvestmentDaily"
pip install yfinance feedparser requests python-dotenv pandas-ta flask

# Create .env
notepad .env
# Add these two lines:
# EMAIL_SENDER=your_gmail@gmail.com
# EMAIL_PASSWORD=xxxx xxxx xxxx xxxx

# Optional — Schwab Market Data for strategy scans (equities/ETFs only; crypto/futures stay on yfinance):
# SCHWAB_MARKET_DATA=1
# SCHWAB_CLIENT_ID=...
# SCHWAB_CLIENT_SECRET=...
# SCHWAB_CALLBACK_URL=https://127.0.0.1:8182
# Then once: python scripts/schwab_login.py

# Register scheduled tasks
powershell -ExecutionPolicy Bypass -File schedule_daily.ps1
powershell -ExecutionPolicy Bypass -File schedule_alerts.ps1

# Test
python test_run.py
```

---

## Git / Version Control

The project is **not currently in a git repo**. To initialize:

```powershell
cd "C:\Users\Owner\InvestmentDaily"
git init
echo ".env" > .gitignore
echo "*.log" >> .gitignore
echo "alert_state.json" >> .gitignore
echo "__pycache__/" >> .gitignore
git add .
git commit -m "Initial commit"
```

Do **not** commit `.env` â€” it contains your Gmail App Password.
