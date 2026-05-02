#!/usr/bin/env python3
"""
Investment Daily — Mobile Web Dashboard
Access from your phone browser on the same WiFi:  http://<your-PC-IP>:5050
Access from anywhere via ngrok tunnel (see start_dashboard.ps1).

Routes:
  GET  /              Home — sentiment, top signals, quick actions
  GET  /signals       Full strategy signal list
  GET  /simulation    Portfolio paper-trade simulation vs SPY (portfolio_sim)
  GET  /market        Full market snapshot
  GET  /logs          Recent log lines
  POST /run/newsletter  Trigger manual newsletter send
  POST /run/alerts      Trigger manual alert check
  POST /refresh         Force-refresh cached data
  GET  /api/status    JSON health check
"""

import json
import os
import re
import subprocess
import threading
import time
import logging
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, send_from_directory, Response
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

app = Flask(__name__)
log = logging.getLogger("dashboard")


@app.after_request
def add_local_cors_headers(response):
    """Allow the local hub page to read dashboard API status."""
    allowed_origins = {"http://127.0.0.1:5051", "http://localhost:5051"}
    request_origin = request.headers.get("Origin")
    if request_origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = request_origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5051"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# ─── Simple in-memory cache ───────────────────────────────────────────────────

_cache: dict = {
    "market":    None,
    "signals":   None,
    "sentiment": None,
    "positioning": None,
    "positioning_diag": None,
    "fetched_at": None,
    "loading":   False,
}
CACHE_TTL_MINUTES = 30   # auto-refresh data every 30 min


def cache_age_str() -> str:
    if not _cache["fetched_at"]:
        return "never"
    delta = datetime.now() - _cache["fetched_at"]
    mins  = int(delta.total_seconds() / 60)
    if mins < 1:
        return "just now"
    return f"{mins} min ago"


def refresh_cache(force: bool = False) -> None:
    """Pull fresh market data + strategy signals into the cache."""
    if _cache["loading"]:
        return
    if not force and _cache["fetched_at"]:
        age = (datetime.now() - _cache["fetched_at"]).total_seconds() / 60
        if age < CACHE_TTL_MINUTES:
            return

    _cache["loading"] = True
    try:
        from investment_daily import get_market_data, analyze_sentiment
        from positioning_data import get_cot_positioning_summary
        from strategy_engine import run_full_scan, positioning_overlay_diagnostics

        log.info("Dashboard: refreshing market data + signals ...")
        market    = get_market_data()
        sentiment = analyze_sentiment(market)
        signals   = run_full_scan()
        positioning = get_cot_positioning_summary()

        _cache["market"]    = market
        _cache["sentiment"] = sentiment
        _cache["signals"]   = signals
        _cache["positioning"] = positioning
        _cache["positioning_diag"] = positioning_overlay_diagnostics(signals)
        _cache["fetched_at"] = datetime.now()
        log.info(f"Dashboard: cache refreshed — {len(signals)} signals")
    except Exception as exc:
        log.error(f"Dashboard cache refresh error: {exc}")
    finally:
        _cache["loading"] = False


def bg_refresh() -> None:
    """Background thread that keeps the cache warm."""
    while True:
        refresh_cache()
        time.sleep(CACHE_TTL_MINUTES * 60)


