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

import json
import os
import sys
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

# A snapshot older than this is treated as stale and ignored in favor of a live re-scan.
_ALERT_SNAPSHOT_MAX_AGE_HOURS = 2.0


def _load_recent_alert_snapshot(max_age_hours: float = _ALERT_SNAPSHOT_MAX_AGE_HOURS) -> dict | None:
    """Read last_scan.json if present and recent enough; return None to trigger fallback."""
    try:
        from alert_system import LAST_SCAN_FILE
    except Exception:
        return None
    if not os.path.exists(LAST_SCAN_FILE):
        return None
    try:
        with open(LAST_SCAN_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"  Skipping snapshot (failed to read {LAST_SCAN_FILE}): {exc}")
        return None
    scan_at = data.get("scan_at_iso")
    try:
        ts = datetime.fromisoformat(scan_at)
    except (TypeError, ValueError):
        return None
    age_hours = (datetime.now().astimezone() - ts.astimezone()).total_seconds() / 3600.0
    if age_hours > max_age_hours:
        print(f"  Snapshot is {age_hours:.1f}h old (>{max_age_hours}h) — falling back to live scan.")
        return None
    return data


def _signal_table(rows: list, header: str, intro: str = "") -> list:
    if not rows:
        return []
    out = [f"## {header}", ""]
    if intro:
        out += [intro, ""]
    out += [
        "| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in rows:
        wr  = s.get("win_rate", "?")
        avg = s.get("avg_return", "?")
        sh  = s.get("sharpe", "?")
        out.append(
            f"| {_dir_badge(s.get('direction', 'BULLISH'))} | **{s.get('ticker', '?')}** | {s.get('strategy', '?')} "
            f"| {s.get('confidence', '?')} | {wr}% | {avg}% | {sh} |"
        )
    out.append("")
    return out


def _format_alerts_report_from_snapshot(snap: dict) -> list:
    """Render ALERTS.md from the per-run breakdown written by alert_system.py."""
    totals = snap.get("totals", {}) or {}
    buckets = snap.get("buckets", {}) or {}
    sms = snap.get("sms", {}) or {}
    thresholds = snap.get("thresholds", {}) or {}
    scan_human = snap.get("scan_human", "")
    crypto_only = snap.get("crypto_only", False)
    early_exit = snap.get("early_exit_reason")
    min_conf = thresholds.get("min_confidence", 50)
    alert_h = thresholds.get("alert_cooldown_hours", 6)

    fired = buckets.get("fired_this_run", [])
    sup_ticker = buckets.get("suppressed_ticker_cooldown", [])
    sup_signal = buckets.get("suppressed_signal_cooldown", [])
    bypassed = buckets.get("bypassed_signal_cooldown", [])
    snoozed = buckets.get("snoozed", [])

    title_suffix = "  _(crypto-only scan)_" if crypto_only else ""
    lines = [
        "# Strategy Alerts",
        f"**Last scan:** {scan_human}{title_suffix}",
        "",
        "## Scan Summary",
        "",
        "| | Count |",
        "|---|---|",
        f"| Total signals scanned (confidence ≥ {min_conf:g}) | {totals.get('above_threshold', 0)} |",
        f"| 🟢 Bullish | {totals.get('bullish', 0)} |",
        f"| 🔴 Bearish | {totals.get('bearish', 0)} |",
        f"| ✅ Fired this run (SMS + email) | {totals.get('fired_this_run', 0)} |",
        f"| ⏭ Skipped — same ticker notified in last {alert_h}h | {totals.get('suppressed_ticker_cooldown', 0)} |",
        f"| ⏸ Suppressed — same signal already fired in last {alert_h}h | {totals.get('suppressed_signal_cooldown', 0)} |",
        f"| 🚀 Bypassed cooldown (large price move) | {totals.get('bypassed_signal_cooldown', 0)} |",
        f"| 😴 Snoozed by strategy/ticker | {totals.get('snoozed', 0)} |",
        f"| ⚠ Tickers with conflicting BULL+BEAR signals | {len(snap.get('conflicts') or {})} |",
        "",
    ]

    if early_exit:
        lines += [f"_Run ended early: **{early_exit}** — no email or SMS dispatched._", ""]

    if sms.get("sent"):
        tickers_sent = sms.get("tickers_sent") or [sms.get("top_ticker", "—")]
        sent_count = sms.get("sent_count", len(tickers_sent))
        skipped = sms.get("tickers_skipped_cooldown") or []
        over_cap = sms.get("tickers_over_cap") or []
        sms_lines = [
            f"## 📲 SMS sent ({sent_count})",
            "",
            f"- One text per ticker: **{', '.join(tickers_sent)}**",
        ]
        if skipped:
            sms_lines.append(
                f"- Skipped — per-ticker cooldown: **{', '.join(skipped)}**"
            )
        if over_cap:
            sms_lines.append(
                f"- Skipped — over per-scan cap: **{', '.join(over_cap)}** "
                f"(visible on dashboard)"
            )
        if sms.get("conflicted"):
            sms_lines.append(
                f"- ⚠ **Headline ticker was contested** — opposing-side "
                f"top score **{sms.get('conflict_opposing_top_score', '?')}** "
                f"({sms.get('conflict_opposing_count', '?')} {sms.get('conflict_opposing_dir', '?')} signals)."
            )
        sms_lines.append("")
        lines += sms_lines
    elif sms.get("reason"):
        lines += [
            "## 📲 SMS not sent",
            "",
            f"_Reason: `{sms['reason']}`_",
            "",
        ]

    conflicts = snap.get("conflicts") or {}
    if conflicts:
        cthr = snap.get("conflict_threshold", 65)
        lines += [
            f"## ⚠ Conflicting tickers (both directions ≥ {cthr:g})",
            "",
            "Tickers where bullish *and* bearish strategies are firing above the conflict threshold "
            "at the same time. Treat the headline as one input only.",
            "",
            "| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |",
            "|---|---|---:|---:|---|---:|---:|",
        ]
        for ticker in sorted(
            conflicts.keys(),
            key=lambda t: max(
                float(conflicts[t].get("bull_max") or 0),
                float(conflicts[t].get("bear_max") or 0),
            ),
            reverse=True,
        ):
            info = conflicts[ticker]
            lines.append(
                f"| **{ticker}** "
                f"| {info.get('bull_top_strategy', '?')} | {info.get('bull_max', '?')} | {info.get('bull_count', 0)} "
                f"| {info.get('bear_top_strategy', '?')} | {info.get('bear_max', '?')} | {info.get('bear_count', 0)} |"
            )
        lines.append("")

    lines += _signal_table(
        fired,
        "✅ Fired this run (SMS + email)",
        intro="Signals that **actually triggered** an SMS / email on this run.",
    )
    lines += _signal_table(
        sup_ticker,
        "⏭ Skipped — same ticker already notified",
        intro=f"Above-threshold signals dropped because another strategy on the same ticker fired within the last {alert_h}h ticker-cooldown window.",
    )
    lines += _signal_table(
        sup_signal,
        "⏸ Suppressed — same signal already fired",
        intro=f"The exact ticker + strategy pair fired within the last {alert_h}h, and the price did not move enough to bypass the cooldown.",
    )
    lines += _signal_table(
        bypassed,
        "🚀 Bypassed cooldown (large price move)",
        intro="Signal would normally be in cooldown, but the price moved enough since the last alert to re-fire.",
    )
    lines += _signal_table(snoozed, "😴 Snoozed", intro="Strategy or ticker is currently snoozed.")

    lines += ["---", "*Not financial advice. Backtests use historical data.*"]
    return lines


def _format_alerts_report_from_live_scan() -> list:
    """Legacy fallback: re-scan the market when no fresh snapshot is available.

    Without the per-run buckets we can only tell whether each signal is currently in
    `state["fired"]` — we cannot distinguish "fired this run" from "fired earlier today"
    or from "ticker-cooldown suppressed". The labels below reflect that limitation.
    """
    from strategy_engine import run_full_scan
    from alert_system import (
        load_state,
        make_state_key,
        already_fired_recently,
        ALERT_COOLDOWN_HOURS,
    )

    signals  = run_full_scan()
    state    = load_state()
    now      = datetime.now()

    in_cooldown = [s for s in signals if already_fired_recently(state, make_state_key(s))]
    available   = [s for s in signals if not already_fired_recently(state, make_state_key(s))]
    bullish     = [s for s in signals if s["direction"] == "BULLISH"]
    bearish     = [s for s in signals if s["direction"] == "BEARISH"]

    lines = [
        "# Strategy Alerts",
        f"**Last scan:** {now.strftime('%A %B %d, %Y at %I:%M %p')}  _(live re-scan; per-run snapshot unavailable)_",
        "",
        "## Scan Summary",
        "",
        "| | Count |",
        "|---|---|",
        f"| Total signals (confidence ≥ 45) | {len(signals)} |",
        f"| 🟢 Bullish | {len(bullish)} |",
        f"| 🔴 Bearish | {len(bearish)} |",
        f"| 🔵 In cooldown (fired in last {ALERT_COOLDOWN_HOURS}h) | {len(in_cooldown)} |",
        f"| 🟡 Available to fire (not in cooldown) | {len(available)} |",
        "",
        "_Note: without `last_scan.json` we cannot tell which signals fired on the most recent run vs. earlier in the cooldown window. Run `alert_system.py` to refresh the snapshot._",
        "",
    ]

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
        stat = f"🔵 In cooldown (≤{ALERT_COOLDOWN_HOURS}h)" if already_fired_recently(state, key) else "🟡 Available"
        lines.append(
            f"| {_dir_badge(s['direction'])} | **{s['ticker']}** | {s['strategy']} "
            f"| {s['confidence']} | {wr}% | {dd}% | {stat} |"
        )

    lines += ["", "---", "*Not financial advice. Backtests use historical data.*"]
    return lines


def generate_alerts_report() -> None:
    print("Generating reports/ALERTS.md ...")
    snapshot = _load_recent_alert_snapshot()
    if snapshot is not None:
        print(f"  Using snapshot from {snapshot.get('scan_human', '?')}.")
        lines = _format_alerts_report_from_snapshot(snapshot)
    else:
        lines = _format_alerts_report_from_live_scan()
    _write("ALERTS.md", lines)


# ─── Simulation Report ────────────────────────────────────────────────────────

def generate_simulation_report() -> None:
    print("Generating reports/SIMULATION.md ...")
    import portfolio_sim as sim
    from strategy_engine import run_full_scan

    state = sim.load_state()
    if not state:
        _write("SIMULATION.md", ["# Portfolio Simulation", "", "_Not initialized yet._"])
        return

    tickers = [k for k in state["positions"] if k != "CASH"]
    prices  = sim.get_current_prices(tickers + [state["benchmark"]["ticker"]])
    state   = sim.check_limit_orders(state, state["init_date"])
    rows    = sim.compute_pnl(state, prices)
    bm      = sim.compute_benchmark_pnl(state, prices)

    # ── Run live signal scan and evaluate the portfolio ───────────────────────
    print("  Running strategy scan for portfolio evaluation...")
    signals = run_full_scan()
    recs    = sim.evaluate_portfolio(state, prices, signals)
    # Persist recommendations (without large exit_cost dicts) into state
    state["recommendations"] = [
        {k: v for k, v in r.items() if k != "exit_cost"}
        for r in recs
    ]
    state["recommendations_updated"] = datetime.now().isoformat()
    sim.save_state(state)

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

    # ── Strategy Advisor section ──────────────────────────────────────────────
    if recs:
        action_labels = {
            "HOLD":            "✅ HOLD",
            "HOLD_LIMIT":      "✅ HOLD LIMIT",
            "REVIEW_EXIT":     "⚠️ REVIEW EXIT",
            "CANCEL_LIMIT":    "⚠️ CANCEL LIMIT",
            "NEW_OPPORTUNITY": "🔍 NEW OPPORTUNITY",
        }
        priority_labels = {"high": "🔴 HIGH", "medium": "🟡 MEDIUM", "low": "🟢 LOW"}

        lines += [
            "",
            "## Strategy Advisor",
            "",
            f"_Evaluated {now.strftime('%b %d %Y %I:%M %p')} · "
            f"Tax rates: {int(sim.TAX_SHORT_TERM_RATE*100)}% short-term / "
            f"{int(sim.TAX_LONG_TERM_RATE*100)}% long-term · "
            f"Slippage: {sim.SLIPPAGE_RATE*100:.1f}% per trade_",
            "",
            "| Priority | Action | Ticker | Summary |",
            "|---|---|---|---|",
        ]
        for r in recs:
            action_lbl   = action_labels.get(r["action"], r["action"])
            priority_lbl = priority_labels.get(r["priority"], r["priority"])
            # Keep table rows short; truncate reason at ~90 chars
            summary = r["reason"][:90] + "…" if len(r["reason"]) > 90 else r["reason"]
            lines.append(
                f"| {priority_lbl} | {action_lbl} | **{r['ticker']}** | {summary} |"
            )

        lines += [""]
        for r in recs:
            action_lbl = action_labels.get(r["action"], r["action"])
            lines += [
                f"### {action_lbl} — {r['ticker']}",
                "",
                f"**Signal Analysis:** {r['reason']}",
                "",
                f"**Tax & Cost:** {r['tax_note']}",
                "",
            ]

    # Rationale for each position
    lines += ["## Position Rationale", ""]
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
    _write("SIMULATION.md", lines)


# ─── Newsletter Report ────────────────────────────────────────────────────────

def generate_newsletter_report() -> None:
    print("Generating reports/NEWSLETTER.md ...")
    from investment_daily import get_market_data, get_news, analyze_sentiment
    from strategy_engine import run_full_scan

    now       = datetime.now()
    market    = get_market_data()
    news      = get_news()
    sentiment = analyze_sentiment(market)
    signals   = run_full_scan()

    # Flatten market items and get top movers
    # get_market_data() returns Dict[str, Dict[str, Dict]] — category → {display_name → {symbol, price, change, pct_change}}
    all_items = []
    for cat_dict in market.values():
        for name, d in cat_dict.items():
            all_items.append({**d, "name": name})
    movers = sorted(all_items, key=lambda x: abs(x.get("pct_change", 0)), reverse=True)[:10]

    bullish = [s for s in signals if s["direction"] == "BULLISH"]
    bearish = [s for s in signals if s["direction"] == "BEARISH"]

    lines = [
        f"# Daily Newsletter — {now.strftime('%A, %B %d, %Y')}",
        f"Generated at {now.strftime('%I:%M %p')}",
        "",
        f"## Market Sentiment: {sentiment.get('overall', 'Neutral').capitalize()}",
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
        chg   = item.get("pct_change", 0)
        icon  = _pct_arrow(chg)
        lines.append(
            f"| **{item.get('symbol','')}** | {item.get('name','')} "
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
    from alert_system import ALERT_COOLDOWN_HOURS
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
| Alert cooldown | Same ticker+strategy: at most once per {ALERT_COOLDOWN_HOURS} hours |
| Signals tracked | 28 tickers × 30 strategy detectors |

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
