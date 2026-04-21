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
from datetime import datetime, date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import yfinance as yf
import numpy as np
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIR, "portfolio_sim.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

EMAIL_SENDER    = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = "dan.r.custodio@gmail.com"
STATE_FILE      = os.path.join(SCRIPT_DIR, "sim_portfolio.json")

TOTAL_CAPITAL   = 194_000.00
CASH_APY        = 0.045   # ~4.5% annual yield on T-Bills / money market

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

def load_state() -> Dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: Dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def init_simulation() -> Dict:
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

def get_current_prices(tickers: List[str]) -> Dict[str, float]:
    prices = {}
    for t in tickers:
        try:
            hist = yf.Ticker(t).history(period="1d")
            if not hist.empty:
                prices[t] = float(hist["Close"].iloc[-1])
        except Exception as e:
            logger.warning(f"Could not fetch {t}: {e}")
    return prices


def get_price_history_since(ticker: str, since_date: str) -> "pd.DataFrame":
    """Return daily OHLCV since a given date string (YYYY-MM-DD)."""
    import pandas as pd
    try:
        hist = yf.Ticker(ticker).history(start=since_date)
        return hist
    except Exception as e:
        logger.warning(f"History fetch failed for {ticker}: {e}")
        return None


# ─── Limit Order Check ────────────────────────────────────────────────────────

def check_limit_orders(state: Dict, since_date: str) -> Dict:
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

def compute_pnl(state: Dict, current_prices: Dict) -> List[Dict]:
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


def compute_benchmark_pnl(state: Dict, current_prices: Dict) -> Dict:
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

def take_snapshot(state: Dict) -> Dict:
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

    save_state(state)
    logger.info(f"Snapshot saved: portfolio {portfolio_pnl_pct:+.2f}% | SPY {bm['pnl_pct']:+.2f}%")
    return state, rows, bm


# ─── Console Report ──────────────────────────────────────────────────────────

def print_report(rows: List[Dict], bm: Dict, state: Dict) -> None:
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
    pnl_arrow = "+" if total_pnl >= 0 else ""
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


# ─── HTML Report ─────────────────────────────────────────────────────────────

def build_html_report(rows: List[Dict], bm: Dict, state: Dict, weekly: bool = False) -> str:
    init_date   = state.get("init_date", "?")
    days        = (date.today() - date.fromisoformat(init_date)).days
    total_value = sum(r.get("current_value", r["allocation"]) for r in rows)
    total_pnl   = total_value - TOTAL_CAPITAL
    total_pct   = total_pnl / TOTAL_CAPITAL * 100
    alpha       = total_pct - bm["pnl_pct"]
    snaps       = sorted(state.get("snapshots", []), key=lambda x: x["date"])

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
              <div style='color:#94a3b8;font-size:13px;margin-top:4px'>Signal: {r['signal']}  |  Confidence: {r['confidence']}  |  Win Rate: {r['win_rate']}%</div>
              <div style='color:#94a3b8;font-size:13px;margin-top:4px'>Entry: {ep}  →  Current: {cp}</div>
              <div style='color:{pc};font-weight:700;font-size:14px;margin-top:6px'>P&L: {pnl_disp}</div>
              <div style='color:#64748b;font-size:12px;margin-top:6px;font-style:italic'>{r['rationale']}</div>
            </div>"""

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
    msg["To"]      = EMAIL_RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        logger.info(f"Email sent: {subject}")
    except Exception as e:
        logger.error(f"Email failed: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

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
    rows     = compute_pnl(state, prices)
    bm       = compute_benchmark_pnl(state, prices)

    # Always print to console
    print_report(rows, bm, state)

    if "--snapshot" in args or "--email" in args or "--weekly" in args:
        state, rows, bm = take_snapshot(state)

    if "--email" in args:
        html = build_html_report(rows, bm, state, weekly=False)
        total_pct = (sum(r.get("current_value", r["allocation"]) for r in rows) - TOTAL_CAPITAL) / TOTAL_CAPITAL * 100
        arrow = "+" if total_pct >= 0 else ""
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