def _safe_float(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def compute_macro_tilt_snapshot() -> dict:
    """
    Leadership concentration model:
      - Trigger: RSP/SPY < SMA30 and SMA30 slope down
      - Confirm: SPY near 20d high while ratio at 20d low
      - Leadership: at least 2/3 of NVDA, ORCL, PLTR above SMA30
      - De-risk: ratio > SMA30 for 3 straight sessions
    """
    out = {
        "ok": False,
        "message": "",
        "ratio": None,
        "ratio_sma30": None,
        "sma30_slope_down": False,
        "trigger_on": False,
        "spy_near_20d_high": False,
        "ratio_20d_low": False,
        "confirmation_on": False,
        "leaders_above_sma30": 0,
        "leaders_total": 3,
        "leadership_on": False,
        "riskoff_flip": False,
        "tilt_pct": 0,
        "tilt_label": "No tilt",
        "leaders": {},
        "as_of": None,
    }
    try:
        px = yf.download(
            ["RSP", "SPY", "NVDA", "ORCL", "PLTR"],
            period="9mo",
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="ticker",
            threads=False,
        )
        if px is None or px.empty:
            out["message"] = "No price data returned."
            return out

        close = pd.DataFrame({
            "RSP": px["RSP"]["Close"],
            "SPY": px["SPY"]["Close"],
            "NVDA": px["NVDA"]["Close"],
            "ORCL": px["ORCL"]["Close"],
            "PLTR": px["PLTR"]["Close"],
        }).dropna(how="all")
        if len(close) < 40:
            out["message"] = "Insufficient history for SMA30 model."
            return out

        ratio = (close["RSP"] / close["SPY"]).dropna()
        if len(ratio) < 35:
            out["message"] = "Insufficient RSP/SPY ratio history."
            return out
        ratio_sma30 = ratio.rolling(30).mean()

        r_now = _safe_float(ratio.iloc[-1], None)
        rs_now = _safe_float(ratio_sma30.iloc[-1], None)
        if r_now is None or rs_now is None:
            out["message"] = "Unable to compute current ratio/SMA30."
            return out
        slope_down = bool(ratio_sma30.iloc[-1] < ratio_sma30.iloc[-2])
        trigger_on = bool(r_now < rs_now and slope_down)

        spy = close["SPY"].dropna()
        spy_20h = spy.rolling(20).max().iloc[-1]
        spy_near_20d_high = bool(spy.iloc[-1] >= spy_20h * 0.98)
        ratio_20d_low = bool(r_now <= ratio.tail(20).min())
        confirmation_on = bool(spy_near_20d_high and ratio_20d_low)

        leaders = {}
        leaders_above = 0
        for t in ("NVDA", "ORCL", "PLTR"):
            s = close[t].dropna()
            sma30 = s.rolling(30).mean()
            if len(s) < 35 or pd.isna(sma30.iloc[-1]):
                leaders[t] = {"above_sma30": False}
                continue
            above = bool(s.iloc[-1] > sma30.iloc[-1])
            leaders[t] = {"above_sma30": above}
            if above:
                leaders_above += 1
        leadership_on = leaders_above >= 2

        riskoff_flip = bool((ratio.tail(3) > ratio_sma30.tail(3)).all())

        tilt_pct = 0
        if trigger_on:
            tilt_pct += 10
            if confirmation_on:
                tilt_pct += 5
            if leadership_on:
                tilt_pct += 5
        tilt_pct = min(20, tilt_pct)
        if riskoff_flip:
            tilt_pct = 0

        if tilt_pct >= 20:
            tilt_label = "Max concentration tilt"
        elif tilt_pct > 0:
            tilt_label = "Partial concentration tilt"
        else:
            tilt_label = "Neutral / broad exposure"

        out.update(
            {
                "ok": True,
                "ratio": r_now,
                "ratio_sma30": rs_now,
                "sma30_slope_down": slope_down,
                "trigger_on": trigger_on,
                "spy_near_20d_high": spy_near_20d_high,
                "ratio_20d_low": ratio_20d_low,
                "confirmation_on": confirmation_on,
                "leaders_above_sma30": leaders_above,
                "leadership_on": leadership_on,
                "riskoff_flip": riskoff_flip,
                "tilt_pct": tilt_pct,
                "tilt_label": tilt_label,
                "leaders": leaders,
                "as_of": str(ratio.index[-1].date()) if hasattr(ratio.index[-1], "date") else str(ratio.index[-1]),
            }
        )
        return out
    except Exception as exc:
        out["message"] = f"Macro tilt calc failed: {exc}"
        return out


BEGINNER_STRATEGY_GUIDE = {
    "RSI Oversold": (
        "RSI measures momentum. 'Oversold' means price has fallen fast and may be stretched down.",
        "This can signal a bounce setup, but only if price stabilizes and volume confirms.",
    ),
    "RSI Overbought": (
        "RSI measures momentum. 'Overbought' means price has run up quickly and may be stretched up.",
        "This can warn of pullback risk if momentum starts fading.",
    ),
    "MACD Bullish Crossover": (
        "MACD compares short and medium trend momentum. Bullish crossover means momentum is improving.",
        "Often used as an early trend continuation signal when price also holds key moving averages.",
    ),
    "MACD Bearish Crossover": (
        "MACD bearish crossover means short-term momentum is weakening versus the recent trend.",
        "Often an early warning to reduce risk or tighten stops.",
    ),
    "Golden Cross": (
        "Golden Cross is when the 50-day moving average rises above the 200-day moving average.",
        "This is a long-term trend-strength signal many institutions watch.",
    ),
    "Death Cross": (
        "Death Cross is when the 50-day moving average falls below the 200-day moving average.",
        "This warns that long-term trend structure is weakening.",
    ),
    "SMA 30 — Bullish Reclaim": (
        "Price moved back above its 30-day average, a medium-term trend line.",
        "This can mark a trend reset if price can stay above that level.",
    ),
    "SMA 30 — Bearish Loss": (
        "Price fell below its 30-day average, a medium-term trend line.",
        "This is often a risk-management warning before bigger trend breaks.",
    ),
    "EMA 9/21 — Bullish Cross": (
        "The fast average (9 EMA) crossed above the slower average (21 EMA).",
        "This suggests short-term momentum is accelerating upward.",
    ),
    "EMA 9/21 — Bearish Cross": (
        "The fast average (9 EMA) crossed below the slower average (21 EMA).",
        "This suggests short-term momentum is weakening.",
    ),
}


def _beginner_explainer_for_strategy(strategy_name: str) -> tuple[str, str]:
    if strategy_name in BEGINNER_STRATEGY_GUIDE:
        return BEGINNER_STRATEGY_GUIDE[strategy_name]

    s = (strategy_name or "").lower()
    if "breakout" in s:
        return (
            "A breakout means price moved above a recent range or high.",
            "Breakouts can start strong trends when volume and follow-through are present.",
        )
    if "bollinger" in s:
        return (
            "Bollinger Bands show how far price is from its recent average volatility range.",
            "Touches can signal either mean-reversion opportunities or strong trend extension.",
        )
    if "vwap" in s:
        return (
            "VWAP is the average traded price weighted by volume.",
            "Trading above VWAP often means buyers are controlling the session; below means sellers.",
        )
    if "adx" in s:
        return (
            "ADX measures trend strength, not direction.",
            "Higher ADX means trend conditions are stronger and pullbacks can be shallower.",
        )
    if "stoch" in s:
        return (
            "Stochastic-style indicators compare current price to its recent range.",
            "Extremes can mark momentum turning points when confirmed by price action.",
        )
    if "atr" in s or "ulcer" in s:
        return (
            "This is a volatility or drawdown stress signal.",
            "Use it to size positions smaller when market movement risk is elevated.",
        )
    return (
        "This is a rule-based technical signal from the strategy engine.",
        "Use it with trend context, risk limits, and confirmation instead of trading it in isolation.",
    )

# ─── Shared HTML shell ────────────────────────────────────────────────────────

def shell(title: str, body: str, active: str = "") -> str:
    ticker_options = ""
    ticker_pairs: dict[str, str] = {}
    for s in (_cache.get("signals") or []):
        t = str(s.get("ticker", "")).strip()
        n = str(s.get("name", t)).strip()
        if t and t not in ticker_pairs:
            ticker_pairs[t] = n
    for t in sorted(ticker_pairs.keys()):
        ticker_options += f'<option value="{t}">{t} - {ticker_pairs[t]}</option>'

    nav_items = [
        ("Home",    "/",             "home"),
        ("Chart",   "/chart",        "chart"),
        ("Alerts",  "/alerts",       "alerts"),
        ("Signals", "/signals",      "signals"),
        ("Sim",     "/simulation",   "simulation"),
        ("Market",  "/market",       "market"),
        ("Logs",    "/logs",         "logs"),
    ]
    nav_html = ""
    for label, href, key in nav_items:
        active_style = "background:#6366f1;color:#fff;" if key == active else "color:#94a3b8;"
        nav_html += (
            f'<a href="{href}" style="flex:1;text-align:center;padding:10px 4px;'
            f'font-size:12px;font-weight:700;text-decoration:none;'
            f'border-radius:8px;{active_style}">{label}</a>'
        )

    age  = cache_age_str()
    spin = ' <span style="animation:spin 1s linear infinite;display:inline-block">⟳</span>' if _cache["loading"] else ""

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#020617">
<title>{title} — Investment Daily</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#020617;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
       padding-bottom:80px;font-size:15px}}
  .card{{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;margin:12px 14px}}
  .badge{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700}}
  .btn{{display:block;width:100%;padding:14px;border-radius:10px;border:none;font-size:15px;
        font-weight:700;cursor:pointer;text-align:center;text-decoration:none;margin-bottom:10px}}
  .btn-primary{{background:#6366f1;color:#fff}}
  .btn-green{{background:#166534;color:#4ade80}}
  .btn-red{{background:#7f1d1d;color:#f87171}}
  .btn-gray{{background:#1e293b;color:#94a3b8}}
  .metric{{text-align:center;padding:10px 6px}}
  .metric-val{{font-size:22px;font-weight:900}}
  .metric-lbl{{font-size:10px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-top:2px}}
  table{{width:100%;border-collapse:collapse}}
  td,th{{padding:8px 10px;font-size:12px}}
  th{{color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;font-size:10px}}
  tr{{border-bottom:1px solid #0f172a}}
  h2{{font-size:16px;font-weight:700;color:#f1f5f9;margin-bottom:12px}}
  h3{{font-size:13px;font-weight:700;color:#94a3b8;text-transform:uppercase;
      letter-spacing:1px;margin-bottom:8px}}
  .tag-up{{color:#22c55e;font-weight:700}}
  .tag-dn{{color:#ef4444;font-weight:700}}
  .tag-neu{{color:#f59e0b;font-weight:700}}
  @keyframes spin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
  .toast{{position:fixed;bottom:90px;left:50%;transform:translateX(-50%);
          background:#6366f1;color:#fff;padding:10px 20px;border-radius:20px;
          font-size:13px;font-weight:600;display:none;z-index:999}}
</style>
</head>
<body>
  <!-- Top bar -->
  <div style="background:#0f172a;border-bottom:1px solid #1e293b;
              padding:12px 16px;display:flex;justify-content:space-between;
              align-items:center;position:sticky;top:0;z-index:100">
    <div style="font-size:13px;font-weight:800;color:#818cf8">&#9889; Investment Daily</div>
    <div style="display:flex;align-items:center;gap:8px">
      <select id="globalTickerJump" onchange="goToTickerChart(this.value)"
        style="max-width:180px;padding:6px 8px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:11px">
        <option value="">Chart ticker...</option>
        {ticker_options}
      </select>
      <div style="font-size:11px;color:#475569">Updated {age}{spin}</div>
    </div>
  </div>

  {body}

  <!-- Bottom nav -->
  <div style="position:fixed;bottom:0;left:0;right:0;background:#0f172a;
              border-top:1px solid #1e293b;padding:6px 12px;
              display:flex;gap:4px;z-index:100">
    {nav_html}
  </div>

  <div class="toast" id="toast"></div>

  <script>
  function showToast(msg) {{
    const t = document.getElementById('toast');
    t.textContent = msg; t.style.display = 'block';
    setTimeout(() => t.style.display = 'none', 3000);
  }}
  async function runAction(url, label) {{
    showToast(label + ' started...');
    const r = await fetch(url, {{method:'POST'}});
    const d = await r.json();
    showToast(d.message || 'Done');
  }}
  function goToTickerChart(ticker) {{
    if (!ticker) return;
    window.location.href = '/chart?ticker=' + encodeURIComponent(ticker);
  }}
  </script>
</body></html>"""

# ─── Home page ────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    refresh_cache()
    sentiment = _cache.get("sentiment") or {}
    signals   = _cache.get("signals")   or []
    market    = _cache.get("market")    or {}
    positioning = _cache.get("positioning") or {}
    positioning_diag = _cache.get("positioning_diag") or {}

    overall = sentiment.get("overall", "...")
    score   = sentiment.get("score", 0)
    s_color = {"bullish": "#22c55e", "bearish": "#ef4444", "neutral": "#f59e0b"}.get(overall, "#94a3b8")
    s_bg    = {"bullish": "#0f2d1f", "bearish": "#2d0f0f", "neutral": "#2d200f"}.get(overall, "#1e293b")

    bullish_n  = sum(1 for s in signals if s["direction"] == "BULLISH")
    bearish_n  = sum(1 for s in signals if s["direction"] == "BEARISH")
    macro = compute_macro_tilt_snapshot()

    # Top 5 grouped rows (top rule + runner-up when present)
    from strategy_engine import group_signals_primary_secondary, strategy_learn_link

    groups    = group_signals_primary_secondary(signals)[:5]
    top_rows = ""
    for g in groups:
        s       = g["primary"]
        sec     = g.get("secondary")
        is_bull = s["direction"] == "BULLISH"
        dc      = "#22c55e" if is_bull else "#ef4444"
        arrow   = "▲" if is_bull else "▼"
        conf    = s.get("confidence", 0)
        conf_base = s.get("confidence_base", conf)
        conf_adj = s.get("confidence_adj", 0.0)
        cc      = "#22c55e" if conf >= 65 else ("#f59e0b" if conf >= 52 else "#94a3b8")
        bt      = s.get("backtest", {})
        d5      = bt.get("5d", {})
        wr      = f"{d5['win_rate']:.0f}%" if d5 else "—"
        n_sub   = ""
        if d5 and d5.get("count") is not None:
            n_sub = f'<span style="font-size:9px;color:#475569"> · n={d5["count"]}</span>'
        sub     = ""
        if sec:
            sub = (
                f'<div style="font-size:10px;color:#475569;margin-top:3px">'
                f'Runner-up: {sec["strategy"]} ({sec.get("confidence", 0):.0f})</div>'
            )
        reg_l = ""
        if s.get("regime"):
            reg_l = f'<div style="font-size:9px;color:#475569;margin-top:2px">{s["regime"]}</div>'
        agree_l = ""
        if g.get("agreement_count", 1) > 1:
            agree_l = (
                f'<div style="font-size:9px;color:#a78bfa;margin-top:2px">'
                f'{g["agreement_count"]} rules agree</div>'
            )
        adj_l = ""
        if abs(conf_adj) > 0:
            adj_c = "#22c55e" if conf_adj > 0 else "#ef4444"
            adj_sign = "+" if conf_adj > 0 else ""
            adj_l = (
                f'<div style="font-size:9px;color:{adj_c};margin-top:2px">'
                f'base {conf_base:.0f} {adj_sign}{conf_adj:.0f}</div>'
            )
        learn_badge = strategy_learn_link(s.get("strategy", ""), style="badge")
        strat_html = (
            f'<div style="font-size:11px;color:#64748b">{s["strategy"]}</div>'
            + (f'<div style="margin-top:4px">{learn_badge}</div>' if learn_badge else "")
        )
        search_blob = " ".join(
            [
                str(s.get("ticker", "")),
                str(s.get("name", "")),
                str(s.get("strategy", "")),
                str(s.get("direction", "")),
                str(sec.get("strategy", "")) if sec else "",
            ]
        ).lower().replace('"', "&quot;")
        top_rows += (
            f'<tr class="home-signal-row" data-search="{search_blob}">'
            f'<td style="color:{dc};font-size:16px">{arrow}</td>'
            f'<td><div style="font-weight:700;color:#e2e8f0"><a href="/chart?ticker={s["ticker"]}" '
            f'style="color:#e2e8f0;text-decoration:none">{s["ticker"]}</a></div>'
            f'{strat_html}{reg_l}{agree_l}{sub}</td>'
            f'<td style="text-align:right;color:{cc};font-weight:700;font-size:16px">{conf:.0f}{adj_l}</td>'
            f'<td style="text-align:right;color:#94a3b8">{wr}{n_sub}</td>'
            f'</tr>'
        )

    # Quick index snapshot
    indices  = market.get("Major Indices", {})
    idx_html = ""
    for name, d in list(indices.items())[:4]:
        pct   = d.get("pct_change", 0)
        pc    = "#22c55e" if pct >= 0 else "#ef4444"
        arrow = "▲" if pct >= 0 else "▼"
        short = name.replace(" (Fear Index)", "").replace("Dow Jones", "Dow")
        idx_html += (
            f'<div class="metric">'
            f'<div class="metric-val" style="color:{pc}">{arrow}{abs(pct):.1f}%</div>'
            f'<div class="metric-lbl">{short}</div>'
            f'</div>'
        )

    # Positioning summary card
    p_status = positioning.get("status", "unavailable")
    p_regime = positioning.get("regime", "Unknown")
    p_as_of = positioning.get("report_as_of", "")
    p_items = positioning.get("items", []) or []
    if p_status == "ok" and p_items:
        p_rows = ""
        for item in p_items[:4]:
            side = item.get("crowded_side", "flat")
            crowd = item.get("crowding", "unknown")
            net_oi = item.get("net_pct_open_interest")
            tone = "#22c55e" if side == "long" else ("#ef4444" if side == "short" else "#94a3b8")
            metric = "n/a" if net_oi is None else f"{net_oi:+.1f}% OI"
            p_rows += (
                f'<tr>'
                f'<td style="color:#e2e8f0">{item.get("proxy", "")}</td>'
                f'<td style="color:{tone};text-transform:uppercase;font-weight:700">{side}</td>'
                f'<td style="color:#94a3b8;text-transform:uppercase">{crowd}</td>'
                f'<td style="text-align:right;color:#64748b">{metric}</td>'
                f"</tr>"
            )
        positioning_block = f"""
    <div class="card">
      <h2>Positioning Regime</h2>
      <div style="font-size:12px;color:#94a3b8;margin-bottom:8px">{p_regime}</div>
      <div style="font-size:11px;color:#475569;margin-bottom:10px">CFTC COT {'· as of ' + p_as_of if p_as_of else ''}</div>
      <table>
        <tr style="border-bottom:1px solid #1e293b">
          <th>Proxy</th><th>Net side</th><th>Crowding</th><th style="text-align:right">Net/OI</th>
        </tr>
        {p_rows}
      </table>
    </div>"""
    else:
        positioning_block = """
    <div class="card">
      <h2>Positioning Regime</h2>
      <div style="font-size:12px;color:#94a3b8">COT data unavailable. System will retry on next refresh.</div>
    </div>"""

    # Positioning overlay diagnostics card
    d_total = int(positioning_diag.get("total", len(signals) or 0))
    d_adj = int(positioning_diag.get("adjusted", 0))
    d_boost = int(positioning_diag.get("boosted", 0))
    d_pen = int(positioning_diag.get("penalized", 0))
    d_rate = f"{(100.0 * d_adj / d_total):.1f}%" if d_total else "0.0%"
    d_rows = ""
    by_ticker = positioning_diag.get("by_ticker") or {}
    top_diag = sorted(by_ticker.items(), key=lambda kv: kv[1].get("adjusted", 0), reverse=True)[:5]
    for ticker, vals in top_diag:
        d_rows += (
            f'<tr style="border-bottom:1px solid #0f172a">'
            f'<td style="padding:6px 10px;color:#e2e8f0">{ticker}</td>'
            f'<td style="padding:6px 10px;color:#94a3b8;text-align:right">{vals.get("adjusted", 0)}</td>'
            f'<td style="padding:6px 10px;color:#22c55e;text-align:right">{vals.get("boosted", 0)}</td>'
            f'<td style="padding:6px 10px;color:#ef4444;text-align:right">{vals.get("penalized", 0)}</td>'
            f"</tr>"
        )
    diag_block = f"""
    <div class="card">
      <h2>Overlay Diagnostics</h2>
      <div style="font-size:12px;color:#94a3b8;margin-bottom:8px">
        Positioning overlay adjusted <span style="color:#e2e8f0;font-weight:700">{d_adj}/{d_total}</span> signals ({d_rate})
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:10px">
        <div style="background:#0a0f1e;border-radius:8px;padding:8px;text-align:center">
          <div style="font-size:16px;font-weight:800;color:#94a3b8">{d_adj}</div>
          <div style="font-size:10px;color:#475569">Adjusted</div>
        </div>
        <div style="background:#0a0f1e;border-radius:8px;padding:8px;text-align:center">
          <div style="font-size:16px;font-weight:800;color:#22c55e">{d_boost}</div>
          <div style="font-size:10px;color:#475569">Boosted</div>
        </div>
        <div style="background:#0a0f1e;border-radius:8px;padding:8px;text-align:center">
          <div style="font-size:16px;font-weight:800;color:#ef4444">{d_pen}</div>
          <div style="font-size:10px;color:#475569">Penalized</div>
        </div>
      </div>
      {f'''
      <table>
        <tr style="border-bottom:1px solid #1e293b">
          <th>Ticker</th><th style="text-align:right">Adj</th><th style="text-align:right">+</th><th style="text-align:right">-</th>
        </tr>
        {d_rows}
      </table>''' if d_rows else '<div style="font-size:11px;color:#64748b">No active adjustments this run.</div>'}
    </div>"""

    if macro.get("ok"):
        tilt_pct = int(macro.get("tilt_pct", 0))
        tilt_c = "#22c55e" if tilt_pct >= 15 else ("#f59e0b" if tilt_pct > 0 else "#94a3b8")
        trg = "ON" if macro.get("trigger_on") else "OFF"
        trg_c = "#22c55e" if macro.get("trigger_on") else "#64748b"
        conf = "ON" if macro.get("confirmation_on") else "OFF"
        conf_c = "#22c55e" if macro.get("confirmation_on") else "#64748b"
        lead = f"{macro.get('leaders_above_sma30', 0)}/{macro.get('leaders_total', 3)}"
        lead_c = "#22c55e" if macro.get("leadership_on") else "#64748b"
        risk = "YES" if macro.get("riskoff_flip") else "NO"
        risk_c = "#ef4444" if macro.get("riskoff_flip") else "#64748b"
        macro_block = f"""
    <div class="card">
      <h2>Macro Tilt (RSP/SPY)</h2>
      <div style="font-size:12px;color:#94a3b8;margin-bottom:8px">
        {macro.get("tilt_label", "Neutral")} · as of {macro.get("as_of", "n/a")}
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:10px">
        <div style="background:#0a0f1e;border-radius:8px;padding:8px;text-align:center">
          <div style="font-size:13px;font-weight:800;color:#e2e8f0">{macro.get("ratio", 0):.4f}</div>
          <div style="font-size:10px;color:#475569">RSP/SPY</div>
        </div>
        <div style="background:#0a0f1e;border-radius:8px;padding:8px;text-align:center">
          <div style="font-size:13px;font-weight:800;color:#e2e8f0">{macro.get("ratio_sma30", 0):.4f}</div>
          <div style="font-size:10px;color:#475569">SMA 30</div>
        </div>
        <div style="background:#0a0f1e;border-radius:8px;padding:8px;text-align:center">
          <div style="font-size:18px;font-weight:900;color:{tilt_c}">{tilt_pct}%</div>
          <div style="font-size:10px;color:#475569">Recommended Tilt</div>
        </div>
      </div>
      <table>
        <tr><td style="color:#94a3b8">Trigger (ratio &lt; SMA30 + slope down)</td><td style="text-align:right;color:{trg_c};font-weight:700">{trg}</td></tr>
        <tr><td style="color:#94a3b8">Confirmation (SPY near 20d high + ratio 20d low)</td><td style="text-align:right;color:{conf_c};font-weight:700">{conf}</td></tr>
        <tr><td style="color:#94a3b8">Leadership above SMA30 (NVDA/ORCL/PLTR)</td><td style="text-align:right;color:{lead_c};font-weight:700">{lead}</td></tr>
        <tr><td style="color:#94a3b8">Risk-off flip (ratio above SMA30 3 days)</td><td style="text-align:right;color:{risk_c};font-weight:700">{risk}</td></tr>
      </table>
      <div style="font-size:11px;color:#64748b;margin-top:8px">
        Rule set: +10% base tilt on trigger, +5% on confirmation, +5% on leadership; capped at 20%.
      </div>
    </div>"""
    else:
        macro_block = f"""
    <div class="card">
      <h2>Macro Tilt (RSP/SPY)</h2>
      <div style="font-size:12px;color:#94a3b8">Unavailable right now: {macro.get("message", "Data fetch error")}</div>
    </div>"""

    # Beginner mode: plain-English strategy explanations for today's active playbook.
    guide_rows = ""
    seen = set()
    shown = 0
    for s in signals:
        strategy_name = str(s.get("strategy", "")).strip()
        if not strategy_name or strategy_name in seen:
            continue
        seen.add(strategy_name)
        what_is, why_matters = _beginner_explainer_for_strategy(strategy_name)
        direction = str(s.get("direction", "")).upper()
        d_color = "#22c55e" if direction == "BULLISH" else "#ef4444"
        guide_rows += (
            f'<div style="background:#0a0f1e;border:1px solid #1e293b;border-radius:8px;padding:10px;margin-bottom:8px">'
            f'<div style="font-size:12px;color:#e2e8f0;font-weight:700">{strategy_name}</div>'
            f'<div style="font-size:10px;color:{d_color};font-weight:700;margin-top:3px">{direction}</div>'
            f'<div style="font-size:12px;color:#94a3b8;margin-top:6px;line-height:1.45"><strong style="color:#cbd5e1">What it is:</strong> {what_is}</div>'
            f'<div style="font-size:12px;color:#94a3b8;margin-top:6px;line-height:1.45"><strong style="color:#cbd5e1">Why it matters:</strong> {why_matters}</div>'
            f'</div>'
        )
        shown += 1
        if shown >= 5:
            break
    if not guide_rows:
        guide_rows = '<div style="font-size:12px;color:#94a3b8">No active signals yet. Tap Refresh to generate today&apos;s strategy list.</div>'
    beginner_block = f"""
    <div class="card">
      <h2>Beginner Mode: Read Today&apos;s Signals</h2>
      <div style="font-size:12px;color:#64748b;margin-bottom:8px">
        Plain-English definitions for the active strategies in this run.
      </div>
      {guide_rows}
      <div style="font-size:11px;color:#64748b">
        Starter rule: never trade a signal without position size, stop level, and invalidation plan.
      </div>
    </div>"""

    body = f"""
    <!-- Sentiment banner -->
    <div style="background:{s_bg};border-bottom:2px solid {s_color}30;
                padding:18px 16px;text-align:center">
      <div style="font-size:11px;color:{s_color};font-weight:700;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:4px">Market Sentiment</div>
      <div style="font-size:32px;font-weight:900;color:{s_color};text-transform:uppercase">
        {overall.upper() if overall else '...'}
      </div>
      <div style="font-size:12px;color:#64748b;margin-top:4px">
        Avg index move: {score:+.2f}%
      </div>
    </div>

    <!-- Index row -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);
                background:#0a0f1e;border-bottom:1px solid #1e293b">
      {idx_html}
    </div>

    {macro_block}
    {beginner_block}

    <!-- Quick actions -->
    <div class="card">
      <h3>Quick Actions</h3>
      <button class="btn btn-green"
        onclick="runAction('/run/newsletter','Newsletter')">
        &#128231; Send Newsletter Now
      </button>
      <button class="btn btn-primary"
        onclick="runAction('/run/alerts','Alert scan')">
        &#128270; Run Strategy Scan &amp; Alert
      </button>
      <button class="btn btn-gray"
        onclick="runAction('/refresh','Refresh')">
        &#8635; Refresh Data
      </button>
      <a href="/alerts" class="btn btn-gray"
        style="text-decoration:none;display:block">
        &#128276; Manage Alerts
      </a>
      <button class="btn btn-gray"
        onclick="runAction('/run/simulation-init','Simulation init')">
        &#9881; Initialize Simulation State
      </button>
      <a href="/simulation" class="btn btn-gray"
        style="text-decoration:none;display:block;margin-bottom:0">
        &#128202; Portfolio simulation (paper vs SPY)
      </a>
    </div>

    <!-- Top signals -->
    <div class="card">
      <h2>Top Signals &nbsp;
        <span style="font-size:12px;color:#64748b;font-weight:400">
          {bullish_n} buy · {bearish_n} sell
        </span>
      </h2>
      <input id="homeSignalSearch" type="text" placeholder="Search top signals (ticker/strategy)..."
        oninput="filterHomeSignals()"
        style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-bottom:10px" />
      <table>
        <tr style="border-bottom:1px solid #1e293b">
          <th></th><th>Asset / Strategy</th>
          <th style="text-align:right">Score</th>
          <th style="text-align:right">5d Win</th>
        </tr>
        {top_rows if top_rows else '<tr><td colspan="4" style="color:#475569;padding:14px">No signals — data loading or market closed</td></tr>'}
      </table>
      <div id="homeSignalEmpty" style="display:none;color:#64748b;font-size:12px;margin-top:8px">
        No top signals match your search.
      </div>
      <a href="/signals" style="display:block;text-align:center;margin-top:12px;
         color:#818cf8;font-size:13px;font-weight:600;text-decoration:none">
        View all {len(signals)} signals &#8594;
      </a>
    </div>

    {positioning_block}
    {diag_block}
    <script>
      function filterHomeSignals() {{
        const q = (document.getElementById('homeSignalSearch')?.value || '').toLowerCase().trim();
        const rows = document.querySelectorAll('.home-signal-row');
        let shown = 0;
        rows.forEach((row) => {{
          const txt = (row.getAttribute('data-search') || '').toLowerCase();
          const ok = !q || txt.includes(q);
          row.style.display = ok ? '' : 'none';
          if (ok) shown += 1;
        }});
        const empty = document.getElementById('homeSignalEmpty');
        if (empty) empty.style.display = shown ? 'none' : 'block';
      }}
    </script>"""

    return shell("Home", body, active="home")

# ─── Signals page ─────────────────────────────────────────────────────────────

@app.route("/signals")
def signals_page():
    refresh_cache()
    from strategy_engine import (
        group_signals_primary_secondary,
        confidence_breakdown,
        holdout_backtest_score,
        strategy_learn_link,
    )

    signals = _cache.get("signals") or []
    groups  = group_signals_primary_secondary(signals)

    rows = ""
    for g in groups:
        s   = g["primary"]
        sec = g.get("secondary")
        is_bull = s["direction"] == "BULLISH"
        dc      = "#22c55e" if is_bull else "#ef4444"
        arrow   = "▲" if is_bull else "▼"
        conf    = s.get("confidence", 0)
        conf_base = s.get("confidence_base", conf)
        conf_adj = s.get("confidence_adj", 0.0)
        cc      = "#22c55e" if conf >= 65 else ("#f59e0b" if conf >= 52 else "#94a3b8")
        bt      = s.get("backtest", {})
        d5      = bt.get("5d", {})
        wr      = f"{d5['win_rate']:.0f}%" if d5 else "—"
        ar      = f"{d5['avg_return']:+.1f}%" if d5 else "—"
        sh      = f"{d5['sharpe']:.2f}" if d5 else "—"
        dd      = f"{d5['max_drawdown']:.1f}%" if d5 else "—"

        reg_html = ""
        if s.get("regime"):
            reg_html = (
                f'<div style="font-size:11px;color:#475569;margin-top:4px">{s["regime"]}</div>'
            )
        agr_html = ""
        if g.get("agreement_count", 1) > 1:
            agr_html = (
                f'<div style="font-size:10px;color:#a78bfa;margin-top:4px;font-weight:600">'
                f'{g["agreement_count"]} rules · same direction</div>'
            )
        bd      = confidence_breakdown(bt)
        bd_html = ""
        if bd:
            wr20 = bd["wr20_pts"] if bd["has_20d"] else 0
            bd_html = (
                f'<div style="font-size:10px;color:#64748b;margin:6px 0;line-height:1.45">'
                f'Pts: 5dWR {bd["wr5_pts"]}+Sh {bd["sharpe_pts"]}+20dWR {wr20}+PF {bd["pf_pts"]} '
                f'· n={bd["n_5d"]}</div>'
            )
        hsc, hn = holdout_backtest_score(bt)
        ho_html = ""
        if hsc is not None and hn:
            hcc = "#22c55e" if hsc >= 65 else ("#f59e0b" if hsc >= 52 else "#94a3b8")
            ho_html = (
                f'<div style="font-size:10px;color:#475569;margin-bottom:4px">'
                f'Recent slice score: <span style="color:{hcc};font-weight:800">{hsc:.0f}</span> '
                f'(n={hn})</div>'
            )
        adj_html = ""
        if abs(conf_adj) > 0:
            adj_c = "#22c55e" if conf_adj > 0 else "#ef4444"
            adj_sign = "+" if conf_adj > 0 else ""
            adj_html = (
                f'<div style="font-size:10px;color:{adj_c};margin-top:2px">'
                f'base {conf_base:.0f} {adj_sign}{conf_adj:.0f} positioning</div>'
            )
        learn_badge = strategy_learn_link(s.get("strategy", ""), style="badge")
        search_blob = " ".join(
            [
                str(s.get("ticker", "")),
                str(s.get("name", "")),
                str(s.get("strategy", "")),
                str(s.get("direction", "")),
                str(s.get("indicator", "")),
                str(s.get("implication", "")),
            ]
        ).lower().replace('"', "&quot;")

        rows += f"""
        <div class="signal-card" data-search="{search_blob}"
             style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                    padding:14px;margin:0 14px 10px">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <div style="font-size:18px;font-weight:800;color:#f1f5f9">
                <span style="color:{dc}">{arrow}</span> <a href="/chart?ticker={s['ticker']}" style="color:#f1f5f9;text-decoration:none">{s['ticker']}</a>
                <span style="font-size:13px;color:#64748b;font-weight:400">({s['name']})</span>
              </div>
              {reg_html}
              {agr_html}
              <div style="font-size:11px;color:#64748b;margin-top:2px">Top rule</div>
              <div style="font-size:12px;color:#818cf8;margin-top:3px">{s['strategy']}</div>
              {f'<div style="margin-top:6px">{learn_badge}</div>' if learn_badge else ''}
            </div>
            <div style="text-align:right">
              <div style="font-size:24px;font-weight:900;color:{cc}">{conf:.0f}</div>
              <div style="font-size:10px;color:#475569">backtest score</div>
              {adj_html}
            </div>
          </div>
          {(
            f'<div style="font-size:11px;color:#64748b;background:#0a1628;border-radius:8px;'
            f'padding:8px 10px;margin:8px 0;border:1px solid #1e293b">'
            f'<span style="color:#475569;font-weight:700">Runner-up · </span>'
            f'{sec["strategy"]} · <span style="color:#94a3b8;font-weight:700">'
            f'{sec.get("confidence", 0):.0f}</span></div>'
          ) if sec else ''}
          {bd_html}
          {ho_html}
          <div style="font-family:monospace;font-size:11px;color:#6366f1;
                      background:#0a0f1e;padding:6px 8px;border-radius:6px;margin:8px 0">
            {s.get('indicator','')}
          </div>
          <div style="font-size:12px;color:#94a3b8;line-height:1.5;margin-bottom:8px">
            {s.get('implication','')}
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px">
            <div style="background:#0a0f1e;border-radius:6px;padding:6px;text-align:center">
              <div style="font-size:13px;font-weight:700;color:#94a3b8">{wr}</div>
              <div style="font-size:9px;color:#475569">win rate</div>
            </div>
            <div style="background:#0a0f1e;border-radius:6px;padding:6px;text-align:center">
              <div style="font-size:13px;font-weight:700;color:#94a3b8">{ar}</div>
              <div style="font-size:9px;color:#475569">avg 5d ret</div>
            </div>
            <div style="background:#0a0f1e;border-radius:6px;padding:6px;text-align:center">
              <div style="font-size:13px;font-weight:700;color:#94a3b8">{sh}</div>
              <div style="font-size:9px;color:#475569">Sharpe</div>
            </div>
            <div style="background:#0a0f1e;border-radius:6px;padding:6px;text-align:center">
              <div style="font-size:13px;font-weight:700;color:#ef4444">{dd}</div>
              <div style="font-size:9px;color:#475569">max DD</div>
            </div>
          </div>
        </div>"""

    n_sig = len(signals)
    body = f"""
    <div style="padding:14px 14px 4px">
      <h2>Strategy Signals <span style="color:#64748b;font-weight:400;font-size:14px">({len(groups)} rows · {n_sig} rules)</span></h2>
      <p style="font-size:12px;color:#64748b;margin-bottom:4px">
        Grouped by asset &amp; direction — top rule and runner-up · pandas-ta · 30 detectors
      </p>
      <input id="signalsSearch" type="text" placeholder="Search signals (ticker, strategy, indicator)..."
        oninput="filterSignalsPage()"
        style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-top:8px" />
      <div style="margin-top:8px;font-size:11px;color:#64748b">Tip: click any ticker to open its candle chart.</div>
    </div>
    {rows if rows else '<div class="card" style="color:#64748b">No signals yet — tap Refresh on the home screen.</div>'}
    <div id="signalsEmpty" class="card" style="display:none;color:#64748b">
      No signals match your search.
    </div>
    <script>
      function filterSignalsPage() {{
        const q = (document.getElementById('signalsSearch')?.value || '').toLowerCase().trim();
        const cards = document.querySelectorAll('.signal-card');
        let shown = 0;
        cards.forEach((card) => {{
          const txt = (card.getAttribute('data-search') || '').toLowerCase();
          const ok = !q || txt.includes(q);
          card.style.display = ok ? '' : 'none';
          if (ok) shown += 1;
        }});
        const empty = document.getElementById('signalsEmpty');
        if (empty) empty.style.display = shown ? 'none' : 'block';
      }}
    </script>"""

    return shell("Signals", body, active="signals")

# ─── Market page ──────────────────────────────────────────────────────────────

@app.route("/market")
def market_page():
    refresh_cache()
    market = _cache.get("market") or {}

    sections = ""
    for category, tickers in market.items():
        rows = ""
        for name, d in tickers.items():
            pct   = d.get("pct_change", 0)
            price = d.get("price", 0)
            ticker = d.get("ticker", "")
            pc    = "#22c55e" if pct >= 0 else "#ef4444"
            arrow = "▲" if pct >= 0 else "▼"
            if price > 1000:
                price_s = f"${price:,.2f}"
            elif price > 1:
                price_s = f"${price:.2f}"
            else:
                price_s = f"${price:.4f}"
            search_blob = f"{category} {name} {ticker}".lower().replace('"', "&quot;")
            rows += (
                f'<tr class="market-row" data-search="{search_blob}"><td style="color:#e2e8f0">'
                f'<a href="/chart?ticker={ticker or name}" style="color:#e2e8f0;text-decoration:none">{name}</a>'
                f'<div style="font-size:10px;color:#64748b">{ticker}</div></td>'
                f'<td style="text-align:right;color:#94a3b8">{price_s}</td>'
                f'<td style="text-align:right;color:{pc};font-weight:700">'
                f'{arrow}{abs(pct):.2f}%</td></tr>'
            )
        sections += f"""
        <div class="card market-card" style="padding:0;overflow:hidden">
          <div style="background:#1e293b;padding:10px 14px;font-size:11px;
                      font-weight:700;color:#94a3b8;text-transform:uppercase;
                      letter-spacing:1px">{category}</div>
          <table>
            <tr style="background:#0a0f1e">
              <th style="text-align:left">Asset</th>
              <th style="text-align:right">Price</th>
              <th style="text-align:right">Day %</th>
            </tr>
            {rows}
          </table>
        </div>"""

    body = f"""
    <div style="padding:14px 14px 4px">
      <h2>Live Market Snapshot</h2>
      <p style="font-size:12px;color:#64748b">Updated {cache_age_str()}</p>
      <input id="marketSearch" type="text" placeholder="Search market (name, category, ticker)..."
        oninput="filterMarketPage()"
        style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-top:8px" />
    </div>
    {sections if sections else '<div class="card" style="color:#64748b">Loading market data...</div>'}
    <div id="marketEmpty" class="card" style="display:none;color:#64748b">
      No market rows match your search.
    </div>
    <script>
      function filterMarketPage() {{
        const q = (document.getElementById('marketSearch')?.value || '').toLowerCase().trim();
        const rows = document.querySelectorAll('.market-row');
        let shownRows = 0;
        rows.forEach((row) => {{
          const txt = (row.getAttribute('data-search') || '').toLowerCase();
          const ok = !q || txt.includes(q);
          row.style.display = ok ? '' : 'none';
          if (ok) shownRows += 1;
        }});
        document.querySelectorAll('.market-card').forEach((card) => {{
          const visibleInCard = card.querySelectorAll('.market-row:not([style*="display: none"])').length;
          card.style.display = visibleInCard ? '' : 'none';
        }});
        const empty = document.getElementById('marketEmpty');
        if (empty) empty.style.display = shownRows ? 'none' : 'block';
      }}
    </script>"""

    return shell("Market", body, active="market")


def _default_period_for_interval(interval: str) -> str:
    # yfinance limits very fine intervals to short periods.
    return {
        "1m": "7d",
        "2m": "14d",
        "5m": "30d",
        "15m": "60d",
        "30m": "60d",
        "60m": "730d",
        "1d": "5y",
        "1wk": "10y",
    }.get(interval, "1y")


def _series_json(series: pd.Series) -> list[float | None]:
    out: list[float | None] = []
    for v in series.tolist():
        try:
            fv = float(v)
            if pd.isna(fv):
                out.append(None)
            else:
                out.append(fv)
        except Exception:
            out.append(None)
    return out


@app.route("/chart")
def chart_page():
    refresh_cache()
    signals = _cache.get("signals") or []
    ticker = (request.args.get("ticker") or "BTC-USD").strip().upper()
    options = ""
    seen: dict[str, str] = {}
    for s in signals:
        t = str(s.get("ticker", "")).strip()
        if t and t not in seen:
            seen[t] = str(s.get("name", t))
    for t in sorted(seen.keys()):
        sel = " selected" if t == ticker else ""
        options += f'<option value="{t}"{sel}>{t} - {seen[t]}</option>'

    body = f"""
    <div style="padding:14px 14px 4px">
      <h2>Candle Chart & Indicator Context</h2>
      <p style="font-size:12px;color:#64748b">View multi-timeframe candles and highest-confidence strategy indicators for a ticker.</p>
    </div>
    <div class="card">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <select id="chartTicker" onchange="reloadChartPage()"
          style="padding:10px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:13px">
          <option value="BTC-USD">BTC-USD - Bitcoin</option>
          {options}
        </select>
        <select id="chartInterval" onchange="loadChartData()"
          style="padding:10px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:13px">
          <option value="15m">15m</option>
          <option value="30m">30m</option>
          <option value="60m">1h</option>
          <option value="1d" selected>1D</option>
          <option value="1wk">1W</option>
        </select>
      </div>
      <div id="indicatorToggles" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px"></div>
      <div id="chartStatus" style="font-size:11px;color:#64748b;margin-top:10px">Loading chart...</div>
      <div id="candleChart" style="height:420px;margin-top:8px"></div>
    </div>
    <div class="card">
      <h3>High Confidence Recommended Indicators</h3>
      <div id="indicatorCards" style="font-size:12px;color:#94a3b8">Loading indicators...</div>
    </div>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <script>
      const INDICATOR_OPTIONS = [
        {{ key: 'ema9', label: 'EMA 9', group: 'price' }},
        {{ key: 'ema21', label: 'EMA 21', group: 'price' }},
        {{ key: 'sma20', label: 'SMA 20', group: 'price' }},
        {{ key: 'sma30', label: 'SMA 30', group: 'price' }},
        {{ key: 'sma50', label: 'SMA 50', group: 'price' }},
        {{ key: 'bb_upper', label: 'BB Upper', group: 'price' }},
        {{ key: 'bb_lower', label: 'BB Lower', group: 'price' }},
        {{ key: 'vwap', label: 'VWAP', group: 'price' }},
        {{ key: 'rsi14', label: 'RSI 14', group: 'osc' }},
        {{ key: 'macd', label: 'MACD', group: 'osc' }},
        {{ key: 'macd_signal', label: 'MACD Signal', group: 'osc' }},
        {{ key: 'macd_hist', label: 'MACD Hist', group: 'osc' }},
      ];
      let recommendedKeys = [];

      function strategyToIndicatorKeys(name) {{
        const s = (name || '').toLowerCase();
        if (s.includes('macd')) return ['ema9', 'ema21', 'macd', 'macd_signal', 'macd_hist'];
        if (s.includes('rsi')) return ['rsi14'];
        if (s.includes('bollinger')) return ['sma20', 'bb_upper', 'bb_lower'];
        if (s.includes('vwap')) return ['vwap'];
        if (s.includes('golden cross') || s.includes('death cross')) return ['sma30', 'sma50'];
        if (s.includes('sma 30')) return ['sma30'];
        if (s.includes('sma')) return ['sma20', 'sma30', 'sma50'];
        if (s.includes('ema')) return ['ema9', 'ema21'];
        if (s.includes('breakout') || s.includes('aroon') || s.includes('adx')) return ['ema21', 'sma20'];
        return [];
      }}

      function selectedIndicatorKeys() {{
        return Array.from(document.querySelectorAll('.indicator-check:checked')).map(x => x.value);
      }}

      function renderIndicatorToggles() {{
        const host = document.getElementById('indicatorToggles');
        const defaults = new Set(recommendedKeys.length ? recommendedKeys : ['ema9', 'ema21', 'rsi14']);
        host.innerHTML = INDICATOR_OPTIONS.map(opt => `
          <label style="display:flex;align-items:center;gap:6px;background:#0a0f1e;border:1px solid #1e293b;border-radius:8px;padding:8px 10px;font-size:11px;color:#cbd5e1">
            <input class="indicator-check" type="checkbox" value="${{opt.key}}" ${{defaults.has(opt.key) ? 'checked' : ''}} onchange="loadChartData()" />
            <span>${{opt.label}}</span>
          </label>
        `).join('');
      }}

      async function loadChartData() {{
        const ticker = (document.getElementById('chartTicker').value || '').trim();
        const interval = (document.getElementById('chartInterval').value || '1d').trim();
        const status = document.getElementById('chartStatus');
        status.textContent = 'Loading candles...';
        try {{
          const r = await fetch('/api/candles?ticker=' + encodeURIComponent(ticker) + '&interval=' + encodeURIComponent(interval));
          const d = await r.json();
          if (!d.ok || !d.candles || !d.candles.length) {{
            status.textContent = d.message || 'No candle data returned.';
            document.getElementById('candleChart').innerHTML = '';
            return;
          }}
          const c = d.candles;
          const indicators = d.indicators || {{}};
          const selected = selectedIndicatorKeys();
          const upper = [];
          const lower = [];
          const priceTrace = {{
            x: c.map(x => x.t),
            open: c.map(x => x.o),
            high: c.map(x => x.h),
            low: c.map(x => x.l),
            close: c.map(x => x.c),
            type: 'candlestick',
            increasing: {{line: {{color: '#22c55e'}}}},
            decreasing: {{line: {{color: '#ef4444'}}}},
            name: ticker
          }};
          upper.push(priceTrace);

          function maybeLine(key, color, width=1.3) {{
            if (!selected.includes(key) || !indicators[key]) return;
            upper.push({{
              x: c.map(x => x.t),
              y: indicators[key],
              type: 'scatter',
              mode: 'lines',
              line: {{color: color, width: width}},
              name: key.toUpperCase(),
            }});
          }}
          maybeLine('ema9', '#60a5fa');
          maybeLine('ema21', '#818cf8');
          maybeLine('sma20', '#f59e0b');
          maybeLine('sma30', '#fb7185');
          maybeLine('sma50', '#f97316');
          maybeLine('bb_upper', '#64748b', 1.0);
          maybeLine('bb_lower', '#64748b', 1.0);
          maybeLine('vwap', '#22c55e', 1.2);

          if (selected.includes('rsi14') && indicators.rsi14) {{
            lower.push({{
              x: c.map(x => x.t), y: indicators.rsi14, type: 'scatter', mode: 'lines',
              line: {{color: '#a78bfa', width: 1.2}}, name: 'RSI 14', xaxis: 'x2', yaxis: 'y2'
            }});
          }}
          if (selected.includes('macd') && indicators.macd) {{
            lower.push({{
              x: c.map(x => x.t), y: indicators.macd, type: 'scatter', mode: 'lines',
              line: {{color: '#22c55e', width: 1.1}}, name: 'MACD', xaxis: 'x2', yaxis: 'y2'
            }});
          }}
          if (selected.includes('macd_signal') && indicators.macd_signal) {{
            lower.push({{
              x: c.map(x => x.t), y: indicators.macd_signal, type: 'scatter', mode: 'lines',
              line: {{color: '#ef4444', width: 1.1}}, name: 'MACD Signal', xaxis: 'x2', yaxis: 'y2'
            }});
          }}
          if (selected.includes('macd_hist') && indicators.macd_hist) {{
            lower.push({{
              x: c.map(x => x.t), y: indicators.macd_hist, type: 'bar',
              marker: {{color: '#334155'}}, name: 'MACD Hist', xaxis: 'x2', yaxis: 'y2'
            }});
          }}

          const showLower = lower.length > 0;
          const traces = showLower ? upper.concat(lower) : upper;
          const layout = {{
            paper_bgcolor: '#0f172a',
            plot_bgcolor: '#0f172a',
            font: {{color: '#cbd5e1'}},
            margin: {{l: 36, r: 8, t: 10, b: 30}},
            xaxis: {{gridcolor: '#1e293b', rangeslider: {{visible: false}}, domain: [0, 1], anchor: 'y'}},
            yaxis: {{gridcolor: '#1e293b', domain: showLower ? [0.34, 1.0] : [0, 1]}},
            showlegend: true,
            legend: {{orientation: 'h', y: 1.06, x: 0}}
          }};
          if (showLower) {{
            layout.xaxis2 = {{gridcolor: '#1e293b', domain: [0, 1], anchor: 'y2', matches: 'x'}};
            layout.yaxis2 = {{gridcolor: '#1e293b', domain: [0, 0.26], zerolinecolor: '#334155'}};
          }}
          Plotly.newPlot('candleChart', traces, layout, {{displayModeBar: false, responsive: true}});
          status.textContent = ticker + ' · ' + interval + ' · ' + c.length + ' candles';
        }} catch (e) {{
          status.textContent = 'Chart load failed: ' + e;
          document.getElementById('candleChart').innerHTML = '';
        }}
      }}

      async function loadIndicatorCards() {{
        const ticker = (document.getElementById('chartTicker').value || '').trim();
        const host = document.getElementById('indicatorCards');
        host.textContent = 'Loading indicators...';
        try {{
          const r = await fetch('/api/ticker-signals?ticker=' + encodeURIComponent(ticker));
          const d = await r.json();
          if (!d.ok || !d.signals || !d.signals.length) {{
            host.innerHTML = '<div style="color:#64748b">No high-confidence signals found for this ticker right now.</div>';
            recommendedKeys = ['ema9', 'ema21', 'rsi14'];
            renderIndicatorToggles();
            loadChartData();
            return;
          }}
          const rec = new Set();
          d.signals.forEach(s => strategyToIndicatorKeys(s.strategy).forEach(k => rec.add(k)));
          recommendedKeys = Array.from(rec);
          renderIndicatorToggles();
          host.innerHTML = d.signals.map(s => {{
            const col = s.direction === 'BULLISH' ? '#22c55e' : '#ef4444';
            return `
              <div style="background:#0a0f1e;border:1px solid #1e293b;border-radius:8px;padding:10px;margin-bottom:8px">
                <div style="font-size:12px;color:${{col}};font-weight:700">${{s.direction}} · ${{s.strategy}} · score ${{s.confidence}}</div>
                ${{s.learn_html ? `<div style="margin-top:6px">${{s.learn_html}}</div>` : ''}}
                <div style="font-size:12px;color:#818cf8;margin-top:6px;font-family:monospace">${{s.indicator || ''}}</div>
                <div style="font-size:12px;color:#94a3b8;margin-top:6px;line-height:1.45">${{s.implication || ''}}</div>
              </div>
            `;
          }}).join('');
          loadChartData();
        }} catch (e) {{
          host.innerHTML = '<div style="color:#fca5a5">Failed to load indicator cards: ' + e + '</div>';
          recommendedKeys = ['ema9', 'ema21', 'rsi14'];
          renderIndicatorToggles();
          loadChartData();
        }}
      }}

      function reloadChartPage() {{
        const ticker = (document.getElementById('chartTicker').value || '').trim();
        window.location.href = '/chart?ticker=' + encodeURIComponent(ticker);
      }}

      renderIndicatorToggles();
      loadIndicatorCards();
    </script>
    """
    return shell("Chart", body, active="chart")


@app.route("/api/candles")
def api_candles():
    ticker = (request.args.get("ticker") or "").strip().upper()
    interval = (request.args.get("interval") or "1d").strip()
    if not ticker:
        return jsonify({"ok": False, "message": "Ticker is required."}), 400

    allowed = {"1m", "2m", "5m", "15m", "30m", "60m", "1d", "1wk"}
    if interval not in allowed:
        return jsonify({"ok": False, "message": "Unsupported interval."}), 400

    period = _default_period_for_interval(interval)
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
        if df is None or df.empty:
            return jsonify({"ok": False, "message": f"No candle data for {ticker} ({interval}).", "candles": []})
        df = df.tail(600).copy()
        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        vol = df["Volume"].fillna(0)

        sma20 = close.rolling(20).mean()
        sma30 = close.rolling(30).mean()
        sma50 = close.rolling(50).mean()
        ema9 = close.ewm(span=9, adjust=False).mean()
        ema21 = close.ewm(span=21, adjust=False).mean()
        std20 = close.rolling(20).std()
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20
        tp = (high + low + close) / 3.0
        cum_vol = vol.cumsum().replace(0, pd.NA)
        vwap = (tp * vol).cumsum() / cum_vol

        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta.clip(upper=0))
        avg_gain = gain.ewm(alpha=(1 / 14), adjust=False, min_periods=14).mean()
        avg_loss = loss.ewm(alpha=(1 / 14), adjust=False, min_periods=14).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi14 = 100 - (100 / (1 + rs))

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - macd_signal

        rows = []
        for idx, row in df.iterrows():
            rows.append(
                {
                    "t": idx.isoformat() if hasattr(idx, "isoformat") else str(idx),
                    "o": float(row.get("Open", 0.0)),
                    "h": float(row.get("High", 0.0)),
                    "l": float(row.get("Low", 0.0)),
                    "c": float(row.get("Close", 0.0)),
                    "v": float(row.get("Volume", 0.0)),
                }
            )
        indicators = {
            "sma20": _series_json(sma20),
            "sma30": _series_json(sma30),
            "sma50": _series_json(sma50),
            "ema9": _series_json(ema9),
            "ema21": _series_json(ema21),
            "bb_upper": _series_json(bb_upper),
            "bb_lower": _series_json(bb_lower),
            "vwap": _series_json(vwap),
            "rsi14": _series_json(rsi14),
            "macd": _series_json(macd),
            "macd_signal": _series_json(macd_signal),
            "macd_hist": _series_json(macd_hist),
        }
        return jsonify(
            {
                "ok": True,
                "ticker": ticker,
                "interval": interval,
                "period": period,
                "candles": rows,
                "indicators": indicators,
            }
        )
    except Exception as exc:
        return jsonify({"ok": False, "message": f"Candle fetch failed: {exc}", "candles": []}), 500


@app.route("/api/ticker-signals")
def api_ticker_signals():
    refresh_cache()
    from strategy_engine import strategy_learn_link
    ticker = (request.args.get("ticker") or "").strip().upper()
    if not ticker:
        return jsonify({"ok": False, "message": "Ticker is required.", "signals": []}), 400
    all_signals = [s for s in (_cache.get("signals") or []) if str(s.get("ticker", "")).upper() == ticker]
    if not all_signals:
        return jsonify({"ok": True, "ticker": ticker, "signals": []})
    top = sorted(all_signals, key=lambda s: float(s.get("confidence", 0.0)), reverse=True)[:8]
    recommended = [
        {
            "strategy": s.get("strategy", ""),
            "direction": s.get("direction", ""),
            "confidence": round(float(s.get("confidence", 0.0)), 1),
            "indicator": s.get("indicator", ""),
            "implication": s.get("implication", ""),
            "learn_html": strategy_learn_link(s.get("strategy", ""), style="badge"),
        }
        for s in top
        if float(s.get("confidence", 0.0)) >= 60
    ]
    if not recommended:
        recommended = [
            {
                "strategy": s.get("strategy", ""),
                "direction": s.get("direction", ""),
                "confidence": round(float(s.get("confidence", 0.0)), 1),
                "indicator": s.get("indicator", ""),
                "implication": s.get("implication", ""),
                "learn_html": strategy_learn_link(s.get("strategy", ""), style="badge"),
            }
            for s in top[:3]
        ]
    return jsonify({"ok": True, "ticker": ticker, "signals": recommended})


@app.route("/api/macro-tilt")
def api_macro_tilt():
    snap = compute_macro_tilt_snapshot()
    return jsonify(snap), (200 if snap.get("ok") else 503)

# ─── Logs page ────────────────────────────────────────────────────────────────

@app.route("/logs")
def logs_page():
    log_files = {
        "Newsletter": os.path.join(SCRIPT_DIR, "logs", "investment_daily.log"),
        "Alerts":     os.path.join(SCRIPT_DIR, "logs", "alert_system.log"),
        "Dashboard":  os.path.join(SCRIPT_DIR, "logs", "dashboard.log"),
    }
    sections = ""
    for label, path in log_files.items():
        if not os.path.exists(path):
            content = "No log file yet."
        else:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            last = lines[-40:] if len(lines) > 40 else lines
            content = "".join(reversed(last)).strip() or "(empty)"

        sections += f"""
        <div class="card">
          <h3>{label} Log</h3>
          <pre style="font-size:10px;color:#64748b;overflow-x:auto;
                      white-space:pre-wrap;line-height:1.5;max-height:200px;
                      overflow-y:auto">{content}</pre>
        </div>"""

    body = f"""
    <div style="padding:14px 14px 4px"><h2>System Logs</h2></div>
    {sections}"""

    return shell("Logs", body, active="logs")

# ─── Action endpoints ─────────────────────────────────────────────────────────

def _run_script(script_name: str, args: list[str] | None = None) -> dict:
    """Run a script in a subprocess, return status dict."""
    import sys
    script_path = os.path.join(SCRIPT_DIR, script_name)
    python_exe  = sys.executable
    cmd = [python_exe, script_path] + (args or [])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=300,
            cwd=SCRIPT_DIR,
        )
        ok = result.returncode == 0
        return {
            "ok":      ok,
            "message": "Sent successfully!" if ok else f"Error: {result.stderr[-200:]}",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "message": "Timed out after 5 minutes."}
    except Exception as exc:
        return {"ok": False, "message": str(exc)}


@app.route("/run/newsletter", methods=["POST"])
def run_newsletter():
    def _do():
        _run_script("investment_daily.py")
    threading.Thread(target=_do, daemon=True).start()
    return jsonify({"ok": True, "message": "Newsletter queued — check your email in ~30 seconds!"})


@app.route("/run/alerts", methods=["POST"])
def run_alerts():
    def _do():
        # Force run even outside market hours by patching the check
        from strategy_engine import run_full_scan
        from alert_system import (
            build_alert_email, send_email, load_state,
            save_state, MIN_CONFIDENCE, mark_fired, make_state_key,
        )
        import logging as lg
        lg.info("Dashboard: manual alert scan triggered")
        signals     = run_full_scan()
        new_signals = [s for s in signals if s.get("confidence", 0) >= MIN_CONFIDENCE]
        if new_signals:
            state = load_state()
            dispatch_seq = int(state.get("send_count", 0)) + 1
            state["send_count"] = dispatch_seq
            subject, html = build_alert_email(
                new_signals, signals, dispatch_seq=dispatch_seq
            )
            send_email(subject, html)
            for s in new_signals:
                mark_fired(state, make_state_key(s))
            save_state(state)
    threading.Thread(target=_do, daemon=True).start()
    return jsonify({"ok": True, "message": "Scan running — email on its way if signals found!"})


@app.route("/run/simulation-init", methods=["POST"])
def run_simulation_init():
    def _do():
        r = _run_script("portfolio_sim.py", ["--init"])
        if r.get("ok"):
            # make the new state visible immediately in status checks
            _cache["fetched_at"] = None
        log.info(f"Dashboard: simulation init result => {r.get('message')}")
    threading.Thread(target=_do, daemon=True).start()
    return jsonify({
        "ok": True,
        "message": "Simulation initialization started. Refresh in ~5 seconds.",
    })


@app.route("/refresh", methods=["POST"])
def force_refresh():
    def _do():
        _cache["fetched_at"] = None   # force expiry
        refresh_cache(force=True)
    threading.Thread(target=_do, daemon=True).start()
    return jsonify({"ok": True, "message": "Refreshing data... pull down to reload in 15 sec."})


@app.route("/alerts")
def alerts_page():
    refresh_cache()
    signals = _cache.get("signals") or []
    from strategy_engine import SCAN_TICKERS

    tickers = sorted(set(SCAN_TICKERS.keys()) | {s.get("ticker", "") for s in signals if s.get("ticker")})
    ticker_options = "".join(f'<option value="{t}">{t}</option>' for t in tickers if t)
    strategy_names = sorted({s.get("strategy", "") for s in signals if s.get("strategy")})
    strategy_options = "".join(f'<option value="{name}">{name}</option>' for name in strategy_names)

    strategy_snoozes_html = '<div style="font-size:11px;color:#64748b">No active strategy snoozes.</div>'
    ticker_snoozes_html = '<div style="font-size:11px;color:#64748b">No active ticker snoozes.</div>'
    ticker_cooldowns_rows = ""

    try:
        from alert_system import load_state, prune_state, ALERT_COOLDOWN_HOURS, SMS_COOLDOWN_HOURS
        state = prune_state(load_state())
        now = datetime.now().astimezone()

        strategy_rows = []
        for strategy, until in (state.get("snoozed_strategies") or {}).items():
            try:
                dt = datetime.fromisoformat(until)
                if dt.tzinfo is None:
                    dt = dt.astimezone()
                if dt > now:
                    strategy_rows.append((strategy, dt))
            except Exception:
                continue
        strategy_rows.sort(key=lambda x: x[1])
        if strategy_rows:
            strategy_snoozes_html = "".join(
                f'<div style="padding:7px 10px;border:1px solid #334155;border-radius:8px;background:#0a0f1e;'
                f'color:#94a3b8;font-size:11px;margin-bottom:6px"><span style="color:#e2e8f0;font-weight:700">{name}</span>'
                f' until {dt.strftime("%I:%M %p")}</div>'
                for name, dt in strategy_rows[:10]
            )

        ticker_rows = []
        for ticker, until in (state.get("snoozed_tickers") or {}).items():
            try:
                dt = datetime.fromisoformat(until)
                if dt.tzinfo is None:
                    dt = dt.astimezone()
                if dt > now:
                    ticker_rows.append((ticker, dt))
            except Exception:
                continue
        ticker_rows.sort(key=lambda x: x[1])
        if ticker_rows:
            ticker_snoozes_html = "".join(
                f'<div style="padding:7px 10px;border:1px solid #334155;border-radius:8px;background:#0a0f1e;'
                f'color:#94a3b8;font-size:11px;margin-bottom:6px"><span style="color:#e2e8f0;font-weight:700">{ticker}</span>'
                f' until {dt.strftime("%I:%M %p")}</div>'
                for ticker, dt in ticker_rows[:10]
            )

        overrides = state.get("ticker_cooldowns") or {}
        if isinstance(overrides, dict):
            for ticker in sorted(overrides.keys())[:100]:
                cfg = overrides.get(ticker, {})
                if not isinstance(cfg, dict):
                    continue
                email_h = cfg.get("email_hours")
                sms_h = cfg.get("sms_hours")
                email_show = str(email_h if email_h is not None else ALERT_COOLDOWN_HOURS)
                sms_show = str(sms_h if sms_h is not None else SMS_COOLDOWN_HOURS)
                ticker_cooldowns_rows += (
                    "<tr>"
                    f"<td style='color:#e2e8f0'>{ticker}</td>"
                    f"<td style='text-align:right;color:#94a3b8'>{email_show}</td>"
                    f"<td style='text-align:right;color:#94a3b8'>{sms_show}</td>"
                    "</tr>"
                )
    except Exception as exc:
        ticker_cooldowns_rows = (
            f"<tr><td colspan='3' style='color:#fca5a5'>Failed to load state: {exc}</td></tr>"
        )

    body = f"""
    <div style="padding:14px 14px 4px">
      <h2>Alert Controls</h2>
      <p style="font-size:12px;color:#64748b">Manage strategy/ticker snoozes and per-ticker email/SMS cooldowns.</p>
    </div>

    <div class="card">
      <h3>Snooze By Strategy</h3>
      <select id="strategyName" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;
        background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-bottom:8px">
        <option value="">Select strategy...</option>
        {strategy_options}
      </select>
      <select id="strategyHours" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;
        background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-bottom:10px">
        <option value="1">1 hour</option><option value="2">2 hours</option><option value="4" selected>4 hours</option>
        <option value="8">8 hours</option><option value="12">12 hours</option><option value="24">24 hours</option>
      </select>
      <button class="btn btn-red" onclick="snoozeStrategy()" style="margin-bottom:10px">&#128263; Snooze Strategy</button>
      {strategy_snoozes_html}
    </div>

    <div class="card">
      <h3>Snooze By Ticker</h3>
      <select id="tickerName" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;
        background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-bottom:8px">
        <option value="">Select ticker...</option>
        {ticker_options}
      </select>
      <select id="tickerSnoozeHours" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;
        background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-bottom:10px">
        <option value="1">1 hour</option><option value="2">2 hours</option><option value="4" selected>4 hours</option>
        <option value="8">8 hours</option><option value="12">12 hours</option><option value="24">24 hours</option>
      </select>
      <button class="btn btn-red" onclick="snoozeTicker()" style="margin-bottom:10px">&#128263; Snooze Ticker</button>
      {ticker_snoozes_html}
    </div>

    <div class="card">
      <h3>Per-Ticker Cooldowns</h3>
      <div style="font-size:11px;color:#64748b;margin-bottom:10px">
        Set cooldown hours by ticker and channel. 0 disables cooldown for that channel+ticker.
      </div>
      <select id="cooldownTicker" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;
        background:#0a0f1e;color:#e2e8f0;font-size:13px;margin-bottom:8px">
        <option value="">Select ticker...</option>
        {ticker_options}
      </select>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
        <input id="emailCooldown" type="number" min="0" max="72" step="1" placeholder="Email hours"
          style="padding:10px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:13px" />
        <input id="smsCooldown" type="number" min="0" max="72" step="1" placeholder="SMS hours"
          style="padding:10px;border-radius:8px;border:1px solid #334155;background:#0a0f1e;color:#e2e8f0;font-size:13px" />
      </div>
      <button class="btn btn-primary" onclick="setTickerCooldowns()" style="margin-bottom:8px">&#9881; Save Ticker Cooldowns</button>
      <button class="btn btn-gray" onclick="resetTickerCooldowns()" style="margin-bottom:10px">&#8635; Reset Selected Ticker</button>
      <button class="btn btn-gray" onclick="clearAllAlertMutes()" style="margin-bottom:0">&#9989; Clear All Ticker/Strategy Snoozes</button>
      <div style="margin-top:12px;background:#0a0f1e;border:1px solid #1e293b;border-radius:10px;overflow:hidden">
        <table>
          <tr style="border-bottom:1px solid #1e293b"><th>Ticker</th><th style="text-align:right">Email h</th><th style="text-align:right">SMS h</th></tr>
          {ticker_cooldowns_rows if ticker_cooldowns_rows else "<tr><td colspan='3' style='color:#64748b'>No ticker overrides yet.</td></tr>"}
        </table>
      </div>
    </div>

    <script>
      async function apiPost(url, payload) {{
        const r = await fetch(url, {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify(payload || {{}})
        }});
        return r.json();
      }}
      async function snoozeStrategy() {{
        const strategy = document.getElementById('strategyName').value;
        const hours = parseInt(document.getElementById('strategyHours').value || '0', 10);
        if (!strategy) return showToast('Pick a strategy');
        const d = await apiPost('/alerts/snooze-strategy', {{strategy, hours}});
        showToast(d.message || 'Updated'); if (d.ok) setTimeout(() => window.location.reload(), 700);
      }}
      async function snoozeTicker() {{
        const ticker = document.getElementById('tickerName').value;
        const hours = parseInt(document.getElementById('tickerSnoozeHours').value || '0', 10);
        if (!ticker) return showToast('Pick a ticker');
        const d = await apiPost('/alerts/snooze-ticker', {{ticker, hours}});
        showToast(d.message || 'Updated'); if (d.ok) setTimeout(() => window.location.reload(), 700);
      }}
      async function setTickerCooldowns() {{
        const ticker = document.getElementById('cooldownTicker').value;
        const emailHours = parseFloat(document.getElementById('emailCooldown').value);
        const smsHours = parseFloat(document.getElementById('smsCooldown').value);
        if (!ticker) return showToast('Pick a ticker');
        if (Number.isNaN(emailHours) || Number.isNaN(smsHours)) return showToast('Enter both cooldown values');
        const d = await apiPost('/alerts/set-ticker-cooldown', {{ticker, email_hours: emailHours, sms_hours: smsHours}});
        showToast(d.message || 'Saved'); if (d.ok) setTimeout(() => window.location.reload(), 700);
      }}
      async function resetTickerCooldowns() {{
        const ticker = document.getElementById('cooldownTicker').value;
        if (!ticker) return showToast('Pick a ticker');
        const d = await apiPost('/alerts/reset-ticker-cooldown', {{ticker}});
        showToast(d.message || 'Reset'); if (d.ok) setTimeout(() => window.location.reload(), 700);
      }}
      async function clearAllAlertMutes() {{
        const d = await apiPost('/alerts/clear-snoozes', {{}});
        showToast(d.message || 'Cleared'); if (d.ok) setTimeout(() => window.location.reload(), 700);
      }}
    </script>
    """
    return shell("Alerts", body, active="alerts")


@app.route("/alerts/snooze-strategy", methods=["POST"])
def alerts_snooze_strategy():
    payload = request.get_json(silent=True) or {}
    strategy = str(payload.get("strategy", "")).strip()
    hours_raw = payload.get("hours", 4)
    if not strategy:
        return jsonify({"ok": False, "message": "Strategy is required."}), 400
    try:
        hours = int(hours_raw)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Hours must be an integer."}), 400
    if hours <= 0 or hours > 72:
        return jsonify({"ok": False, "message": "Hours must be between 1 and 72."}), 400

    try:
        from alert_system import load_state, save_state, prune_state
        state = prune_state(load_state())
        snoozed = state.setdefault("snoozed_strategies", {})
        until = datetime.now().astimezone() + timedelta(hours=hours)
        snoozed[strategy] = until.isoformat()
        save_state(state)
    except Exception as exc:
        log.exception("Dashboard: failed to snooze strategy")
        return jsonify({"ok": False, "message": f"Failed to save snooze: {exc}"}), 500

    return jsonify({"ok": True, "message": f"Snoozed '{strategy}' for {hours}h."})


@app.route("/alerts/snooze-ticker", methods=["POST"])
def alerts_snooze_ticker():
    payload = request.get_json(silent=True) or {}
    ticker = str(payload.get("ticker", "")).strip().upper()
    hours_raw = payload.get("hours", 4)
    if not ticker:
        return jsonify({"ok": False, "message": "Ticker is required."}), 400
    try:
        hours = int(hours_raw)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Hours must be an integer."}), 400
    if hours <= 0 or hours > 72:
        return jsonify({"ok": False, "message": "Hours must be between 1 and 72."}), 400

    try:
        from alert_system import load_state, save_state, prune_state
        state = prune_state(load_state())
        snoozed = state.setdefault("snoozed_tickers", {})
        until = datetime.now().astimezone() + timedelta(hours=hours)
        snoozed[ticker] = until.isoformat()
        save_state(state)
    except Exception as exc:
        log.exception("Dashboard: failed to snooze ticker")
        return jsonify({"ok": False, "message": f"Failed to save ticker snooze: {exc}"}), 500

    return jsonify({"ok": True, "message": f"Snoozed '{ticker}' for {hours}h."})


@app.route("/alerts/set-ticker-cooldown", methods=["POST"])
def alerts_set_ticker_cooldown():
    payload = request.get_json(silent=True) or {}
    ticker = str(payload.get("ticker", "")).strip().upper()
    if not ticker:
        return jsonify({"ok": False, "message": "Ticker is required."}), 400
    try:
        email_hours = float(payload.get("email_hours"))
        sms_hours = float(payload.get("sms_hours"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Email and SMS cooldowns must be numbers."}), 400
    if email_hours < 0 or email_hours > 72 or sms_hours < 0 or sms_hours > 72:
        return jsonify({"ok": False, "message": "Cooldowns must be between 0 and 72 hours."}), 400

    try:
        from alert_system import load_state, save_state, prune_state
        state = prune_state(load_state())
        tcfg = state.setdefault("ticker_cooldowns", {})
        tcfg[ticker] = {"email_hours": float(email_hours), "sms_hours": float(sms_hours)}
        save_state(state)
    except Exception as exc:
        log.exception("Dashboard: failed setting ticker cooldown")
        return jsonify({"ok": False, "message": f"Failed to save ticker cooldown: {exc}"}), 500
    return jsonify({"ok": True, "message": f"Saved cooldowns for {ticker}."})


@app.route("/alerts/reset-ticker-cooldown", methods=["POST"])
def alerts_reset_ticker_cooldown():
    payload = request.get_json(silent=True) or {}
    ticker = str(payload.get("ticker", "")).strip().upper()
    if not ticker:
        return jsonify({"ok": False, "message": "Ticker is required."}), 400
    try:
        from alert_system import load_state, save_state, prune_state
        state = prune_state(load_state())
        tcfg = state.setdefault("ticker_cooldowns", {})
        tcfg.pop(ticker, None)
        save_state(state)
    except Exception as exc:
        log.exception("Dashboard: failed resetting ticker cooldown")
        return jsonify({"ok": False, "message": f"Failed to reset ticker cooldown: {exc}"}), 500
    return jsonify({"ok": True, "message": f"Reset cooldowns for {ticker}."})


@app.route("/alerts/clear-snoozes", methods=["POST"])
def alerts_clear_snoozes():
    try:
        from alert_system import load_state, save_state
        state = load_state()
        state["snoozed_strategies"] = {}
        state["snoozed_tickers"] = {}
        save_state(state)
    except Exception as exc:
        log.exception("Dashboard: failed to clear snoozes")
        return jsonify({"ok": False, "message": f"Failed to clear snoozes: {exc}"}), 500
    return jsonify({"ok": True, "message": "All strategy/ticker snoozes cleared."})


@app.route("/api/status")
def api_status():
    signals = _cache.get("signals") or []
    sent    = _cache.get("sentiment") or {}
    diag    = _cache.get("positioning_diag") or {}
    sim_ok  = False
    try:
        p = os.path.join(SCRIPT_DIR, "sim_portfolio.json")
        if os.path.isfile(p) and os.path.getsize(p) > 20:
            with open(p, encoding="utf-8") as f:
                sim_ok = bool(json.load(f).get("positions"))
    except Exception:
        sim_ok = False
    return jsonify({
        "ok":               True,
        "fetched_at":       _cache["fetched_at"].isoformat() if _cache["fetched_at"] else None,
        "loading":          _cache["loading"],
        "signal_count":     len(signals),
        "sentiment":        sent.get("overall", "unknown"),
        "positioning_regime": (_cache.get("positioning") or {}).get("regime", "unknown"),
        "positioning_adjusted_count": int(diag.get("adjusted", 0)),
        "simulation_ready": sim_ok,
    })


@app.route("/simulation")
def simulation_page():
    """
    Live portfolio simulation view (same engine as portfolio_sim.py / reports/SIMULATION.md).
    Uses cached strategy signals when available to avoid a duplicate full scan.
    """
    import portfolio_sim as sim
    from strategy_engine import run_full_scan

    refresh_cache()
    state = sim.load_state()
    if not state:
        body = """
    <div style="padding:16px 14px">
      <h2 style="color:#f1f5f9;margin-bottom:12px">Portfolio simulation</h2>
      <div class="card" style="color:#94a3b8;line-height:1.6">
        <p style="margin:0 0 12px">No simulation state on this server yet.</p>
        <button class="btn btn-primary"
          onclick="runAction('/run/simulation-init','Simulation init')"
          style="margin-bottom:10px">
          &#9881; Initialize simulation now
        </button>
        <p style="margin:0 0 10px;font-size:12px;color:#64748b">This creates
        <code style="color:#818cf8">sim_portfolio.json</code> on the server so this page can render.</p>
        <p style="margin:0;font-size:12px;color:#64748b">Optional: you can still initialize locally with
        <code style="color:#818cf8">python portfolio_sim.py --init</code> and push the file for deterministic deploy state.</p>
      </div>
      <a href="/" style="color:#818cf8;font-weight:700;display:inline-block;margin-top:16px">← Home</a>
    </div>"""
        return shell("Simulation", body, active="simulation")

    try:
        state = sim.check_limit_orders(state, state["init_date"])
        tickers = [k for k in state["positions"] if k != "CASH"]
        prices = sim.get_current_prices(tickers + [state["benchmark"]["ticker"]])
        rows = sim.compute_pnl(state, prices)
        bm = sim.compute_benchmark_pnl(state, prices)

        signals = _cache.get("signals") or []
        if not signals:
            log.info("Dashboard: simulation using fresh full scan (signal cache empty)")
            signals = run_full_scan()

        recs = sim.evaluate_portfolio(state, prices, signals)
        state["recommendations"] = [
            {k: v for k, v in r.items() if k != "exit_cost"}
            for r in recs
        ]
        state["recommendations_updated"] = datetime.now().isoformat()
        sim.save_state(state)

        html_doc = sim.build_html_report(rows, bm, state, weekly=False)
    except Exception as exc:
        log.exception("Simulation page failed")
        body = f"""
    <div style="padding:16px 14px">
      <h2 style="color:#f1f5f9">Portfolio simulation</h2>
      <div class="card" style="color:#fca5a5">{exc}</div>
      <a href="/" style="color:#818cf8;font-weight:700;display:inline-block;margin-top:16px">← Home</a>
    </div>"""
        return shell("Simulation", body, active="simulation")

    bar = (
        '<div style="position:sticky;top:0;z-index:200;background:#0f172a;'
        'border-bottom:1px solid #334155;padding:12px 16px;display:flex;'
        'justify-content:space-between;align-items:center">'
        '<a href="/" style="color:#818cf8;font-weight:800;text-decoration:none;font-size:14px">'
        "&#8592; Dashboard</a>"
        '<span style="color:#64748b;font-size:12px">Paper portfolio &middot; vs SPY</span>'
        "</div>"
    )
    m = re.search(r"<body[^>]*>", html_doc)
    if m:
        html_doc = html_doc[: m.end()] + bar + html_doc[m.end() :]

    return Response(html_doc, mimetype="text/html; charset=utf-8")


@app.route("/hub")
def hub_page():
    """Serve the local tools hub from the dashboard service."""
    return send_from_directory(os.path.join(SCRIPT_DIR, "hub"), "index.html")


@app.route("/asset-opportunities")
def asset_opportunities_page():
    """Serve the standalone asset opportunity finder page."""
    return send_from_directory(os.path.join(SCRIPT_DIR, "hub"), "asset-opportunities.html")

# ─── Start ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import socket

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, "dashboard.log"), encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    # Start background cache warm-up
    t = threading.Thread(target=bg_refresh, daemon=True)
    t.start()

    # Print local network address for phone access
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    port = int(os.getenv("PORT", "5050"))

    print(f"\n{'='*55}")
    print("  Investment Daily Dashboard")
    print(f"{'='*55}")
    print(f"  Local (same WiFi): http://{local_ip}:{port}")
    print(f"  Localhost:         http://127.0.0.1:{port}")
    print(f"  Simulation:        http://127.0.0.1:{port}/simulation")
    print("  For outside WiFi:  run start_dashboard.ps1 (ngrok)")
    print(f"{'='*55}\n")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
