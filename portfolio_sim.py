#!/usr/bin/env python3
"""
Portfolio Simulation — Investment Daily
========================================
Tracks the $194,000 allocation recommended on 2026-04-20 based on live strategy signals.

Usage:
  python portfolio_sim.py            # print current P&L to console
  python portfolio_sim.py --email    # email today's status report
  python portfolio_sim.py --weekly   # email full weekly review (charts + analysis)
  python portfolio_sim.py --init     # re-initialize simulation (RESETS everything)
  python portfolio_sim.py --snapshot # record today's prices into history (run daily)
"""

import os
import sys
import json
import smtplib
import logging
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yfinance as yf
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(SCRIPT_DIR, "logs"), exist_ok=True)
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIR, "logs", "portfolio_sim.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

EMAIL_SENDER    = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")
DEFAULT_EMAIL_RECIPIENT = "dan.r.custodio@gmail.com"


def _parse_recipients(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


EMAIL_RECIPIENTS = _parse_recipients(os.getenv("EMAIL_RECIPIENTS"))
if not EMAIL_RECIPIENTS:
    EMAIL_RECIPIENTS = [DEFAULT_EMAIL_RECIPIENT]
    logger.warning(
        "EMAIL_RECIPIENTS not set; using default recipient %s. "
        "Set EMAIL_RECIPIENTS in .env to override.",
        DEFAULT_EMAIL_RECIPIENT,
    )
STATE_FILE      = os.path.join(SCRIPT_DIR, "sim_portfolio.json")

TOTAL_CAPITAL   = 194_000.00
CASH_APY        = 0.045   # ~4.5% annual yield on T-Bills / money market

# ─── Tax & Trading Cost Assumptions ──────────────────────────────────────────
# Short-term gains (< 1 year) taxed as ordinary income; long-term at cap gains rate.
# Slippage covers bid/ask spread and market impact (no explicit broker commission assumed).
TAX_SHORT_TERM_RATE = 0.32    # 32% — ordinary income bracket for active trader
TAX_LONG_TERM_RATE  = 0.15    # 15% — long-term capital gains rate
SLIPPAGE_RATE       = 0.001   # 0.10% per trade (entry + exit = 0.20% round-trip)
MIN_EVAL_CONFIDENCE = 55      # minimum backtest score to surface as new opportunity
MAX_NEW_IDEAS       = 3       # max fresh entries on each evaluation cycle
MIN_TRADE_SIZE      = 2_500   # do not open tiny positions that cannot overcome fees

# ─── Initial Portfolio (locked in 2026-04-20) ─────────────────────────────────

INITIAL_PORTFOLIO = {
    "XLE": {
        "name":       "Energy ETF (XLE)",
        "allocation": 35_000,
        "type":       "market",
        "entry_price": 55.395,
        "shares":     round(35_000 / 55.395, 4),
        "signal":     "VWAP Deviation — Oversold",
        "confidence": 67.7,
        "win_rate":   74.1,
        "sharpe":     1.26,
        "rationale":  "Only clean bullish signal with no conflicting bearish signals. "
                      "74.1% win rate historically. Energy sector diverging positively.",
        "status":     "open",
        "triggered_date": None,
    },
    "CL=F": {
        "name":       "Crude Oil (CL=F)",
        "allocation": 15_000,
        "type":       "market",
        "entry_price": 87.25,
        "shares":     round(15_000 / 87.25, 4),
        "signal":     "Stochastic RSI Oversold",
        "confidence": 60.9,
        "win_rate":   61.3,
        "sharpe":     1.63,
        "rationale":  "Confirms the XLE energy trade. Crude oil stochRSI oversold.",
        "status":     "open",
        "triggered_date": None,
    },
    "GOOGL": {
        "name":          "Alphabet (GOOGL)",
        "allocation":    15_000,
        "type":          "limit",
        "ask_at_init":   339.175,
        "limit_price":   322.22,   # ~5% below entry ask
        "entry_price":   None,
        "shares":        None,
        "signal":        "ADX Strong Trend — Bullish",
        "confidence":    66.9,
        "win_rate":      55.6,
        "sharpe":        1.85,
        "rationale":     "ADX trend intact but RSI overbought. Waiting for 5% pullback to $322.22.",
        "status":        "pending",
        "triggered_date": None,
    },
    "MSFT": {
        "name":          "Microsoft (MSFT)",
        "allocation":    9_000,
        "type":          "limit",
        "ask_at_init":   419.12,
        "limit_price":   399.00,   # ~4.8% below entry ask
        "entry_price":   None,
        "shares":        None,
        "signal":        "ADX Strong Trend — Bullish",
        "confidence":    67.9,
        "win_rate":      67.8,
        "sharpe":        1.75,
        "rationale":     "RSI at 78.9 — overextended. Waiting for pullback to $399.",
        "status":        "pending",
        "triggered_date": None,
    },
    "CASH": {
        "name":       "Cash / Money Market",
        "allocation": 120_000,
        "type":       "cash",
        "annual_rate": CASH_APY,
        "rationale":  "SPY & QQQ both showing highest-confidence bearish signals. "
                      "Holding 62% in T-Bills (~4.5% APY) until pullback confirmed.",
        "status":     "open",
        "triggered_date": None,
    },
}

BENCHMARK = {"ticker": "SPY", "entry_price": 707.79}


# ─── State Management ─────────────────────────────────────────────────────────

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Could not load state file ({e}), starting fresh.")
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def init_simulation() -> dict:
    logger.info("Initializing simulation...")
    state = {
        "initialized":    datetime.now().isoformat(),
        "init_date":      date.today().isoformat(),
        "total_capital":  TOTAL_CAPITAL,
        "positions":      INITIAL_PORTFOLIO,
        "benchmark":      BENCHMARK,
        "snapshots":      [],
    }
    save_state(state)
    logger.info(f"Simulation initialized. State saved to {STATE_FILE}")
    return state


# ─── Price Fetching ───────────────────────────────────────────────────────────

def get_current_prices(tickers: list[str]) -> dict[str, float]:
    prices = {}
    for t in tickers:
        try:
            hist = yf.Ticker(t).history(period="1d")
            if not hist.empty:
                prices[t] = float(hist["Close"].iloc[-1])
        except Exception as e:
            logger.warning(f"Could not fetch {t}: {e}")
    return prices


def get_price_history_since(ticker: str, since_date: str):
    """Return daily OHLCV since a given date string (YYYY-MM-DD)."""
    try:
        hist = yf.Ticker(ticker).history(start=since_date)
        return hist
    except Exception as e:
        logger.warning(f"History fetch failed for {ticker}: {e}")
        return None


# ─── Limit Order Check ────────────────────────────────────────────────────────

def check_limit_orders(state: dict, since_date: str) -> dict:
    """
    Check if any pending limit orders have been triggered since init_date.
    Uses daily Low prices to determine if limit was ever hit.
    Updates state in-place and returns it.
    """
    positions = state["positions"]

    for ticker, pos in positions.items():
        if pos["type"] != "limit" or pos["status"] != "pending":
            continue

        hist = get_price_history_since(ticker, since_date)
        if hist is None or hist.empty:
            continue

        limit = pos["limit_price"]

        for dt, row in hist.iterrows():
            day_low = float(row["Low"])
            if day_low <= limit:
                trigger_date = dt.date().isoformat()
                entry_price  = limit   # assume filled at limit price
                shares       = round(pos["allocation"] / entry_price, 4)

                pos["status"]         = "open"
                pos["entry_price"]    = entry_price
                pos["shares"]         = shares
                pos["triggered_date"] = trigger_date

                logger.info(
                    f"LIMIT TRIGGERED: {ticker} hit ${limit:.2f} on {trigger_date}. "
                    f"Filled {shares} shares at ${entry_price:.2f}."
                )
                break

    return state


# ─── P&L Calculation ─────────────────────────────────────────────────────────

def compute_pnl(state: dict, current_prices: dict) -> list[dict]:
    """
    Returns list of position dicts with current P&L attached.
    """
    init_date_str = state.get("init_date", date.today().isoformat())
    init_date     = date.fromisoformat(init_date_str)
    days_elapsed  = (date.today() - init_date).days
    results       = []

    for ticker, pos in state["positions"].items():
        row = dict(pos)
        row["ticker"] = ticker

        if pos["type"] == "cash":
            daily_rate   = pos["annual_rate"] / 365
            interest     = pos["allocation"] * daily_rate * days_elapsed
            row["current_value"] = pos["allocation"] + interest
            row["pnl_dollars"]   = interest
            row["pnl_pct"]       = interest / pos["allocation"] * 100
            row["current_price"] = None
            results.append(row)
            continue

        if pos["status"] == "pending":
            row["current_value"] = pos["allocation"]
            row["pnl_dollars"]   = 0.0
            row["pnl_pct"]       = 0.0
            row["current_price"] = current_prices.get(ticker)
            results.append(row)
            continue

        # Open position
        cp = current_prices.get(ticker)
        if cp and pos["entry_price"] and pos["shares"]:
            current_value        = cp * pos["shares"]
            pnl_dollars          = current_value - pos["allocation"]
            pnl_pct              = pnl_dollars / pos["allocation"] * 100
            row["current_price"] = cp
            row["current_value"] = current_value
            row["pnl_dollars"]   = pnl_dollars
            row["pnl_pct"]       = pnl_pct
        else:
            row["current_price"] = cp
            row["current_value"] = pos["allocation"]
            row["pnl_dollars"]   = 0.0
            row["pnl_pct"]       = 0.0

        results.append(row)

    return results


def compute_benchmark_pnl(state: dict, current_prices: dict) -> dict:
    bm    = state["benchmark"]
    cp    = current_prices.get(bm["ticker"])
    if cp:
        pnl_pct = (cp - bm["entry_price"]) / bm["entry_price"] * 100
        pnl_dollars = TOTAL_CAPITAL * pnl_pct / 100
    else:
        pnl_pct = 0.0
        pnl_dollars = 0.0
        cp = bm["entry_price"]
    return {
        "ticker":        bm["ticker"],
        "entry_price":   bm["entry_price"],
        "current_price": cp,
        "pnl_pct":       round(pnl_pct, 3),
        "pnl_dollars":   round(pnl_dollars, 2),
    }


# ─── Snapshot ────────────────────────────────────────────────────────────────

def take_snapshot(state: dict, recommendations: list[dict] | None = None) -> dict:
    """Record today's portfolio value for charting the weekly equity curve."""
    tickers = [k for k in state["positions"] if k != "CASH"]
    prices  = get_current_prices(tickers + [state["benchmark"]["ticker"]])

    state   = check_limit_orders(state, state["init_date"])
    rows    = compute_pnl(state, prices)
    bm      = compute_benchmark_pnl(state, prices)

    total_value = sum(r.get("current_value", r["allocation"]) for r in rows)
    portfolio_pnl_pct = (total_value - TOTAL_CAPITAL) / TOTAL_CAPITAL * 100

    snap = {
        "date":            date.today().isoformat(),
        "total_value":     round(total_value, 2),
        "portfolio_pnl":   round(portfolio_pnl_pct, 3),
        "benchmark_pnl":   bm["pnl_pct"],
        "prices":          prices,
    }

    existing = [s for s in state.get("snapshots", []) if s["date"] != snap["date"]]
    existing.append(snap)
    state["snapshots"] = existing

    if recommendations is not None:
        # Strip exit_cost dicts (too large for JSON state); keep the text fields
        state["recommendations"] = [
            {k: v for k, v in r.items() if k != "exit_cost"}
            for r in recommendations
        ]
        state["recommendations_updated"] = datetime.now().isoformat()

    save_state(state)
    logger.info(f"Snapshot saved: portfolio {portfolio_pnl_pct:+.2f}% | SPY {bm['pnl_pct']:+.2f}%")
    return state, rows, bm


# ─── Market Evaluation Engine ────────────────────────────────────────────────

def _holding_days(pos: dict, state: dict) -> int:
    """Days since position was entered (or sim init date for day-1 market orders)."""
    if pos.get("triggered_date"):
        start = date.fromisoformat(pos["triggered_date"])
    elif pos.get("status") == "open" and pos.get("type") == "market":
        start = date.fromisoformat(state.get("init_date", date.today().isoformat()))
    else:
        start = date.today()
    return max(0, (date.today() - start).days)


def _tax_rate(pos: dict, state: dict) -> float:
    """Return applicable capital gains rate based on how long the position has been held."""
    return TAX_LONG_TERM_RATE if _holding_days(pos, state) >= 365 else TAX_SHORT_TERM_RATE


def _exit_cost(pos: dict, current_price: float, state: dict) -> dict:
    """
    Full cost of liquidating an open equity position.
    Gains are taxed; losses produce a tax benefit. Slippage is always a cost.
    Returns a dict with gross_gain, tax_cost/benefit, slippage, net_proceeds, net_gain_after_costs.
    """
    alloc   = pos["allocation"]
    shares  = pos.get("shares") or 0
    current_value = (shares * current_price) if (shares and current_price) else alloc
    gross_gain    = current_value - alloc

    if gross_gain >= 0:
        tax_cost    = gross_gain * _tax_rate(pos, state)
        tax_benefit = 0.0
    else:
        tax_cost    = 0.0
        tax_benefit = abs(gross_gain) * TAX_SHORT_TERM_RATE  # loss offsets ordinary income

    slippage     = current_value * SLIPPAGE_RATE
    net_proceeds = current_value - tax_cost + tax_benefit - slippage

    return {
        "gross_gain":           round(gross_gain, 2),
        "tax_cost":             round(tax_cost, 2),
        "tax_benefit":          round(tax_benefit, 2),
        "slippage":             round(slippage, 2),
        "net_proceeds":         round(net_proceeds, 2),
        "net_gain_after_costs": round(net_proceeds - alloc, 2),
        "holding_days":         _holding_days(pos, state),
        "tax_rate_pct":         round(_tax_rate(pos, state) * 100, 0),
        "term":                 "long" if _holding_days(pos, state) >= 365 else "short",
    }


def _score_signal(sig: dict) -> float:
    """
    Composite quality score for one signal.
    Higher = better risk/reward.  Used to compare bull vs bear signal weight.
    """
    d5      = sig.get("backtest", {}).get("5d", {})
    wr      = (d5.get("win_rate") or 50) / 100
    sharpe  = min(abs(d5.get("sharpe") or 1.0), 4.0)
    conf    = (sig.get("confidence") or 50) / 100
    dd_raw  = d5.get("max_drawdown")
    dd      = abs(dd_raw if dd_raw is not None else -10) / 100
    return conf * wr * (1 + sharpe / 10) * (1 - dd * 0.25)


def evaluate_portfolio(state: dict, prices: dict, signals: list[dict]) -> list[dict]:
    """
    Evaluate every position against live signals. Factor in taxes and slippage.
    Returns a list of recommendation dicts, sorted by priority (high → low).

    Recommendations surface three action types:
      HOLD            — current position, thesis intact
      REVIEW_EXIT     — net bearish signal environment; shows full exit cost
      HOLD_LIMIT      — pending limit order, still valid
      CANCEL_LIMIT    — pending limit, but bearish signals now dominate
      NEW_OPPORTUNITY — bullish signal not yet in portfolio, capital is deployable
    """
    positions  = state["positions"]
    recs: list[dict] = []

    # Build per-ticker signal map from the full scan
    sig_map: dict[str, dict[str, list]] = {}
    for s in signals:
        t   = s["ticker"]
        dir = s["direction"].upper()
        if t not in sig_map:
            sig_map[t] = {"bullish": [], "bearish": []}
        sig_map[t]["bullish" if dir == "BULLISH" else "bearish"].append(s)

    avail_cash     = 0.0
    exit_proceeds  = 0.0  # capital that would be freed by any REVIEW_EXIT

    # ── Evaluate existing positions ───────────────────────────────────────────
    for ticker, pos in positions.items():
        if pos["type"] == "cash":
            avail_cash = pos["allocation"]
            continue

        cp   = prices.get(ticker)
        sigs = sig_map.get(ticker, {"bullish": [], "bearish": []})
        bull = sigs["bullish"]
        bear = sigs["bearish"]

        bull_score = sum(_score_signal(s) for s in bull)
        bear_score = sum(_score_signal(s) for s in bear)
        net_score  = bull_score - bear_score  # positive = net bullish

        if pos["status"] == "pending":
            # Pending limit — should we cancel?
            if bear_score > bull_score * 1.4 and bear:
                top_bear = max(bear, key=lambda s: s["confidence"])
                recs.append({
                    "action":   "CANCEL_LIMIT",
                    "ticker":   ticker,
                    "priority": "medium",
                    "reason": (
                        f"{len(bear)} bearish signal(s) now outweigh {len(bull)} bullish. "
                        f"Strongest: {top_bear['strategy']} at score {top_bear['confidence']}. "
                        f"Limit at ${pos['limit_price']:.2f} may never fill profitably."
                    ),
                    "tax_note": "No tax impact — order not yet filled.",
                    "exit_cost": None,
                })
            else:
                near_gap = ""
                if cp and pos.get("limit_price"):
                    gap = (cp - pos["limit_price"]) / cp * 100
                    near_gap = f" Current price ${cp:.2f} is {gap:.1f}% above limit."
                recs.append({
                    "action":   "HOLD_LIMIT",
                    "ticker":   ticker,
                    "priority": "low",
                    "reason": (
                        f"Thesis intact: {len(bull)} bullish vs {len(bear)} bearish signals.{near_gap} "
                        f"Keep limit order at ${pos['limit_price']:.2f}."
                    ),
                    "tax_note": "No tax impact until order fills.",
                    "exit_cost": None,
                })
            continue

        # Open position — should we exit?
        if pos["status"] == "open" and cp:
            ec = _exit_cost(pos, cp, state)

            if net_score < -0.15:  # net bearish after weighting
                top_bear = max(bear, key=lambda s: s["confidence"]) if bear else None
                priority = "high" if bear_score > bull_score * 1.5 else "medium"
                bear_desc = (
                    f"Strongest bearish: {top_bear['strategy']} "
                    f"(score {top_bear['confidence']})."
                    if top_bear else "Multiple bearish signals present."
                )
                tax_str = (
                    f"${ec['tax_cost']:,.0f} tax owed ({ec['tax_rate_pct']:.0f}% {ec['term']}-term)"
                    if ec["tax_cost"] > 0
                    else f"${ec['tax_benefit']:,.0f} tax benefit (loss deduction)"
                )
                exit_proceeds += ec["net_proceeds"]
                recs.append({
                    "action":   "REVIEW_EXIT",
                    "ticker":   ticker,
                    "priority": priority,
                    "reason": (
                        f"Signal environment turned net bearish "
                        f"({len(bear)} bear score {bear_score:.2f} vs {len(bull)} bull score {bull_score:.2f}). "
                        f"{bear_desc} "
                        f"Gross P&L: ${ec['gross_gain']:+,.0f}."
                    ),
                    "tax_note": (
                        f"Held {ec['holding_days']} days ({ec['term']}-term rate). "
                        f"{tax_str} + ${ec['slippage']:,.0f} slippage. "
                        f"Net proceeds if sold: ${ec['net_proceeds']:,.0f}."
                    ),
                    "exit_cost": ec,
                })
            else:
                pnl_str = f"${ec['gross_gain']:+,.0f}" if ec["gross_gain"] != 0 else "$0"
                recs.append({
                    "action":   "HOLD",
                    "ticker":   ticker,
                    "priority": "low",
                    "reason": (
                        f"Signal still net bullish "
                        f"({len(bull)} bull score {bull_score:.2f} vs {len(bear)} bear score {bear_score:.2f}). "
                        f"Gross P&L: {pnl_str}. Holding avoids ${ec['tax_cost']:,.0f} in taxes."
                    ),
                    "tax_note": (
                        f"Held {ec['holding_days']} days ({ec['term']}-term). "
                        f"Exiting now costs ${ec['tax_cost']:,.0f} tax "
                        f"+ ${ec['slippage']:,.0f} slippage = "
                        f"${ec['tax_cost'] + ec['slippage']:,.0f} total friction."
                    ),
                    "exit_cost": ec,
                })

    # ── Identify new opportunities not already in the portfolio ───────────────
    in_portfolio  = set(positions.keys())
    deployable    = avail_cash + exit_proceeds

    if deployable >= 5_000:
        candidates = []
        for ticker, sigs in sig_map.items():
            if ticker in in_portfolio:
                continue
            bull = sigs["bullish"]
            bear = sigs["bearish"]
            if not bull:
                continue

            top_bull      = max(bull, key=lambda s: s["confidence"])
            if top_bull["confidence"] < MIN_EVAL_CONFIDENCE:
                continue

            top_bear_conf = max((s["confidence"] for s in bear), default=0)
            if top_bear_conf >= 78:
                continue  # skip when a very high-confidence bear signal exists

            d5    = top_bull.get("backtest", {}).get("5d", {})
            score = _score_signal(top_bull) - sum(_score_signal(s) for s in bear) * 0.5
            candidates.append({
                "ticker":       ticker,
                "signal":       top_bull["strategy"],
                "confidence":   top_bull["confidence"],
                "win_rate":     d5.get("win_rate", "?"),
                "avg_return":   d5.get("avg_return", "?"),
                "max_drawdown": d5.get("max_drawdown", "?"),
                "sharpe":       d5.get("sharpe", "?"),
                "score":        score,
                "bear_count":   len(bear),
                "top_bear_conf": top_bear_conf,
                "is_crypto":    ticker.endswith("-USD"),
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        selected: list[dict] = []
        # Ensure crypto is represented when a valid crypto setup exists.
        best_crypto = next((c for c in candidates if c["is_crypto"]), None)
        if best_crypto:
            selected.append(best_crypto)
        for c in candidates:
            if c in selected:
                continue
            selected.append(c)
            if len(selected) >= MAX_NEW_IDEAS:
                break

        for c in selected[:MAX_NEW_IDEAS]:
            suggested_alloc = round(min(deployable * 0.35, 30_000) / 1000) * 1000
            if c["is_crypto"]:
                suggested_alloc = round(min(deployable * 0.25, 25_000) / 1000) * 1000
            conflict_note = (
                "No conflicting bearish signals."
                if c["bear_count"] == 0
                else f"{c['bear_count']} minor bearish signal(s), max confidence {c['top_bear_conf']}."
            )
            recs.append({
                "action":   "NEW_OPPORTUNITY",
                "ticker":   c["ticker"],
                "priority": "high" if c["confidence"] >= 70 else "medium",
                "reason": (
                    f"{c['signal']} — Score {c['confidence']}, "
                    f"Win Rate {c['win_rate']}%, Avg 5d Return {c['avg_return']}%, "
                    f"Max Drawdown {c['max_drawdown']}%, Sharpe {c['sharpe']}. {conflict_note}"
                ),
                "tax_note": (
                    f"New position — no tax on entry. "
                    f"Suggested allocation: ~${suggested_alloc:,.0f} of "
                    f"${deployable:,.0f} deployable. "
                    f"Entry slippage est. ${suggested_alloc * SLIPPAGE_RATE:,.0f}."
                ),
                "suggested_allocation": suggested_alloc,
                "is_crypto": c["is_crypto"],
                "exit_cost": None,
            })

    # Sort: high first, then by ticker name
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: (priority_order.get(r["priority"], 9), r["ticker"]))
    return recs


def _append_move(state: dict, move: dict) -> None:
    log = state.setdefault("trade_log", [])
    move["timestamp"] = datetime.now().isoformat()
    log.append(move)
    state["trade_log"] = log[-250:]  # cap growth


def apply_mock_trades(state: dict, recs: list[dict], prices: dict) -> tuple[dict, list[dict]]:
    """
    Paper-execute recommendation actions and record explanations for each move.
    Returns updated state and list of executed move dicts.
    """
    positions = state["positions"]
    executed: list[dict] = []
    cash_pos = positions.get("CASH")
    if not cash_pos:
        cash_pos = {
            "name": "Cash / Money Market",
            "allocation": 0.0,
            "type": "cash",
            "annual_rate": CASH_APY,
            "rationale": "Auto-created cash sleeve for simulation accounting.",
            "status": "open",
            "triggered_date": None,
        }
        positions["CASH"] = cash_pos

    for r in recs:
        action = r.get("action")
        ticker = r.get("ticker")
        if not ticker:
            continue

        if action == "REVIEW_EXIT":
            pos = positions.get(ticker)
            cp = prices.get(ticker)
            if not pos or pos.get("status") != "open" or cp is None:
                continue
            ec = _exit_cost(pos, cp, state)
            del positions[ticker]
            cash_pos["allocation"] += ec["net_proceeds"]
            move = {
                "action": "SELL",
                "ticker": ticker,
                "gross_gain": ec["gross_gain"],
                "net_proceeds": ec["net_proceeds"],
                "tax_cost": ec["tax_cost"],
                "slippage": ec["slippage"],
                "explanation": f"{r['reason']} {r['tax_note']}",
            }
            _append_move(state, move)
            executed.append(move)
            continue

        if action == "CANCEL_LIMIT":
            pos = positions.get(ticker)
            if not pos or pos.get("status") != "pending":
                continue
            freed = float(pos.get("allocation", 0.0))
            del positions[ticker]
            cash_pos["allocation"] += freed
            move = {
                "action": "CANCEL_LIMIT",
                "ticker": ticker,
                "freed_cash": round(freed, 2),
                "explanation": f"{r['reason']} {r['tax_note']}",
            }
            _append_move(state, move)
            executed.append(move)
            continue

        if action == "NEW_OPPORTUNITY":
            if ticker in positions:
                continue
            cp = prices.get(ticker)
            if cp is None or cp <= 0:
                continue
            avail_cash = float(cash_pos.get("allocation", 0.0))
            if avail_cash < MIN_TRADE_SIZE:
                continue

            suggested = float(r.get("suggested_allocation") or 0.0)
            alloc = suggested if suggested > 0 else round(min(avail_cash * 0.35, 30_000) / 1000) * 1000
            alloc = max(MIN_TRADE_SIZE, min(alloc, avail_cash))

            # Keep fees explicit: entry slippage is paid from cash in addition to allocation.
            entry_fee = alloc * SLIPPAGE_RATE
            total_needed = alloc + entry_fee
            if total_needed > avail_cash:
                alloc = max(0.0, round((avail_cash / (1 + SLIPPAGE_RATE)) / 100) * 100)
                entry_fee = alloc * SLIPPAGE_RATE
                total_needed = alloc + entry_fee
            if alloc < MIN_TRADE_SIZE or total_needed > avail_cash:
                continue

            shares = round(alloc / cp, 6)
            positions[ticker] = {
                "name": ticker,
                "allocation": round(alloc, 2),
                "type": "market",
                "entry_price": cp,
                "shares": shares,
                "signal": r.get("signal", "Strategy signal"),
                "confidence": r.get("confidence"),
                "win_rate": None,
                "sharpe": None,
                "rationale": r.get("reason", ""),
                "status": "open",
                "triggered_date": date.today().isoformat(),
            }
            cash_pos["allocation"] = round(avail_cash - total_needed, 2)
            move = {
                "action": "BUY",
                "ticker": ticker,
                "allocation": round(alloc, 2),
                "entry_price": round(cp, 4),
                "shares": shares,
                "entry_fee": round(entry_fee, 2),
                "is_crypto": bool(r.get("is_crypto")),
                "explanation": f"{r['reason']} {r['tax_note']}",
            }
            _append_move(state, move)
            executed.append(move)

    state["positions"] = positions
    return state, executed


# ─── Console Report ──────────────────────────────────────────────────────────

def print_report(rows: list[dict], bm: dict, state: dict) -> None:
    init_date   = state.get("init_date", "?")
    days        = (date.today() - date.fromisoformat(init_date)).days
    total_value = sum(r.get("current_value", r["allocation"]) for r in rows)
    total_pnl   = total_value - TOTAL_CAPITAL
    total_pct   = total_pnl / TOTAL_CAPITAL * 100

    print("\n" + "="*72)
    print(f"  PORTFOLIO SIMULATION  —  Started {init_date}  ({days} days elapsed)")
    print("="*72)
    print(f"  {'TICKER':<10} {'NAME':<28} {'STATUS':<10} {'ALLOC':>9} {'P&L $':>10} {'P&L %':>8}")
    print("-"*72)

    for r in rows:
        status_str = r["status"].upper()
        if r["type"] == "limit" and r["status"] == "pending":
            limit = r.get("limit_price", 0)
            cur   = r.get("current_price") or 0
            gap   = (cur - limit) / limit * 100 if limit else 0
            status_str = f"PENDING ({gap:+.1f}% from limit)"
        pnl_str = f"${r['pnl_dollars']:+,.2f}" if r['pnl_dollars'] != 0 else "—"
        pct_str = f"{r['pnl_pct']:+.2f}%" if r['pnl_pct'] != 0 else "—"
        print(f"  {r['ticker']:<10} {r['name']:<28} {status_str:<10} ${r['allocation']:>8,.0f} {pnl_str:>10} {pct_str:>8}")

    print("-"*72)
    print(f"  {'TOTAL':<10} {'':28} {'':10} ${TOTAL_CAPITAL:>8,.0f} ${total_pnl:>+9,.2f} {total_pct:>+7.2f}%")
    print()
    print(f"  BENCHMARK (SPY)  entry ${bm['entry_price']:.2f}  ->  current ${bm['current_price']:.2f}  {bm['pnl_pct']:+.2f}%  (${bm['pnl_dollars']:+,.0f} if 100% SPY)")
    alpha = total_pct - bm["pnl_pct"]
    print(f"  ALPHA vs SPY:  {alpha:+.2f}%  ({'outperforming' if alpha >= 0 else 'underperforming'})")

    # Limit order status
    pending = [r for r in rows if r["type"] == "limit" and r["status"] == "pending"]
    if pending:
        print()
        print("  WATCHING (limit orders not yet triggered):")
        for r in pending:
            cur   = r.get("current_price") or 0
            limit = r.get("limit_price", 0)
            gap   = (cur - limit) / cur * 100 if cur else 0
            print(f"    {r['ticker']:<8} waiting for ${limit:.2f}  (currently ${cur:.2f}, needs to drop {gap:.1f}% more)")

    # Equity curve if snapshots exist
    snaps = state.get("snapshots", [])
    if len(snaps) >= 2:
        print()
        print("  EQUITY CURVE (daily):")
        print(f"  {'Date':<12} {'Portfolio':>12} {'SPY':>10} {'Alpha':>8}")
        for s in sorted(snaps, key=lambda x: x["date"]):
            alpha_d = s["portfolio_pnl"] - s["benchmark_pnl"]
            print(f"  {s['date']:<12} {s['portfolio_pnl']:>+11.2f}%  {s['benchmark_pnl']:>+9.2f}%  {alpha_d:>+7.2f}%")

    print("="*72 + "\n")

    # Show cached advisor output if available
    recs = state.get("recommendations", [])
    if recs:
        action_icons = {
            "HOLD": "[OK]", "HOLD_LIMIT": "[OK]", "REVIEW_EXIT": "[!!]",
            "CANCEL_LIMIT": "[!!]", "NEW_OPPORTUNITY": "[>>]",
        }
        print("  STRATEGY ADVISOR  (taxes & fees included)")
        print("-"*72)
        for r in recs:
            icon = action_icons.get(r["action"], "•")
            print(f"  {icon} [{r['action']}] {r['ticker']}")
            print(f"     {r['reason']}")
            print(f"     Tax/Fee: {r['tax_note']}")
            print()
        print("="*72 + "\n")

    moves = state.get("trade_log", [])
    if moves:
        print("  LAST PAPER MOVES")
        print("-"*72)
        for m in moves[-6:]:
            stamp = m.get("timestamp", "")[:19].replace("T", " ")
            print(f"  [{stamp}] {m.get('action')} {m.get('ticker')}")
            print(f"     {m.get('explanation', '')}")
        print("="*72 + "\n")


# ─── HTML Report ─────────────────────────────────────────────────────────────

def build_html_report(rows: list[dict], bm: dict, state: dict, weekly: bool = False) -> str:
    init_date   = state.get("init_date", "?")
    days        = (date.today() - date.fromisoformat(init_date)).days
    total_value = sum(r.get("current_value", r["allocation"]) for r in rows)
    total_pnl   = total_value - TOTAL_CAPITAL
    total_pct   = total_pnl / TOTAL_CAPITAL * 100
    alpha       = total_pct - bm["pnl_pct"]
    snaps       = sorted(state.get("snapshots", []), key=lambda x: x["date"])
    moves       = state.get("trade_log", [])

    color = "#22c55e" if total_pnl >= 0 else "#ef4444"
    bm_color = "#22c55e" if bm["pnl_pct"] >= 0 else "#ef4444"
    alpha_color = "#22c55e" if alpha >= 0 else "#ef4444"

    def pnl_color(v):
        return "#22c55e" if v >= 0 else "#ef4444"

    rows_html = ""
    for r in rows:
        status_display = r["status"].upper()
        if r["type"] == "limit" and r["status"] == "pending":
            cur   = r.get("current_price") or 0
            limit = r.get("limit_price", 0)
            gap   = (cur - limit) / cur * 100 if cur else 0
            status_display = f"PENDING<br><small style='color:#94a3b8'>needs -{gap:.1f}% to ${limit:.2f}</small>"

        pnl_disp = f"${r['pnl_dollars']:+,.2f}" if r["pnl_dollars"] != 0 else "—"
        pct_disp = f"{r['pnl_pct']:+.2f}%" if r["pnl_pct"] != 0 else "—"
        pc = pnl_color(r["pnl_pct"])

        rows_html += f"""
        <tr>
          <td style='padding:10px 12px;font-weight:700;color:#e2e8f0'>{r['ticker']}</td>
          <td style='padding:10px 12px;color:#94a3b8'>{r['name']}</td>
          <td style='padding:10px 12px;color:#94a3b8;font-size:12px'>{status_display}</td>
          <td style='padding:10px 12px;color:#94a3b8;text-align:right'>${r['allocation']:,.0f}</td>
          <td style='padding:10px 12px;color:{pc};font-weight:700;text-align:right'>{pnl_disp}</td>
          <td style='padding:10px 12px;color:{pc};font-weight:700;text-align:right'>{pct_disp}</td>
        </tr>"""

    # Equity curve table rows
    curve_html = ""
    if snaps:
        curve_rows = ""
        for s in snaps:
            a = s["portfolio_pnl"] - s["benchmark_pnl"]
            ac = "#22c55e" if a >= 0 else "#ef4444"
            pc2 = "#22c55e" if s["portfolio_pnl"] >= 0 else "#ef4444"
            bc = "#22c55e" if s["benchmark_pnl"] >= 0 else "#ef4444"
            curve_rows += f"""
            <tr>
              <td style='padding:8px 12px;color:#94a3b8'>{s['date']}</td>
              <td style='padding:8px 12px;color:{pc2};font-weight:700;text-align:right'>{s['portfolio_pnl']:+.2f}%</td>
              <td style='padding:8px 12px;color:{bc};text-align:right'>{s['benchmark_pnl']:+.2f}%</td>
              <td style='padding:8px 12px;color:{ac};font-weight:700;text-align:right'>{a:+.2f}%</td>
            </tr>"""

        curve_html = f"""
        <h3 style='color:#e2e8f0;margin:28px 0 12px'>Daily Equity Curve</h3>
        <table width='100%' style='border-collapse:collapse;background:#1e293b;border-radius:8px;overflow:hidden'>
          <thead>
            <tr style='background:#0f172a'>
              <th style='padding:10px 12px;color:#64748b;text-align:left;font-size:12px'>DATE</th>
              <th style='padding:10px 12px;color:#64748b;text-align:right;font-size:12px'>PORTFOLIO</th>
              <th style='padding:10px 12px;color:#64748b;text-align:right;font-size:12px'>SPY</th>
              <th style='padding:10px 12px;color:#64748b;text-align:right;font-size:12px'>ALPHA</th>
            </tr>
          </thead>
          <tbody>{curve_rows}</tbody>
        </table>"""

    # Position details for weekly report
    detail_html = ""
    if weekly:
        for r in rows:
            if r["type"] == "cash":
                continue
            ep = f"${r['entry_price']:.2f}" if r.get("entry_price") else f"Limit: ${r.get('limit_price', 0):.2f} (not triggered)"
            cp = f"${r['current_price']:.2f}" if r.get("current_price") else "N/A"
            pnl_disp = f"${r['pnl_dollars']:+,.2f} ({r['pnl_pct']:+.2f}%)" if r["pnl_dollars"] != 0 else "No P&L (pending)"
            pc = pnl_color(r["pnl_pct"])
            detail_html += f"""
            <div style='background:#1e293b;border-radius:8px;padding:16px;margin:10px 0;border-left:3px solid {pc}'>
              <div style='font-weight:700;color:#e2e8f0;font-size:15px'>{r['ticker']} — {r['name']}</div>
              <div style='color:#94a3b8;font-size:13px;margin-top:4px'>Signal: {r['signal']}  |  Score: {r['confidence']}  |  Win Rate: {r['win_rate']}%</div>
              <div style='color:#94a3b8;font-size:13px;margin-top:4px'>Entry: {ep}  →  Current: {cp}</div>
              <div style='color:{pc};font-weight:700;font-size:14px;margin-top:6px'>P&L: {pnl_disp}</div>
              <div style='color:#64748b;font-size:12px;margin-top:6px;font-style:italic'>{r['rationale']}</div>
            </div>"""

    move_html = ""
    if moves:
        move_cards = ""
        for m in moves[-8:]:
            ts = (m.get("timestamp", "") or "")[:19].replace("T", " ")
            action = m.get("action", "MOVE")
            ticker = m.get("ticker", "?")
            explanation = m.get("explanation", "")
            move_cards += f"""
            <div style='background:#1e293b;border-radius:8px;padding:12px;margin:10px 0;border-left:3px solid #60a5fa'>
              <div style='font-weight:700;color:#e2e8f0'>{action} — {ticker}</div>
              <div style='color:#94a3b8;font-size:12px;margin-top:4px'>{ts}</div>
              <div style='color:#cbd5e1;font-size:13px;margin-top:8px'>{explanation}</div>
            </div>"""
        move_html = f"""
        <h3 style='color:#e2e8f0;margin:28px 0 12px'>Recent Paper Trade Moves</h3>
        {move_cards}
        """

    title = "Weekly Review" if weekly else "Daily Status"
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Portfolio Simulation {title}</title></head>
<body style='background:#0f172a;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;margin:0;padding:20px'>
<div style='max-width:640px;margin:0 auto'>

  <h2 style='color:#60a5fa;margin-bottom:4px'>Portfolio Simulation — {title}</h2>
  <p style='color:#64748b;margin-top:0;font-size:13px'>Started {init_date} &nbsp;·&nbsp; Day {days} &nbsp;·&nbsp; {date.today().isoformat()}</p>

  <div style='display:flex;gap:12px;margin:20px 0;flex-wrap:wrap'>
    <div style='flex:1;min-width:140px;background:#1e293b;border-radius:8px;padding:16px;border-top:3px solid {color}'>
      <div style='color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:1px'>Portfolio P&L</div>
      <div style='font-size:26px;font-weight:700;color:{color}'>{total_pct:+.2f}%</div>
      <div style='color:{color};font-size:14px'>${total_pnl:+,.2f}</div>
    </div>
    <div style='flex:1;min-width:140px;background:#1e293b;border-radius:8px;padding:16px;border-top:3px solid {bm_color}'>
      <div style='color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:1px'>SPY Benchmark</div>
      <div style='font-size:26px;font-weight:700;color:{bm_color}'>{bm['pnl_pct']:+.2f}%</div>
      <div style='color:{bm_color};font-size:14px'>${bm['pnl_dollars']:+,.0f} (if 100% SPY)</div>
    </div>
    <div style='flex:1;min-width:140px;background:#1e293b;border-radius:8px;padding:16px;border-top:3px solid {alpha_color}'>
      <div style='color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:1px'>Alpha vs SPY</div>
      <div style='font-size:26px;font-weight:700;color:{alpha_color}'>{alpha:+.2f}%</div>
      <div style='color:{alpha_color};font-size:14px'>{'Outperforming' if alpha >= 0 else 'Underperforming'}</div>
    </div>
  </div>

  <h3 style='color:#e2e8f0;margin:28px 0 12px'>Position Breakdown</h3>
  <table width='100%' style='border-collapse:collapse;background:#1e293b;border-radius:8px;overflow:hidden'>
    <thead>
      <tr style='background:#0f172a'>
        <th style='padding:10px 12px;color:#64748b;text-align:left;font-size:12px'>TICKER</th>
        <th style='padding:10px 12px;color:#64748b;text-align:left;font-size:12px'>NAME</th>
        <th style='padding:10px 12px;color:#64748b;text-align:left;font-size:12px'>STATUS</th>
        <th style='padding:10px 12px;color:#64748b;text-align:right;font-size:12px'>ALLOCATED</th>
        <th style='padding:10px 12px;color:#64748b;text-align:right;font-size:12px'>P&L $</th>
        <th style='padding:10px 12px;color:#64748b;text-align:right;font-size:12px'>P&L %</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
    <tfoot>
      <tr style='background:#0f172a;border-top:1px solid #334155'>
        <td colspan='3' style='padding:12px;color:#e2e8f0;font-weight:700'>TOTAL</td>
        <td style='padding:12px;color:#e2e8f0;font-weight:700;text-align:right'>${TOTAL_CAPITAL:,.0f}</td>
        <td style='padding:12px;color:{color};font-weight:700;text-align:right'>${total_pnl:+,.2f}</td>
        <td style='padding:12px;color:{color};font-weight:700;text-align:right'>{total_pct:+.2f}%</td>
      </tr>
    </tfoot>
  </table>

  {curve_html}
  {move_html}
  {detail_html}

  <p style='color:#334155;font-size:11px;margin-top:24px'>
    This is a simulated portfolio for educational purposes. Not financial advice.
    Signals generated by the Investment Daily strategy engine on 2026-04-20.
  </p>
</div></body></html>"""


# ─── Email Sender ─────────────────────────────────────────────────────────────

def send_email(subject: str, html: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = ", ".join(EMAIL_RECIPIENTS)
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())
        logger.info(f"Email sent: {subject}")
    except Exception as e:
        logger.error(f"Email failed: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    run_mock_trading = "--no-trade" not in args

    if "--init" in args:
        state = init_simulation()
        print("Simulation initialized. Run 'python portfolio_sim.py' to check status.")
        return

    state = load_state()
    if not state:
        print("No simulation found. Run 'python portfolio_sim.py --init' first.")
        return

    # Check limit orders + get current prices
    state    = check_limit_orders(state, state["init_date"])
    tickers  = [k for k in state["positions"] if k != "CASH"]
    prices   = get_current_prices(tickers + [state["benchmark"]["ticker"]])
    recs = []

    if run_mock_trading:
        try:
            from strategy_engine import run_full_scan
            signals = run_full_scan()
            recs = evaluate_portfolio(state, prices, signals)
            state, executed = apply_mock_trades(state, recs, prices)
            if executed:
                logger.info(f"Applied {len(executed)} mock trade move(s).")
            state["recommendations"] = [{k: v for k, v in r.items() if k != "exit_cost"} for r in recs]
            state["recommendations_updated"] = datetime.now().isoformat()
            # Refresh price set in case we opened new symbols (e.g., crypto).
            tickers = [k for k in state["positions"] if k != "CASH"]
            prices = get_current_prices(tickers + [state["benchmark"]["ticker"]])
        except Exception as e:
            logger.warning(f"Auto mock-trading skipped: {e}")

    rows = compute_pnl(state, prices)
    bm = compute_benchmark_pnl(state, prices)

    # Always print to console
    print_report(rows, bm, state)

    if "--snapshot" in args or "--email" in args or "--weekly" in args:
        state, rows, bm = take_snapshot(state, recs if recs else None)

    if "--email" in args:
        html = build_html_report(rows, bm, state, weekly=False)
        total_pct = (sum(r.get("current_value", r["allocation"]) for r in rows) - TOTAL_CAPITAL) / TOTAL_CAPITAL * 100
        send_email(
            f"Portfolio Simulation — Day {(date.today() - date.fromisoformat(state['init_date'])).days} | {total_pct:+.2f}% vs SPY {bm['pnl_pct']:+.2f}%",
            html,
        )

    if "--weekly" in args:
        html = build_html_report(rows, bm, state, weekly=True)
        total_pct = (sum(r.get("current_value", r["allocation"]) for r in rows) - TOTAL_CAPITAL) / TOTAL_CAPITAL * 100
        send_email(
            f"Weekly Simulation Review — {total_pct:+.2f}% portfolio vs SPY {bm['pnl_pct']:+.2f}%",
            html,
        )

    save_state(state)


if __name__ == "__main__":
    main()
