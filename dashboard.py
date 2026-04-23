#!/usr/bin/env python3
"""
Investment Daily — Mobile Web Dashboard
Access from your phone browser on the same WiFi:  http://<your-PC-IP>:5050
Access from anywhere via ngrok tunnel (see start_dashboard.ps1).

Routes:
  GET  /              Home — sentiment, top signals, quick actions
  GET  /signals       Full strategy signal list
  GET  /market        Full market snapshot
  GET  /logs          Recent log lines
  POST /run/newsletter  Trigger manual newsletter send
  POST /run/alerts      Trigger manual alert check
  POST /refresh         Force-refresh cached data
  GET  /api/status    JSON health check
"""

import os
import json
import subprocess
import threading
import time
import logging
from datetime import datetime
from functools import lru_cache
from typing import Dict, List

from flask import Flask, jsonify, redirect, render_template_string, request, url_for
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

app = Flask(__name__)
log = logging.getLogger("dashboard")

# ─── Simple in-memory cache ───────────────────────────────────────────────────

_cache: Dict = {
    "market":    None,
    "signals":   None,
    "sentiment": None,
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
        from strategy_engine import run_full_scan

        log.info("Dashboard: refreshing market data + signals ...")
        market    = get_market_data()
        sentiment = analyze_sentiment(market)
        signals   = run_full_scan()

        _cache["market"]    = market
        _cache["sentiment"] = sentiment
        _cache["signals"]   = signals
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

# ─── Shared HTML shell ────────────────────────────────────────────────────────

def shell(title: str, body: str, active: str = "") -> str:
    nav_items = [
        ("Home",    "/",         "home"),
        ("Signals", "/signals",  "signals"),
        ("Market",  "/market",   "market"),
        ("Logs",    "/logs",     "logs"),
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
    <div style="font-size:11px;color:#475569">Updated {age}{spin}</div>
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
  </script>
</body></html>"""

# ─── Home page ────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    refresh_cache()
    sentiment = _cache.get("sentiment") or {}
    signals   = _cache.get("signals")   or []
    market    = _cache.get("market")    or {}

    overall = sentiment.get("overall", "...")
    score   = sentiment.get("score", 0)
    s_color = {"bullish": "#22c55e", "bearish": "#ef4444", "neutral": "#f59e0b"}.get(overall, "#94a3b8")
    s_bg    = {"bullish": "#0f2d1f", "bearish": "#2d0f0f", "neutral": "#2d200f"}.get(overall, "#1e293b")

    bullish_n  = sum(1 for s in signals if s["direction"] == "BULLISH")
    bearish_n  = sum(1 for s in signals if s["direction"] == "BEARISH")

    # Top 5 signals preview
    top_rows = ""
    for s in signals[:5]:
        is_bull = s["direction"] == "BULLISH"
        dc      = "#22c55e" if is_bull else "#ef4444"
        arrow   = "▲" if is_bull else "▼"
        conf    = s.get("confidence", 0)
        cc      = "#22c55e" if conf >= 65 else ("#f59e0b" if conf >= 52 else "#94a3b8")
        bt      = s.get("backtest", {})
        d5      = bt.get("5d", {})
        wr      = f"{d5['win_rate']:.0f}%" if d5 else "—"
        top_rows += (
            f'<tr>'
            f'<td style="color:{dc};font-size:16px">{arrow}</td>'
            f'<td><div style="font-weight:700;color:#e2e8f0">{s["ticker"]}</div>'
            f'<div style="font-size:11px;color:#64748b">{s["strategy"]}</div></td>'
            f'<td style="text-align:right;color:{cc};font-weight:700;font-size:16px">{conf:.0f}</td>'
            f'<td style="text-align:right;color:#94a3b8">{wr}</td>'
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
    </div>

    <!-- Top signals -->
    <div class="card">
      <h2>Top Signals &nbsp;
        <span style="font-size:12px;color:#64748b;font-weight:400">
          {bullish_n} buy · {bearish_n} sell
        </span>
      </h2>
      <table>
        <tr style="border-bottom:1px solid #1e293b">
          <th></th><th>Asset / Strategy</th>
          <th style="text-align:right">Conf</th>
          <th style="text-align:right">5d Win</th>
        </tr>
        {top_rows if top_rows else '<tr><td colspan="4" style="color:#475569;padding:14px">No signals — data loading or market closed</td></tr>'}
      </table>
      <a href="/signals" style="display:block;text-align:center;margin-top:12px;
         color:#818cf8;font-size:13px;font-weight:600;text-decoration:none">
        View all {len(signals)} signals &#8594;
      </a>
    </div>"""

    return shell("Home", body, active="home")

# ─── Signals page ─────────────────────────────────────────────────────────────

@app.route("/signals")
def signals_page():
    refresh_cache()
    signals = _cache.get("signals") or []

    rows = ""
    for s in signals:
        is_bull = s["direction"] == "BULLISH"
        dc      = "#22c55e" if is_bull else "#ef4444"
        arrow   = "▲" if is_bull else "▼"
        conf    = s.get("confidence", 0)
        cc      = "#22c55e" if conf >= 65 else ("#f59e0b" if conf >= 52 else "#94a3b8")
        bt      = s.get("backtest", {})
        d5      = bt.get("5d", {})
        wr      = f"{d5['win_rate']:.0f}%" if d5 else "—"
        ar      = f"{d5['avg_return']:+.1f}%" if d5 else "—"
        sh      = f"{d5['sharpe']:.2f}" if d5 else "—"
        dd      = f"{d5['max_drawdown']:.1f}%" if d5 else "—"

        rows += f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                    padding:14px;margin:0 14px 10px">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <div style="font-size:18px;font-weight:800;color:#f1f5f9">
                <span style="color:{dc}">{arrow}</span> {s['ticker']}
                <span style="font-size:13px;color:#64748b;font-weight:400">({s['name']})</span>
              </div>
              <div style="font-size:12px;color:#818cf8;margin-top:3px">{s['strategy']}</div>
            </div>
            <div style="text-align:right">
              <div style="font-size:24px;font-weight:900;color:{cc}">{conf:.0f}</div>
              <div style="font-size:10px;color:#475569">confidence</div>
            </div>
          </div>
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

    body = f"""
    <div style="padding:14px 14px 4px">
      <h2>Strategy Signals <span style="color:#64748b;font-weight:400;font-size:14px">({len(signals)} total)</span></h2>
      <p style="font-size:12px;color:#64748b;margin-bottom:4px">
        Ranked by confidence · Powered by pandas-ta · 9 strategies · 28 tickers
      </p>
    </div>
    {rows if rows else '<div class="card" style="color:#64748b">No signals yet — tap Refresh on the home screen.</div>'}"""

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
            pc    = "#22c55e" if pct >= 0 else "#ef4444"
            arrow = "▲" if pct >= 0 else "▼"
            if price > 1000:
                price_s = f"${price:,.2f}"
            elif price > 1:
                price_s = f"${price:.2f}"
            else:
                price_s = f"${price:.4f}"
            rows += (
                f'<tr><td style="color:#e2e8f0">{name}</td>'
                f'<td style="text-align:right;color:#94a3b8">{price_s}</td>'
                f'<td style="text-align:right;color:{pc};font-weight:700">'
                f'{arrow}{abs(pct):.2f}%</td></tr>'
            )
        sections += f"""
        <div class="card" style="padding:0;overflow:hidden">
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
    </div>
    {sections if sections else '<div class="card" style="color:#64748b">Loading market data...</div>'}"""

    return shell("Market", body, active="market")

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
            with open(path, "r", encoding="utf-8", errors="replace") as f:
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

def _run_script(script_name: str) -> Dict:
    """Run a script in a subprocess, return status dict."""
    import sys
    script_path = os.path.join(SCRIPT_DIR, script_name)
    python_exe  = sys.executable
    try:
        result = subprocess.run(
            [python_exe, script_path],
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
    return jsonify({"ok": True, "message": f"Scan running — email on its way if signals found!"})


@app.route("/refresh", methods=["POST"])
def force_refresh():
    def _do():
        _cache["fetched_at"] = None   # force expiry
        refresh_cache(force=True)
    threading.Thread(target=_do, daemon=True).start()
    return jsonify({"ok": True, "message": "Refreshing data... pull down to reload in 15 sec."})


@app.route("/api/status")
def api_status():
    signals = _cache.get("signals") or []
    sent    = _cache.get("sentiment") or {}
    return jsonify({
        "ok":          True,
        "fetched_at":  _cache["fetched_at"].isoformat() if _cache["fetched_at"] else None,
        "loading":     _cache["loading"],
        "signal_count": len(signals),
        "sentiment":   sent.get("overall", "unknown"),
    })

# ─── Start ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import socket

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(SCRIPT_DIR, "logs", "dashboard.log"), encoding="utf-8"),
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

    print(f"\n{'='*55}")
    print(f"  Investment Daily Dashboard")
    print(f"{'='*55}")
    print(f"  Local (same WiFi): http://{local_ip}:5050")
    print(f"  Localhost:         http://127.0.0.1:5050")
    print(f"  For outside WiFi:  run start_dashboard.ps1 (ngrok)")
    print(f"{'='*55}\n")

    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
