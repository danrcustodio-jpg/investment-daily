#!/usr/bin/env python3
"""
Intraday Strategy Alert System
Runs every 30 minutes during NYSE market hours (Mon-Fri 9:30 AM – 4:00 PM ET).
Scans all watched tickers for technical strategy signals, backtests each signal
against 2 years of history, then emails ONLY the highest backtest-score setups.
One alert per strategy+ticker combination per 12 hours (no spam).
"""

import os
import json
import smtplib
import logging
import sys
import zoneinfo
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from strategy_engine import (
    DEX_TICKERS,
    SCAN_TICKERS,
    confidence_breakdown,
    fetch_15m_bars,
    format_intraday_15m_alert_html,
    run_full_scan,
    strategy_learn_link,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(SCRIPT_DIR, "logs"), exist_ok=True)
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIR, "logs", "alert_system.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────

EMAIL_SENDER    = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = "dan.r.custodio@gmail.com"
SMS_GATEWAY     = os.getenv("SMS_GATEWAY")   # e.g. 5551234567@vtext.com
# Optional: SMS_ENABLE=0/false to turn off SMS while keeping SMS_GATEWAY in .env
_SMS_EN = (os.getenv("SMS_ENABLE") or "1").strip().lower()
SMS_ENABLED     = _SMS_EN in ("1", "true", "yes", "on", "")
# Min hours between *any* two SMS (carriers often throttle email-to-SMS; 0 = no limit)
def _parse_sms_cooldown() -> float:
    raw = (os.getenv("SMS_COOLDOWN_HOURS") or "1").strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 1.0
SMS_COOLDOWN_HOURS = _parse_sms_cooldown()
SMS_BODY_MAX = 200  # keep single-segment; gateway line length varies

STATE_FILE      = os.path.join(SCRIPT_DIR, "alert_state.json")
ET_ZONE         = zoneinfo.ZoneInfo("America/New_York")
MARKET_OPEN     = (9, 30)
MARKET_CLOSE    = (16, 0)

