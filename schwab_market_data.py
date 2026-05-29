"""
Optional Schwab Market Data (OAuth) → daily OHLCV for strategy_engine.

Enable with SCHWAB_MARKET_DATA=1 plus SCHWAB_CLIENT_ID and SCHWAB_CLIENT_SECRET in .env.
First auth: run  python scripts/schwab_login.py  (browser flow, writes schwab_token.json).

Symbols with '=', '-USD', or '^' are skipped (futures/crypto Yahoo-style / indices); those
stay on yfinance. Schwab daily history is trimmed to ~2 years to match scan_ticker.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING, Any

import pandas as pd
from dotenv import load_dotenv

if TYPE_CHECKING:
    from schwab.client import Client

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

_client: Client | None = None


def _truthy(val: str | None) -> bool:
    if val is None:
        return False
    return val.strip().lower() in ("1", "true", "yes", "on")


def schwab_market_data_enabled() -> bool:
    if not _truthy(os.getenv("SCHWAB_MARKET_DATA")):
        return False
    cid = os.getenv("SCHWAB_CLIENT_ID", "").strip()
    secret = os.getenv("SCHWAB_CLIENT_SECRET", "").strip()
    return bool(cid and secret)


def token_path() -> str:
    return os.path.join(
        SCRIPT_DIR, os.getenv("SCHWAB_TOKEN_PATH", "schwab_token.json")
    )


def callback_url() -> str:
    return os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8182").strip()


def use_schwab_for_symbol(symbol: str) -> bool:
    if not schwab_market_data_enabled():
        return False
    if any(x in symbol for x in ("=", "-USD", "^")):
        return False
    return True


def candles_to_dataframe_intraday(payload: dict[str, Any]) -> pd.DataFrame:
    """Schwab intraday JSON → DataFrame with ET timezone-aware index (no daily normalization)."""
    candles = payload.get("candles") or []
    if not candles:
        return pd.DataFrame()

    rows: list[dict[str, float | int]] = []
    times_ms: list[int] = []
    for c in candles:
        o = c.get("open")
        h = c.get("high")
        lo = c.get("low")
        cl = c.get("close")
        vol = c.get("volume")
        if o is None or h is None or lo is None or cl is None:
            continue
        dt = c.get("datetime")
        if dt is None:
            continue
        rows.append(
            {
                "Open": float(o),
                "High": float(h),
                "Low": float(lo),
                "Close": float(cl),
                "Volume": int(vol) if vol is not None else 0,
            }
        )
        times_ms.append(int(dt))

    if not rows:
        return pd.DataFrame()

    idx = pd.to_datetime(times_ms, unit="ms", utc=True)
    idx = idx.tz_convert("America/New_York")
    df = pd.DataFrame(rows, index=idx)
    return df.sort_index()


def price_history_to_dataframe(payload: dict[str, Any], years: float = 2.0) -> pd.DataFrame:
    """Map Schwab priceHistory JSON to a yfinance-like DataFrame (Open, High, Low, Close, Volume)."""
    candles = payload.get("candles") or []
    if not candles:
        return pd.DataFrame()

    rows: list[dict[str, float | int]] = []
    times_ms: list[int] = []
    for c in candles:
        o = c.get("open")
        h = c.get("high")
        lo = c.get("low")
        cl = c.get("close")
        vol = c.get("volume")
        if o is None or h is None or lo is None or cl is None:
            continue
        dt = c.get("datetime")
        if dt is None:
            continue
        rows.append(
            {
                "Open": float(o),
                "High": float(h),
                "Low": float(lo),
                "Close": float(cl),
                "Volume": int(vol) if vol is not None else 0,
            }
        )
        times_ms.append(int(dt))

    if not rows:
        return pd.DataFrame()

    idx = pd.to_datetime(times_ms, unit="ms", utc=True)
    idx = idx.tz_convert("America/New_York").normalize()
    df = pd.DataFrame(rows, index=idx)
    df = df.sort_index()
    cutoff = pd.Timestamp.now(tz="America/New_York") - pd.DateOffset(days=int(365 * years))
    df = df[df.index >= cutoff.normalize()]
    return df


def get_client() -> Client | None:
    """
    Return a shared Client, or None if Schwab is disabled / token missing in non-interactive mode.
    With token file: uses client_from_token_file. Without token: easy_client only if stdin is a TTY.
    """
    global _client
    if _client is not None:
        return _client
    if not schwab_market_data_enabled():
        return None

    from schwab.auth import client_from_token_file, easy_client

    client_id = os.environ["SCHWAB_CLIENT_ID"]
    client_secret = os.environ["SCHWAB_CLIENT_SECRET"]
    path = token_path()

    if os.path.isfile(path):
        _client = client_from_token_file(path, client_id, client_secret)
        return _client

    if not sys.stdin.isatty():
        logger.warning(
            "Schwab enabled but %s is missing; use scripts/schwab_login.py once. "
            "Falling back to yfinance for price data.",
            path,
        )
        return None

    _client = easy_client(
        client_id,
        client_secret,
        callback_url(),
        path,
        interactive=True,
    )
    return _client


def fetch_daily_history(symbol: str, client: Client | None = None) -> pd.DataFrame | None:
    """
    Fetch daily candles from Schwab; return None on failure or empty response.
    """
    c = client if client is not None else get_client()
    if c is None:
        return None
    try:
        resp = c.get_price_history_every_day(symbol)
        if resp.status_code != 200:
            logger.warning("Schwab price history %s: HTTP %s", symbol, resp.status_code)
            return None
        data = resp.json()
    except Exception as exc:
        logger.warning("Schwab price history %s failed: %s", symbol, exc)
        return None

    df = price_history_to_dataframe(data, years=2.0)
    if df.empty:
        return None
    return df


def fetch_fifteen_minute_history(symbol: str, client: Client | None = None) -> pd.DataFrame | None:
    """~15m bars (Schwab: observed ~9 months). Returns None on failure."""
    c = client if client is not None else get_client()
    if c is None:
        return None
    try:
        resp = c.get_price_history_every_fifteen_minutes(symbol)
        if resp.status_code != 200:
            logger.warning("Schwab 15m history %s: HTTP %s", symbol, resp.status_code)
            return None
        df = candles_to_dataframe_intraday(resp.json())
        if df.empty:
            return None
        return df
    except Exception as exc:
        logger.warning("Schwab 15m history %s failed: %s", symbol, exc)
        return None


def reset_client() -> None:
    """Test helper: clear cached client."""
    global _client
    _client = None
