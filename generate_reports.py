#!/usr/bin/env python3
"""
Report Generator — Investment Daily
=====================================
Reads current state files and live market data, then writes markdown files
that GitHub renders natively in the browser.

Usage (called by GitHub Actions after each run):
  python generate_reports.py --alerts       # after alert_system.py
  python generate_reports.py --newsletter   # after investment_daily.py
  python generate_reports.py --simulation   # standalone simulation update
  python generate_reports.py               # all three
"""

import os
import sys
import json
from datetime import datetime, date

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(SCRIPT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def _write(filename: str, lines: list) -> None:
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Written: reports/{filename}")

def _pct_arrow(v: float) -> str:
    return "📈" if v > 0 else ("📉" if v < 0 else "➡️")

def _dir_badge(direction: str) -> str:
    return "🟢 BULLISH" if direction == "BULLISH" else "🔴 BEARISH"


# ─── Alerts Report ────────────────────────────────────────────────────────────

def generate_alerts_report() -> None:
    print("Generating reports/ALERTS.md ...")
    from strategy_engine import run_full_scan
    from alert_system import load_state, make_state_key, already_fired_recently

    signals  = run_full_scan()
    state    = load_state()
    now      = datetime.now()

    fired    = [s for s in signals if already_fired_recently(state, make_state_key(s))]
    new_sigs = [s for s in signals if not already_fired_recently(state, make_state_key(s))]
    bullish  = [s for s in signals if s["direction"] == "BULLISH"]
    bearish  = [s for s in signals if s["direction"] == "BEARISH"]

    lines = [
        "# Strategy Alerts",
        f"**Last scan:** {now.strftime('%A %B %d, %Y at %I:%M %p')}",
        "",
        "## Scan Summary",
        "",
        "| | Count |",
        "|---|---|",
        f"| Total signals (confidence ≥ 45) | {len(signals)} |",
        f"| 🟢 Bullish | {len(bullish)} |",
        f"| 🔴 Bearish | {len(bearish)} |",
        f"| ✅ New alerts fired this window | {len(new_sigs)} |",
        f"| ⏸ Suppressed (already sent today) | {len(fired)} |",
        "",
    ]

    if new_sigs:
        lines += [
            "## ✅ New Signals This Window",
            "",
            "| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |",
            "|---|---|---|---|---|---|---|",
        ]
        for s in new_sigs:
            d5  = s.get("backtest", {}).get("5d", {})
            wr  = d5.get("win_rate", "?")
            avg = d5.get("avg_return", "?")
            sh  = d5.get("sharpe", "?")
            lines.append(
                f"| {_dir_badge(s['direction'])} | **{s['ticker']}** | {s['strategy']} "
                f"| {s['confidence']} | {wr}% | {avg}% | {sh} |"
            )
        lines.append("")
    else:
        lines += ["## ✅ New Signals", "", "_No new signals this window — all already sent today._", ""]

    lines += [
        "## All Active Signals",
        "",
        "| Direction | Ticker | Strategy | Confidence | Win Rate | Max Drawdown | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in signals:
        key  = make_state_key(s)
        d5   = s.get("backtest", {}).get("5d", {})
        wr   = d5.get("win_rate", "?")
        dd   = d5.get("max_drawdown", "?")
        stat = "⏸ Suppressed" if already_fired_recently(state, key) else "✅ New"
        lines.append(
            f"| {_dir_badge(s['direction'])} | **{s['ticker']}** | {s['strategy']} "
            f"| {s['confidence']} | {wr}% | {dd}% | {stat} |"
        )

    lines += ["", "---", "*Not financial advice. Backtests use historical data.*"]
    _write("ALERTS.md", lines)


# ─── Simulation Report ────────────────────────────────────────────────────────

def generate_simulation_report() -> None:
    print("Generating reports/SIMULATION.md ...")
    import portfolio_sim as sim

    state = sim.load_state()
    if not state:
        _write("SIMULATION.md", ["# Portfolio Simulation", "", "_Not initialized yet._"])
        return

    tickers = [k for k in state["positions"] if k != "CASH"]
    prices  = sim.get_current_prices(tickers + [state["benchmark"]["ticker"]])
    state   = sim.check_limit_orders(state, state["init_date"])
    rows    = sim.compute_pnl(state, prices)
    bm      = sim.compute_benchmark_pnl(state, prices)

    init_date   = state.get("init_date", "?")
    days        = (date.today() - date.fromisoformat(init_date)).days
    total_value = sum(r.get("current_value", r["allocation"]) for r in rows)
    total_pnl   = total_value - sim.TOTAL_CAPITAL
    total_pct   = total_pnl / sim.TOTAL_CAPITAL * 100
    alpha       = total_pct - bm["pnl_pct"]
    now         = datetime.now()

    lines = [
        f"# Portfolio Simulation {_pct_arrow(total_pnl)}",
        f"**Started:** {init_date} &nbsp;·&nbsp; **Day {days}** &nbsp;·&nbsp; "
        f"Updated: {now.strftime('%b %d %Y %I:%M %p')}",
        "",
        "## Performance Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Portfolio P&L | **{total_pct:+.2f}%** &nbsp; (${total_pnl:+,.0f}) |",
        f"| SPY Benchmark | {bm['pnl_pct']:+.2f}% &nbsp; (${bm['pnl_dollars']:+,.0f} if 100% SPY) |",
        f"| Alpha vs SPY | **{alpha:+.2f}%** &nbsp; {'✅ Outperforming' if alpha >= 0 else '❌ Underperforming'} |",
        f"| Total Capital | ${sim.TOTAL_CAPITAL:,.0f} |",
        f"| Current Value | ${total_value:,.0f} |",
        "",
        "## Position Breakdown",
        "",
        "| Ticker | Name | Status | Allocated | Current Price | P&L $ | P&L % |",
        "|---|---|---|---|---|---|---|",
    ]

    for r in rows:
        status = r["status"].upper()
        if r["type"] == "limit" and r["status"] == "pending":
            cur   = r.get("current_price") or 0
            limit = r.get("limit_price", 0)
            gap   = (cur - limit) / cur * 100 if cur else 0
            status = f"⏳ PENDING (needs -{gap:.1f}% → ${limit:.2f})"
        elif r["status"] == "open":
            status = "✅ OPEN"

        cp_str  = f"${r['current_price']:.2f}" if r.get("current_price") else "—"
        pnl_str = f"${r['pnl_dollars']:+,.0f}" if r["pnl_dollars"] != 0 else "—"
        pct_str = f"{r['pnl_pct']:+.2f}%" if r["pnl_pct"] != 0 else "—"
        lines.append(
            f"| **{r['ticker']}** | {r['name']} | {status} "
            f"| ${r['allocation']:,.0f} | {cp_str} | {pnl_str} | {pct_str} |"
        )

    # Equity curve
    snaps = sorted(state.get("snapshots", []), key=lambda x: x["date"])
    if snaps:
        lines += [
            "",
            "## Daily Equity Curve",
            "",
            "| Date | Portfolio | SPY | Alpha vs SPY |",
            "|---|---|---|---|",
        ]
        for s in snaps:
            a      = s["portfolio_pnl"] - s["benchmark_pnl"]
            p_icon = _pct_arrow(s["portfolio_pnl"])
            a_icon = "✅" if a >= 0 else "❌"
            lines.append(
                f"| {s['date']} | {p_icon} {s['portfolio_pnl']:+.2f}% "
                f"| {s['benchmark_pnl']:+.2f}% | {a_icon} {a:+.2f}% |"
            )

    # Rationale for each position
    lines += ["", "## Position Rationale", ""]
    for r in rows:
        if r["type"] == "cash":
            lines += [
                f"### CASH — ${r['allocation']:,.0f} (62%)",
                f"> {r['rationale']}",
                "",
            ]
        else:
            ep = f"${r['entry_price']:.2f}" if r.get("entry_price") else f"Limit ${r.get('limit_price', 0):.2f} (not yet triggered)"
            lines += [
                f"### {r['ticker']} — {r['name']}",
                f"**Signal:** {r.get('signal','')} &nbsp; **Confidence:** {r.get('confidence','')} "
                f"&nbsp; **Win Rate:** {r.get('win_rate','')}% &nbsp; **Entry:** {ep}",
                f"> {r['rationale']}",
                "",
            ]

    lines += ["---", "*Simulated portfolio for educational purposes. Not financial advice.*"]
    sim.save_state(state)
    _write("SIMULATION.md", lines)


# ─── Newsletter Report ────────────────────────────────────────────────────────

def generate_newsletter_report() -> None:
    print("Generating reports/NEWSLETTER.md ...")
    from investment_daily import get_market_data, get_news, analyze_sentiment
    from strategy_engine import run_full_scan

    now       = datetime.now()
    market    = get_market_data()
    news      = get_news()
    sentiment = analyze_sentiment(news, market)
    signals   = run_full_scan()

    # Flatten market items and get top movers
    all_items = []
    for items in market.values():
        if isinstance(items, list):
            all_items.extend(items)
    movers = sorted(all_items, key=lambda x: abs(x.get("change_pct", 0)), reverse=True)[:10]

    bullish = [s for s in signals if s["direction"] == "BULLISH"]
    bearish = [s for s in signals if s["direction"] == "BEARISH"]

    lines = [
        f"# Daily Newsletter — {now.strftime('%A, %B %d, %Y')}",
        f"Generated at {now.strftime('%I:%M %p')}",
        "",
        f"## Market Sentiment: {sentiment.get('label', 'Neutral')}",
        "",
        f"**Strategy Signals:** {len(signals)} total &nbsp;·&nbsp; "
        f"🟢 {len(bullish)} Bullish &nbsp;·&nbsp; 🔴 {len(bearish)} Bearish",
        "",
        "## Top Movers",
        "",
        "| Ticker | Name | Price | Change |",
        "|---|---|---|---|",
    ]

    for item in movers:
        chg   = item.get("change_pct", 0)
        icon  = _pct_arrow(chg)
        lines.append(
            f"| **{item.get('ticker','')}** | {item.get('name','')} "
            f"| ${item.get('price', 0):.2f} | {icon} {chg:+.2f}% |"
        )

    lines += [
        "",
        "## Top Strategy Signals",
        "",
        "| Direction | Ticker | Strategy | Confidence | Win Rate |",
        "|---|---|---|---|---|",
    ]
    for s in signals[:12]:
        d5 = s.get("backtest", {}).get("5d", {})
        wr = d5.get("win_rate", "?")
        lines.append(
            f"| {_dir_badge(s['direction'])} | **{s['ticker']}** | {s['strategy']} "
            f"| {s['confidence']} | {wr}% |"
        )

    lines += ["", "## Latest News", ""]
    for item in (news or [])[:10]:
        title  = item.get("title", "").replace("|", "-")
        link   = item.get("link", "")
        source = item.get("source", "")
        lines.append(f"- [{title}]({link}) — *{source}*")

    lines += ["", "---", "*Investment Daily — Not financial advice.*"]
    _write("NEWSLETTER.md", lines)


# ─── README (repo homepage) ───────────────────────────────────────────────────

def update_readme() -> None:
    print("Updating README.md ...")
    import portfolio_sim as sim

    state       = sim.load_state()
    sim_line    = "_Simulation not initialized_"
    alpha_icon  = ""

    if state:
        tickers     = [k for k in state["positions"] if k != "CASH"]
        prices      = sim.get_current_prices(tickers + [state["benchmark"]["ticker"]])
        rows        = sim.compute_pnl(state, prices)
        bm          = sim.compute_benchmark_pnl(state, prices)
        total_value = sum(r.get("current_value", r["allocation"]) for r in rows)
        total_pnl   = total_value - sim.TOTAL_CAPITAL
        total_pct   = total_pnl / sim.TOTAL_CAPITAL * 100
        alpha       = total_pct - bm["pnl_pct"]
        init_date   = state.get("init_date", "?")
        days        = (date.today() - date.fromisoformat(init_date)).days
        alpha_icon  = "✅" if alpha >= 0 else "❌"
        sim_line = (
            f"Day {days} &nbsp;·&nbsp; Portfolio **{total_pct:+.2f}%** "
            f"vs SPY {bm['pnl_pct']:+.2f}% &nbsp;·&nbsp; "
            f"Alpha {alpha_icon} **{alpha:+.2f}%**"
        )

    now = datetime.now()

    readme = f"""# Investment Daily

Automated investment newsletter, intraday strategy alerts, and portfolio simulation.
Powered by GitHub Actions — runs 24/7 with no PC required.

**Last updated:** {now.strftime('%B %d, %Y at %I:%M %p')}

---

## Live Reports

| Report | Description | Link |
|---|---|---|
| Strategy Alerts | Latest signal scan with confidence scores | [View →](reports/ALERTS.md) |
| Newsletter Summary | Daily market overview and top movers | [View →](reports/NEWSLETTER.md) |
| Portfolio Simulation | $194k paper portfolio vs SPY | [View →](reports/SIMULATION.md) |

## Portfolio Simulation

{sim_line}

[Full details with equity curve →](reports/SIMULATION.md)

---

## System

| Component | Schedule |
|---|---|
| Daily Newsletter | 7:30 AM ET every day |
| Strategy Alerts | Every 30 min, Mon–Fri, 9:30 AM – 4:00 PM ET |
| Alert cooldown | Resets daily at 6:00 AM MT |
| Signals tracked | 28 tickers × 9 strategies |

## Docs

- [Architecture & Data Flow](ARCHITECTURE.md)
- [Agent Guide — Change Recipes](AGENT_GUIDE.md)

---
*This repo is auto-updated by GitHub Actions. Reports commit after every run.*
*Not financial advice.*
"""

    with open(os.path.join(SCRIPT_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)
    print("  Updated README.md")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    run_all = not args

    if "--alerts" in args or run_all:
        generate_alerts_report()

    if "--simulation" in args or run_all:
        generate_simulation_report()

    if "--newsletter" in args or run_all:
        generate_newsletter_report()

    update_readme()
    print("Done.")