def _parse_float_env(name: str, default: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        logger.warning(f"Invalid {name}={raw!r}; using default {default}")
        return default
    return max(min_value, min(max_value, value))


def _parse_int_env(name: str, default: int, min_value: int = 0, max_value: int = 72) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        logger.warning(f"Invalid {name}={raw!r}; using default {default}")
        return default
    return max(min_value, min(max_value, value))


# Minimum backtest score (0-100) to send an alert.
# Lowered default to increase alert frequency while still filtering very weak setups.
MIN_CONFIDENCE  = _parse_float_env("ALERT_MIN_CONFIDENCE", 50.0)

# Signals at or above this score get a 15-minute OHLCV + RSI section in alert emails.
HIGH_CONFIDENCE_15M_THRESHOLD = _parse_float_env("ALERT_HIGH_CONFIDENCE_15M", 68.0)
COOLDOWN_BYPASS_MOVE_PCT = _parse_float_env("ALERT_COOLDOWN_BYPASS_MOVE_PCT", 2.0, min_value=0.0, max_value=50.0)
TRACKING_CADENCE_MINUTES = [15, 30, 60, 120, 240, 1440]

# ─── Market Hours ─────────────────────────────────────────────────────────────

def is_market_open() -> bool:
    now = datetime.now(ET_ZONE)
    if now.weekday() >= 5:
        return False
    t = (now.hour, now.minute)
    return MARKET_OPEN <= t < MARKET_CLOSE


def market_status_str() -> str:
    return datetime.now(ET_ZONE).strftime("%I:%M %p ET, %A %b %d")

# ─── State Management ─────────────────────────────────────────────────────────

# Rolling window: same ticker+strategy will not trigger another email within this many hours.
# Lowered default to increase intraday cadence.
ALERT_COOLDOWN_HOURS = _parse_int_env("ALERT_COOLDOWN_HOURS", 6, min_value=0, max_value=72)


def load_state() -> dict:
    def _base_state() -> dict:
        return {
            "fired": {},
            "snoozed_strategies": {},
            "snoozed_tickers": {},
            "ticker_cooldowns": {},
            "email_ticker_last_sent": {},
            "sms_ticker_last_sent": {},
            "intraday_tracking": {},
            "signal_last_notified_price": {},
        }

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
                if not isinstance(state, dict):
                    return _base_state()
                for k, v in _base_state().items():
                    if k not in state or not isinstance(state.get(k), dict):
                        state[k] = v
                return state
        except Exception:
            pass
    return _base_state()


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def make_state_key(signal: dict) -> str:
    return f"{signal['ticker']}::{signal['strategy']}"


def already_fired_recently(state: dict, key: str) -> bool:
    """
    Return True if this signal was already emailed within the last ALERT_COOLDOWN_HOURS.
    """
    last_sent_str = state["fired"].get(key)
    if not last_sent_str:
        return False
    try:
        last_sent = datetime.fromisoformat(last_sent_str)
        if last_sent.tzinfo is None:
            last_sent = last_sent.astimezone()
        cutoff = datetime.now().astimezone() - timedelta(hours=ALERT_COOLDOWN_HOURS)
        return last_sent >= cutoff
    except Exception:
        return False


def mark_fired(state: dict, key: str) -> None:
    """Record the current timestamp (with timezone) for this signal key."""
    state["fired"][key] = datetime.now().astimezone().isoformat()


def prune_state(state: dict) -> dict:
    """Remove entries older than 48 hours to keep the state file lean."""
    cutoff = datetime.now().timestamp() - 48 * 3600

    def _ts(v: str) -> float:
        try:
            return datetime.fromisoformat(v).timestamp()
        except (ValueError, TypeError):
            return 0.0

    state["fired"] = {k: v for k, v in state["fired"].items() if _ts(v) > cutoff}
    prices = state.get("signal_last_notified_price", {})
    if not isinstance(prices, dict):
        prices = {}
    # Keep last notified prices only for still-recent fired keys.
    state["signal_last_notified_price"] = {
        k: v for k, v in prices.items() if k in state["fired"]
    }
    state["email_ticker_last_sent"] = {
        k: v for k, v in state.get("email_ticker_last_sent", {}).items() if _ts(v) > cutoff
    }
    state["sms_ticker_last_sent"] = {
        k: v for k, v in state.get("sms_ticker_last_sent", {}).items() if _ts(v) > cutoff
    }
    snoozed = state.get("snoozed_strategies", {})
    if not isinstance(snoozed, dict):
        snoozed = {}
    now_ts = datetime.now().astimezone().timestamp()
    state["snoozed_strategies"] = {
        strategy: until
        for strategy, until in snoozed.items()
        if _ts(until) > now_ts
    }
    snoozed_tickers = state.get("snoozed_tickers", {})
    if not isinstance(snoozed_tickers, dict):
        snoozed_tickers = {}
    state["snoozed_tickers"] = {
        ticker: until
        for ticker, until in snoozed_tickers.items()
        if _ts(until) > now_ts
    }
    tracking = state.get("intraday_tracking", {})
    if not isinstance(tracking, dict):
        tracking = {}
    cleaned: dict[str, dict] = {}
    for ticker, meta in tracking.items():
        if not isinstance(meta, dict):
            continue
        try:
            cadence = int(meta.get("cadence_min", 1440))
        except (TypeError, ValueError):
            cadence = 1440
        if cadence not in TRACKING_CADENCE_MINUTES:
            cadence = 1440
        out = {"cadence_min": cadence}
        lf = meta.get("last_fetch_at")
        if isinstance(lf, str):
            out["last_fetch_at"] = lf
        lc = meta.get("last_change_at")
        if isinstance(lc, str):
            out["last_change_at"] = lc
        cleaned[ticker] = out
    state["intraday_tracking"] = cleaned
    return state


def _tracking_bucket(state: dict) -> dict:
    bucket = state.setdefault("intraday_tracking", {})
    if not isinstance(bucket, dict):
        bucket = {}
        state["intraday_tracking"] = bucket
    return bucket


def _tracking_cadence(state: dict, ticker: str) -> int:
    meta = _tracking_bucket(state).get(ticker, {})
    if not isinstance(meta, dict):
        return 1440
    try:
        cadence = int(meta.get("cadence_min", 1440))
    except (TypeError, ValueError):
        return 1440
    return cadence if cadence in TRACKING_CADENCE_MINUTES else 1440


def _set_tracking_cadence(state: dict, ticker: str, cadence_min: int) -> None:
    cadence = cadence_min if cadence_min in TRACKING_CADENCE_MINUTES else 1440
    bucket = _tracking_bucket(state)
    meta = bucket.get(ticker, {})
    if not isinstance(meta, dict):
        meta = {}
    meta["cadence_min"] = cadence
    meta["last_change_at"] = datetime.now().astimezone().isoformat()
    bucket[ticker] = meta


def _mark_tracking_fetch(state: dict, ticker: str) -> None:
    bucket = _tracking_bucket(state)
    meta = bucket.get(ticker, {})
    if not isinstance(meta, dict):
        meta = {}
    meta["last_fetch_at"] = datetime.now().astimezone().isoformat()
    bucket[ticker] = meta


def _is_tracking_due(state: dict, ticker: str) -> bool:
    cadence = _tracking_cadence(state, ticker)
    # Scheduler currently runs every ~30 minutes, so 15m is "as fast as available".
    if cadence <= 30:
        return True
    meta = _tracking_bucket(state).get(ticker, {})
    if not isinstance(meta, dict):
        return True
    last = meta.get("last_fetch_at")
    if not isinstance(last, str):
        return True
    try:
        dt = datetime.fromisoformat(last)
    except (TypeError, ValueError):
        return True
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return datetime.now().astimezone() >= (dt + timedelta(minutes=cadence))


def _progressive_tracking_update(state: dict, high_conf_tickers: set[str]) -> None:
    bucket = _tracking_bucket(state)
    tracked = set(bucket.keys()) | set(high_conf_tickers)
    for ticker in sorted(tracked):
        cur = _tracking_cadence(state, ticker)
        if ticker in high_conf_tickers:
            if cur != 15:
                _set_tracking_cadence(state, ticker, 15)
                logger.info("  Tracking cadence %s -> 15m (high confidence active)", ticker)
            continue
        try:
            idx = TRACKING_CADENCE_MINUTES.index(cur)
        except ValueError:
            idx = len(TRACKING_CADENCE_MINUTES) - 1
        nxt = TRACKING_CADENCE_MINUTES[min(idx + 1, len(TRACKING_CADENCE_MINUTES) - 1)]
        if nxt != cur:
            _set_tracking_cadence(state, ticker, nxt)
            label = "Daily" if nxt >= 1440 else f"{nxt}m"
            logger.info("  Tracking cadence %s -> %s (confidence cooled)", ticker, label)


def _latest_price_for_ticker(ticker: str, cache: dict[str, float | None]) -> float | None:
    if ticker in cache:
        return cache[ticker]
    df15 = fetch_15m_bars(ticker)
    if df15 is None or df15.empty:
        cache[ticker] = None
        return None
    try:
        px = float(df15["Close"].iloc[-1])
    except Exception:
        px = None
    cache[ticker] = px
    return px


def _signal_move_pct_since_last_notify(
    state: dict, signal: dict, price_cache: dict[str, float | None]
) -> float | None:
    key = make_state_key(signal)
    raw = (state.get("signal_last_notified_price") or {}).get(key)
    try:
        prior = float(raw)
    except (TypeError, ValueError):
        return None
    if prior == 0:
        return None
    latest = _latest_price_for_ticker(signal["ticker"], price_cache)
    if latest is None:
        return None
    return ((latest / prior) - 1.0) * 100.0


def is_strategy_snoozed(state: dict, strategy_name: str) -> bool:
    until = state.get("snoozed_strategies", {}).get(strategy_name)
    if not until:
        return False
    try:
        dt = datetime.fromisoformat(until)
    except (TypeError, ValueError):
        return False
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return datetime.now().astimezone() < dt


def is_ticker_snoozed(state: dict, ticker: str) -> bool:
    until = state.get("snoozed_tickers", {}).get(ticker)
    if not until:
        return False
    try:
        dt = datetime.fromisoformat(until)
    except (TypeError, ValueError):
        return False
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return datetime.now().astimezone() < dt


def ticker_cooldown_hours(state: dict, ticker: str, channel: str) -> float:
    """
    Return per-ticker cooldown hours for channel ('email' or 'sms').
    Falls back to channel defaults when override is not configured.
    """
    defaults = {
        "email": float(ALERT_COOLDOWN_HOURS),
        "sms": float(SMS_COOLDOWN_HOURS),
    }
    raw = (state.get("ticker_cooldowns", {}) or {}).get(ticker, {})
    if not isinstance(raw, dict):
        return defaults.get(channel, 0.0)
    key = f"{channel}_hours"
    val = raw.get(key)
    if val is None:
        return defaults.get(channel, 0.0)
    try:
        return max(0.0, float(val))
    except (TypeError, ValueError):
        return defaults.get(channel, 0.0)


def ticker_channel_in_cooldown(state: dict, ticker: str, channel: str) -> bool:
    mapping = {
        "email": "email_ticker_last_sent",
        "sms": "sms_ticker_last_sent",
    }
    bucket = mapping.get(channel)
    if not bucket:
        return False
    hours = ticker_cooldown_hours(state, ticker, channel)
    if hours <= 0:
        return False
    last = (state.get(bucket) or {}).get(ticker)
    if not last:
        return False
    try:
        dt = datetime.fromisoformat(last)
    except (TypeError, ValueError):
        return False
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return datetime.now().astimezone() < (dt + timedelta(hours=hours))


def sms_may_send(state: dict) -> bool:
    """True if email-to-SMS is configured, enabled, and outside global cooldown window."""
    if not SMS_ENABLED or not SMS_GATEWAY or not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    if SMS_COOLDOWN_HOURS <= 0:
        return True
    last = state.get("last_sms_at")
    if not last:
        return True
    try:
        t = datetime.fromisoformat(last)
        if t.tzinfo is None:
            t = t.astimezone()
    except (TypeError, ValueError):
        return True
    return datetime.now().astimezone() >= t + timedelta(hours=SMS_COOLDOWN_HOURS)

# ─── Email Builder ────────────────────────────────────────────────────────────

def _win_bar(win_rate: float) -> str:
    """Render a simple HTML progress bar for win rate."""
    filled = int(win_rate)
    color  = "#22c55e" if win_rate >= 60 else ("#f59e0b" if win_rate >= 50 else "#ef4444")
    return (
        f'<div style="background:#1e293b;border-radius:4px;height:8px;margin-top:4px">'
        f'<div style="width:{filled}%;background:{color};height:8px;border-radius:4px"></div>'
        f'</div>'
    )


def build_signal_card(signal: dict) -> str:
    direction  = signal["direction"]
    is_bullish = direction == "BULLISH"
    accent     = "#22c55e" if is_bullish else "#ef4444"
    bg_accent  = "#0f2d1f" if is_bullish else "#2d0f0f"
    dir_label  = "BUY SIGNAL" if is_bullish else "SELL SIGNAL"
    dir_emoji  = "📈" if is_bullish else "📉"

    bt    = signal.get("backtest", {})
    d5    = bt.get("5d", {})
    count = bt.get("count", 0)
    conf  = signal.get("confidence", 0)
    conf_base = signal.get("confidence_base", conf)
    conf_adj = signal.get("confidence_adj", 0.0)
    conf_adj_reason = signal.get("confidence_adj_reason", "")

    # Score badge color (same thresholds as before)
    conf_color = "#22c55e" if conf >= 65 else ("#f59e0b" if conf >= 52 else "#ef4444")
    adj_html = ""
    if abs(conf_adj) > 0:
        adj_color = "#22c55e" if conf_adj > 0 else "#ef4444"
        adj_sign = "+" if conf_adj > 0 else ""
        adj_html = (
            f'<div style="font-size:10px;color:{adj_color};margin-top:4px">'
            f'Base {conf_base:.0f} {adj_sign}{conf_adj:.0f} positioning = {conf:.0f}</div>'
            f'<div style="font-size:9px;color:#64748b;margin-top:2px">{conf_adj_reason}</div>'
        )

    bd = confidence_breakdown(bt)
    pts_html = ""
    if bd:
        wr20 = bd["wr20_pts"] if bd["has_20d"] else 0
        pts_html = (
            f'<div style="font-size:10px;color:#64748b;margin-top:6px;line-height:1.45">'
            f'Pts 5dWR {bd["wr5_pts"]}+Sh {bd["sharpe_pts"]}+20dWR {wr20}+PF {bd["pf_pts"]} '
            f'· n={bd["n_5d"]}</div>'
        )

    # Backtest rows
    def _metric_color(val: float, good_above: float = 0) -> str:
        return "#22c55e" if val >= good_above else "#ef4444"

    bt_rows = ""
    for period_key, period_label in [("5d", "5-Day"), ("20d", "20-Day")]:
        pd_data = bt.get(period_key, {})
        if not pd_data:
            continue
        wr   = pd_data.get("win_rate", 0)
        ar   = pd_data.get("avg_return", 0)
        sh   = pd_data.get("sharpe", 0)
        so   = pd_data.get("sortino", 0)
        pf   = pd_data.get("profit_factor", 1)
        dd   = pd_data.get("max_drawdown", 0)
        cnt  = pd_data.get("count", 0)
        sep  = "border-top:1px solid #1e293b;" if period_key == "20d" else ""
        bt_rows += f"""
        <tr style="{sep}">
          <td style="padding:6px 10px;color:#94a3b8;font-size:12px;font-weight:600">{period_label}</td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(wr,55)};font-weight:700;font-size:13px">{wr:.0f}%</div>
            <div style="color:#475569;font-size:10px">win rate</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(ar)};font-weight:700;font-size:13px">{ar:+.1f}%</div>
            <div style="color:#475569;font-size:10px">avg return</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(sh,0.5)};font-weight:700;font-size:13px">{sh:.2f}</div>
            <div style="color:#475569;font-size:10px">Sharpe</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(so,0.5)};font-weight:700;font-size:13px">{so:.2f}</div>
            <div style="color:#475569;font-size:10px">Sortino</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(pf,1.2)};font-weight:700;font-size:13px">{pf:.1f}x</div>
            <div style="color:#475569;font-size:10px">profit factor</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:#ef4444;font-weight:700;font-size:13px">{dd:.1f}%</div>
            <div style="color:#475569;font-size:10px">max DD</div>
          </td>
          <td style="padding:6px 10px;color:#64748b;font-size:11px;text-align:right">{cnt} trades</td>
        </tr>"""

    ho = bt.get("holdout")
    if ho and ho.get("5d"):
        ho_note = ho.get("span_note", "")
        note_html = (
            f'<div style="font-size:9px;color:#64748b;font-weight:400">{ho_note}</div>'
            if ho_note
            else ""
        )
        first_ho = True
        for period_key, period_stub in [("5d", "5d"), ("20d", "20d")]:
            pd_data = ho.get(period_key, {})
            if not pd_data:
                continue
            wr   = pd_data.get("win_rate", 0)
            ar   = pd_data.get("avg_return", 0)
            sh   = pd_data.get("sharpe", 0)
            so   = pd_data.get("sortino", 0)
            pf   = pd_data.get("profit_factor", 1)
            dd   = pd_data.get("max_drawdown", 0)
            cnt  = pd_data.get("count", 0)
            lab  = f"Recent slice · {period_stub}"
            sep  = "border-top:1px solid #334155;"
            cell_extra = note_html if first_ho else ""
            first_ho = False
            bt_rows += f"""
        <tr style="{sep}">
          <td style="padding:6px 10px;color:#a78bfa;font-size:11px;font-weight:700">{lab}{cell_extra}</td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(wr,55)};font-weight:700;font-size:13px">{wr:.0f}%</div>
            <div style="color:#475569;font-size:10px">win rate</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(ar)};font-weight:700;font-size:13px">{ar:+.1f}%</div>
            <div style="color:#475569;font-size:10px">avg return</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(sh,0.5)};font-weight:700;font-size:13px">{sh:.2f}</div>
            <div style="color:#475569;font-size:10px">Sharpe</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(so,0.5)};font-weight:700;font-size:13px">{so:.2f}</div>
            <div style="color:#475569;font-size:10px">Sortino</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:{_metric_color(pf,1.2)};font-weight:700;font-size:13px">{pf:.1f}x</div>
            <div style="color:#475569;font-size:10px">profit factor</div>
          </td>
          <td style="padding:6px 10px;text-align:center">
            <div style="color:#ef4444;font-weight:700;font-size:13px">{dd:.1f}%</div>
            <div style="color:#475569;font-size:10px">max DD</div>
          </td>
          <td style="padding:6px 10px;color:#64748b;font-size:11px;text-align:right">{cnt} trades</td>
        </tr>"""

    no_bt_msg = ""
    if not d5:
        no_bt_msg = (
            '<p style="color:#64748b;font-size:12px;margin:10px 0 0">'
            f'Insufficient backtest history ({count} signals found). '
            'Signal may be rare — proceed with caution.</p>'
        )

    return f"""
    <div style="background:#0f172a;border-radius:12px;overflow:hidden;
                margin-bottom:18px;border:1px solid {accent}40">

      <!-- Header -->
      <div style="background:{bg_accent};padding:16px 18px;
                  border-bottom:1px solid {accent}30">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;
                    margin-bottom:8px">
          <div>
            <span style="font-size:10px;color:{accent};font-weight:700;
                         letter-spacing:2px;text-transform:uppercase">
              {dir_emoji} {dir_label}
            </span>
            <div style="font-size:20px;font-weight:800;color:#f1f5f9;margin-top:4px">
              {signal['name']}
              <span style="font-size:13px;color:#64748b;font-weight:400">
                ({signal['ticker']})
              </span>
            </div>
            <div style="font-size:11px;color:#475569;margin-top:4px">{signal.get('regime', '')}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:10px;color:#64748b;margin-bottom:2px">BACKTEST SCORE</div>
            <div style="font-size:22px;font-weight:900;color:{conf_color}">{conf:.0f}</div>
            {adj_html}
            {pts_html}
          </div>
        </div>
        <div style="background:#0f172a;border-radius:6px;padding:8px 10px;
                    font-size:13px;color:#818cf8;font-weight:600;font-family:monospace">
          {signal.get('indicator', '')}
        </div>
      </div>

      <!-- Strategy Name + Detail -->
      <div style="padding:14px 18px;border-bottom:1px solid #1e293b">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
          <span style="font-size:11px;color:#475569;font-weight:700;
                       text-transform:uppercase;letter-spacing:1px">
            Strategy: {signal['strategy']}
          </span>
          {strategy_learn_link(signal['strategy'], style='badge')}
        </div>
        <p style="color:#cbd5e1;font-size:13px;margin:0 0 10px;line-height:1.6">
          {signal.get('detail', '')}
        </p>
        <div style="background:#1e3a5f20;border-left:3px solid #6366f1;
                    padding:8px 12px;border-radius:0 6px 6px 0">
          <span style="font-size:11px;color:#818cf8;font-weight:700">ACTION IMPLICATION: </span>
          <span style="font-size:12px;color:#94a3b8">{signal.get('implication', '')}</span>
        </div>
      </div>

      <!-- Backtest Stats -->
      <div style="padding:12px 18px">
        <div style="font-size:11px;color:#475569;font-weight:700;
                    text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
          Historical Backtest — Last 2 Years ({count} signals)
        </div>
        {f'''
        <table style="width:100%;border-collapse:collapse;background:#0a0f1e;
                      border-radius:8px;overflow:hidden">
          <tr style="background:#1e293b">
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:left;
                       font-weight:600;text-transform:uppercase">Period</th>
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:center;
                       font-weight:600;text-transform:uppercase">Win %</th>
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:center;
                       font-weight:600;text-transform:uppercase">Avg Ret</th>
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:center;
                       font-weight:600;text-transform:uppercase">Sharpe</th>
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:center;
                       font-weight:600;text-transform:uppercase">Sortino</th>
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:center;
                       font-weight:600;text-transform:uppercase">Prof. Factor</th>
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:center;
                       font-weight:600;text-transform:uppercase">Max DD</th>
            <th style="padding:6px 10px;color:#475569;font-size:10px;text-align:right;
                       font-weight:600;text-transform:uppercase">n</th>
          </tr>
          {bt_rows}
        </table>''' if bt_rows else no_bt_msg}
      </div>
    </div>"""


def build_alert_email(
    new_signals: list[dict],
    all_signals: list[dict],
    *,
    dispatch_seq: int,
    intraday_15m_html: str = "",
) -> tuple:
    """Returns (subject, html). dispatch_seq increments each send so subjects/bodies stay distinct."""

    now_et   = datetime.now(ET_ZONE)
    time_str = now_et.strftime("%I:%M %p ET")
    time_precise = now_et.strftime("%I:%M:%S %p ET")
    date_str = now_et.strftime("%A, %B %d, %Y")

    bullish_n = sum(1 for s in new_signals if s["direction"] == "BULLISH")
    bearish_n = sum(1 for s in new_signals if s["direction"] == "BEARISH")

    top = new_signals[0]
    top_conf = top.get("confidence", 0)

    subject = (
        f"{'📈' if top['direction']=='BULLISH' else '📉'} Strategy Alert: "
        f"{top['strategy']} on {top['name']} "
        f"({top_conf:.0f}/100 score)"
        + (f" + {len(new_signals)-1} more" if len(new_signals) > 1 else "")
        + f" | {time_str}"
        + f" · #{dispatch_seq}"
    )

    signal_cards = "".join(build_signal_card(s) for s in new_signals)

    # Today's full signal summary (all, not just new ones)
    summary_rows = ""
    for s in all_signals[:20]:
        c  = s.get("confidence", 0)
        cc = "#22c55e" if c >= 65 else ("#f59e0b" if c >= 52 else "#94a3b8")
        d  = "▲" if s["direction"] == "BULLISH" else "▼"
        dc = "#22c55e" if s["direction"] == "BULLISH" else "#ef4444"
        summary_rows += (
            f'<tr style="border-bottom:1px solid #0f172a">'
            f'<td style="padding:7px 12px;color:{dc};font-size:14px;font-weight:700">{d}</td>'
            f'<td style="padding:7px 12px;color:#e2e8f0;font-size:12px;font-weight:600">{s["ticker"]}</td>'
            f'<td style="padding:7px 12px;color:#94a3b8;font-size:12px">{s["strategy"]}</td>'
            f'<td style="padding:7px 12px;color:{cc};font-size:12px;font-weight:700;text-align:right">{c:.0f}</td>'
            f'</tr>'
        )

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Strategy Alert #{dispatch_seq} — {time_str}</title>
</head>
<body style="margin:0;padding:0;background:#020617;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif">
<div style="max-width:680px;margin:0 auto;padding:20px 14px">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#1e1b4b 0%,#0f172a 100%);
              border-radius:14px;padding:24px;margin-bottom:18px;text-align:center">
    <div style="font-size:10px;color:#818cf8;letter-spacing:3px;
                text-transform:uppercase;font-weight:700;margin-bottom:10px">
      Strategy Signal Alert
    </div>
    <div style="font-size:22px;font-weight:900;color:#f1f5f9;margin-bottom:6px">
      {bullish_n} Bullish &nbsp; · &nbsp; {bearish_n} Bearish
    </div>
    <div style="font-size:12px;color:#64748b">
      {date_str} &nbsp;·&nbsp; {time_str}
      &nbsp;·&nbsp; Ranked by 2-year backtest score
    </div>
    <div style="font-size:11px;color:#a78bfa;margin-top:10px;font-weight:600;
                letter-spacing:0.02em;line-height:1.4">
      Dispatch #{dispatch_seq} &nbsp;·&nbsp; {time_precise}
      &nbsp;—&nbsp; new send (not a repeat of a prior email)
    </div>
  </div>

  <!-- Explanation -->
  <div style="background:#0f172a;border-radius:10px;padding:14px 16px;
              margin-bottom:18px;border:1px solid #1e293b">
    <p style="color:#94a3b8;font-size:12px;margin:0;line-height:1.7">
      <strong style="color:#e2e8f0">How to read these alerts:</strong>
      Each signal has been backtested against 2 years of history.
      <strong style="color:#818cf8">Backtest score</strong> (0-100) combines 5-day and 20-day win rates,
      Sharpe, and profit factor from the 2-year rule history — not a forecast of profit probability.
      Alerts fire when score &ge; {MIN_CONFIDENCE:.0f}.
      <strong style="color:#f59e0b">These are not buy/sell recommendations</strong> —
      use as one input alongside your own research.
    </p>
  </div>

  <!-- New Signal Cards -->
  <h2 style="color:#f1f5f9;margin:0 0 14px;font-size:17px;font-weight:700">
    New Signals This Check
  </h2>
  {signal_cards}

  {intraday_15m_html}

  <!-- Today's Full Scan Summary -->
  {f'''
  <div style="background:#0f172a;border-radius:10px;overflow:hidden;
              margin-top:20px;margin-bottom:20px;border:1px solid #1e293b">
    <div style="background:#1e293b;padding:12px 16px">
      <h3 style="color:#f1f5f9;margin:0;font-size:14px;font-weight:700">
        All Active Signals Today (top {min(len(all_signals),20)})
      </h3>
    </div>
    <table style="width:100%;border-collapse:collapse">
      <tr style="background:#0a0f1e">
        <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:left;
                   font-weight:600;text-transform:uppercase">Dir</th>
        <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:left;
                   font-weight:600;text-transform:uppercase">Ticker</th>
        <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:left;
                   font-weight:600;text-transform:uppercase">Strategy</th>
        <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:right;
                   font-weight:600;text-transform:uppercase">Score</th>
      </tr>
      {summary_rows}
    </table>
  </div>
  ''' if all_signals else ''}

  <!-- Footer -->
  <div style="text-align:center;padding:16px 0 4px;color:#374151;font-size:11px;
              border-top:1px solid #1e293b">
    <p style="margin:0 0 4px">
      Investment Daily Strategy Alerts &nbsp;·&nbsp;
      Checks every 30 min | Market hours only
    </p>
    <p style="margin:8px 0 0;background:#111827;border-radius:6px;padding:10px;
              color:#6b7280;line-height:1.5">
      Backtests use historical data and do not guarantee future results.
      Not financial advice. Always do your own research before trading.
    </p>
  </div>

</div>
</body></html>"""

    return subject, html

# ─── SMS Sender ───────────────────────────────────────────────────────────────

def send_sms(signals: list[dict]) -> bool:
    """Send a concise plain-text SMS summary via email-to-SMS gateway."""
    if not SMS_GATEWAY or not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    try:
        top = signals[0]
        direction = "BUY" if top["direction"] == "BULLISH" else "SELL"
        body = (
            f"{direction}: {top['ticker']} | {top['strategy']}\n"
            f"Score: {top['confidence']:.0f}/100\n"
            f"{top.get('indicator', '')}"
        )
        if len(signals) > 1:
            body += f"\n+{len(signals) - 1} more"
        if len(body) > SMS_BODY_MAX:
            body = body[: SMS_BODY_MAX - 3] + "..."

        from email.mime.text import MIMEText as _MIMEText
        msg         = _MIMEText(body, _charset="utf-8")
        msg["From"] = EMAIL_SENDER
        msg["To"]   = SMS_GATEWAY
        # Omitted Subject: many gateways count it against length / duplicate the alert line.

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, SMS_GATEWAY, msg.as_string())
        logger.info(f"SMS alert sent -> {SMS_GATEWAY}")
        return True
    except Exception as exc:
        logger.warning(f"SMS send failed: {exc}")
        return False


# ─── Email Sender ─────────────────────────────────────────────────────────────

def send_email(subject: str, html: str) -> None:
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD must be set in .env")
    msg            = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECIPIENT
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
    logger.info(f"Alert email sent -> {EMAIL_RECIPIENT}")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main(crypto_only: bool = False) -> None:
    mode_label = "crypto 24/7" if crypto_only else "equities + crypto"
    logger.info(f"=== Strategy alert check starting ({mode_label}) ===")

    if not crypto_only and not is_market_open():
        logger.info(f"Market closed ({market_status_str()}) — skipping.")
        return

    logger.info(f"Running scan ({market_status_str()}) ...")

    if crypto_only:
        scan_tickers = {k: v for k, v in SCAN_TICKERS.items() if k.endswith("-USD")}
        all_signals = run_full_scan(scan_tickers, dex_tickers=DEX_TICKERS)
    else:
        all_signals = run_full_scan(SCAN_TICKERS)

    if not all_signals:
        logger.info("No signals above score threshold — no alert sent.")
        return

    state = load_state()
    state = prune_state(state)

    # Filter out strategies/tickers that are remotely snoozed.
    snoozed = []
    active_signals = []
    for s in all_signals:
        if is_strategy_snoozed(state, s["strategy"]) or is_ticker_snoozed(state, s["ticker"]):
            snoozed.append(s)
        else:
            active_signals.append(s)

    if snoozed:
        logger.info(
            f"{len(snoozed)} signal(s) suppressed by strategy snooze: "
            + ", ".join(f"{s['ticker']}:{s['strategy']}" for s in snoozed[:8])
            + (" ..." if len(snoozed) > 8 else "")
        )

    if not active_signals:
        logger.info("All signals are currently snoozed — no alert sent.")
        return

    hi_tickers = {
        s["ticker"]
        for s in active_signals
        if s.get("confidence", 0) >= HIGH_CONFIDENCE_15M_THRESHOLD
    }
    _progressive_tracking_update(state, hi_tickers)

    # Filter to signals not emailed within global/per-ticker cooldown windows
    new_signals = []
    suppressed_signal_cooldown  = []
    suppressed_ticker_cooldown = []
    bypassed_signal_cooldown = []
    price_cache: dict[str, float | None] = {}
    for s in active_signals:
        key = make_state_key(s)
        if ticker_channel_in_cooldown(state, s["ticker"], "email"):
            suppressed_ticker_cooldown.append(s)
        elif already_fired_recently(state, key):
            move_pct = _signal_move_pct_since_last_notify(state, s, price_cache)
            if move_pct is not None and abs(move_pct) > COOLDOWN_BYPASS_MOVE_PCT:
                new_signals.append(s)
                bypassed_signal_cooldown.append((s, move_pct))
            else:
                suppressed_signal_cooldown.append(s)
        else:
            new_signals.append(s)

    if suppressed_signal_cooldown:
        logger.info(
            f"{len(suppressed_signal_cooldown)} signal(s) suppressed (already sent within {ALERT_COOLDOWN_HOURS}h): "
            + ", ".join(f"{s['ticker']}:{s['strategy']}" for s in suppressed_signal_cooldown[:8])
            + (" ..." if len(suppressed_signal_cooldown) > 8 else "")
        )
    if suppressed_ticker_cooldown:
        logger.info(
            f"{len(suppressed_ticker_cooldown)} signal(s) suppressed by ticker email cooldown: "
            + ", ".join(f"{s['ticker']}:{s['strategy']}" for s in suppressed_ticker_cooldown[:8])
            + (" ..." if len(suppressed_ticker_cooldown) > 8 else "")
        )
    if bypassed_signal_cooldown:
        logger.info(
            f"{len(bypassed_signal_cooldown)} signal(s) bypassed cooldown (|move| > {COOLDOWN_BYPASS_MOVE_PCT:.1f}%): "
            + ", ".join(
                f"{s['ticker']}:{s['strategy']} ({mv:+.2f}%)"
                for s, mv in bypassed_signal_cooldown[:8]
            )
            + (" ..." if len(bypassed_signal_cooldown) > 8 else "")
        )

    if not new_signals:
        logger.info(f"No new signals outside {ALERT_COOLDOWN_HOURS}h cooldown — skipping.")
        save_state(state)
        return

    logger.info(f"{len(new_signals)} new signal(s) to alert on:")
    for s in new_signals:
        base = s.get("confidence_base", s["confidence"])
        adj = s.get("confidence_adj", 0.0)
        logger.info(
            f"  {s['direction']:7s} | {s['ticker']:10s} | {s['strategy']:30s} | "
            f"score={s['confidence']:.0f} (base={base:.0f}, adj={adj:+.0f})"
        )

    dispatch_seq = int(state.get("send_count", 0)) + 1
    state["send_count"] = dispatch_seq

    tracked_tickers = set((state.get("intraday_tracking") or {}).keys())
    intraday_parts: list[str] = []
    intraday_meta_rows: list[str] = []
    for t in sorted(tracked_tickers):
        cadence = _tracking_cadence(state, t)
        if not _is_tracking_due(state, t):
            continue
        display = SCAN_TICKERS.get(t, t)
        df15 = fetch_15m_bars(t)
        _mark_tracking_fetch(state, t)
        if df15 is None:
            logger.info("  15m context skipped for %s (insufficient data)", t)
            continue
        intraday_parts.append(format_intraday_15m_alert_html(t, display, df15))
        cadence_label = "Daily" if cadence >= 1440 else f"{cadence}m"
        mode = "high-confidence" if t in hi_tickers else "cooldown tracking"
        intraday_meta_rows.append(
            f'<tr style="border-bottom:1px solid #0f172a">'
            f'<td style="padding:5px 8px;color:#e2e8f0;font-size:11px">{t}</td>'
            f'<td style="padding:5px 8px;color:#94a3b8;font-size:11px">{mode}</td>'
            f'<td style="padding:5px 8px;color:#a78bfa;font-size:11px;text-align:right">{cadence_label}</td>'
            f'</tr>'
        )
        logger.info(
            "  15m context added for %s (%s cadence, %s)",
            t,
            cadence_label,
            mode,
        )

    intraday_15m_html = ""
    if intraday_parts:
        intraday_15m_html = f"""
  <h2 style="color:#f1f5f9;margin:24px 0 14px;font-size:17px;font-weight:700">
    Progressive ticker tracking (15m bars)
  </h2>
  <p style="color:#94a3b8;font-size:12px;margin:-8px 0 14px;line-height:1.6">
    Tickers at score ≥ {HIGH_CONFIDENCE_15M_THRESHOLD:.0f} reset to 15m cadence.
    If confidence cools off, cadence steps back progressively: 30m, 60m, 120m, 240m, then Daily.
  </p>
  <table style="width:100%;border-collapse:collapse;background:#0f172a;border:1px solid #1e293b;
                border-radius:8px;overflow:hidden;margin:0 0 14px">
    <tr style="background:#111827">
      <th style="padding:6px 8px;color:#64748b;font-size:10px;text-align:left;text-transform:uppercase">Ticker</th>
      <th style="padding:6px 8px;color:#64748b;font-size:10px;text-align:left;text-transform:uppercase">Mode</th>
      <th style="padding:6px 8px;color:#64748b;font-size:10px;text-align:right;text-transform:uppercase">Cadence</th>
    </tr>
    {"".join(intraday_meta_rows)}
  </table>
  {"".join(intraday_parts)}
"""

    subject, html = build_alert_email(
        new_signals,
        all_signals,
        dispatch_seq=dispatch_seq,
        intraday_15m_html=intraday_15m_html,
    )
    send_email(subject, html)
    top_for_sms = new_signals[0] if new_signals else None
    sms_ticker_blocked = bool(top_for_sms and ticker_channel_in_cooldown(state, top_for_sms["ticker"], "sms"))
    if sms_ticker_blocked:
        logger.info(
            f"SMS skipped: ticker cooldown for {top_for_sms['ticker']} ({ticker_cooldown_hours(state, top_for_sms['ticker'], 'sms')}h)."
        )
    elif sms_may_send(state):
        if send_sms(new_signals):
            state["last_sms_at"] = datetime.now().astimezone().isoformat()
            if top_for_sms:
                state.setdefault("sms_ticker_last_sent", {})[top_for_sms["ticker"]] = (
                    datetime.now().astimezone().isoformat()
                )
        else:
            logger.warning("SMS failed; cooldown timestamp not updated so next run can retry.")
    elif SMS_ENABLED and SMS_GATEWAY and EMAIL_SENDER and EMAIL_PASSWORD:
        logger.info(
            f"SMS skipped: global gateway cooldown ({SMS_COOLDOWN_HOURS}h since last SMS) — email sent."
        )

    # Record timestamp for each fired signal
    now_iso = datetime.now().astimezone().isoformat()
    last_price_bucket = state.setdefault("signal_last_notified_price", {})
    if not isinstance(last_price_bucket, dict):
        last_price_bucket = {}
        state["signal_last_notified_price"] = last_price_bucket
    for s in new_signals:
        key = make_state_key(s)
        mark_fired(state, key)
        state.setdefault("email_ticker_last_sent", {})[s["ticker"]] = now_iso
        latest = _latest_price_for_ticker(s["ticker"], price_cache)
        if latest is not None:
            last_price_bucket[key] = latest
    save_state(state)

    logger.info("=== Done ===")


if __name__ == "__main__":
    main(crypto_only="--crypto" in sys.argv)
