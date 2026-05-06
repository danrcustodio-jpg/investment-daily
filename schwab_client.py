"""
Schwab API Data Provider
========================
Wraps schwab-py to provide market quotes and price history as a supplemental
data source alongside yfinance.  When Schwab credentials are not configured
or the API is unavailable, every public function returns None so callers can
fall back to yfinance transparently.

Required env vars (all optional — the module degrades gracefully):
    SCHWAB_API_KEY        – App key from developer.schwab.com
    SCHWAB_APP_SECRET     – App secret
    SCHWAB_CALLBACK_URL   – OAuth callback URL (default https://127.0.0.1)
    SCHWAB_TOKEN_PATH     – Path to persisted token file (default ./schwab_token.json)
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────

SCHWAB_API_KEY = os.getenv("SCHWAB_API_KEY", "")
SCHWAB_APP_SECRET = os.getenv("SCHWAB_APP_SECRET", "")
SCHWAB_CALLBACK_URL = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1")
SCHWAB_TOKEN_PATH = os.getenv(
    "SCHWAB_TOKEN_PATH",
    os.path.join(SCRIPT_DIR, "schwab_token.json"),
)

# Symbols the Schwab API cannot serve (crypto, commodity futures, forex, indices
# using yfinance-style tickers).  These always fall back to yfinance.
_SCHWAB_UNSUPPORTED_PREFIXES = ("^",)
_SCHWAB_UNSUPPORTED_SUFFIXES = ("-USD", "=F", "=X", ".NYB")


def _is_schwab_supported(symbol: str) -> bool:
    """Return True if the symbol can be looked up via Schwab's equity API."""
    if any(symbol.startswith(p) for p in _SCHWAB_UNSUPPORTED_PREFIXES):
        return False
    if any(symbol.endswith(s) for s in _SCHWAB_UNSUPPORTED_SUFFIXES):
        return False
    return True


# ─── Client singleton ────────────────────────────────────────────────────────

_client = None
_client_init_attempted = False


def _get_client():
    """
    Lazily initialise and return the Schwab API client.
    Returns None if credentials are missing or the library is not installed.
    """
    global _client, _client_init_attempted
    if _client_init_attempted:
        return _client
    _client_init_attempted = True

    if not SCHWAB_API_KEY or not SCHWAB_APP_SECRET:
        logger.info("Schwab API: credentials not configured — using yfinance only")
        return None

    try:
        from schwab.auth import client_from_token_file
    except ImportError:
        logger.warning("schwab-py not installed — using yfinance only")
        return None

    if not os.path.exists(SCHWAB_TOKEN_PATH):
        logger.warning(
            f"Schwab token file not found at {SCHWAB_TOKEN_PATH}. "
            "Run schwab-generate-token.py to create one, then restart."
        )
        return None

    try:
        _client = client_from_token_file(
            SCHWAB_TOKEN_PATH,
            SCHWAB_API_KEY,
            SCHWAB_APP_SECRET,
        )
        logger.info("Schwab API client initialised successfully")
    except Exception as exc:
        logger.warning(f"Schwab API client init failed: {exc}")
        _client = None

    return _client


def is_available() -> bool:
    """Return True if the Schwab client is ready to make API calls."""
    return _get_client() is not None


# ─── Batch Quotes ─────────────────────────────────────────────────────────────

def get_quotes(symbols: list[str]) -> dict[str, dict[str, Any]] | None:
    """
    Fetch current quotes for multiple symbols in a single API call.

    Returns {symbol: {"price": float, "change": float, "pct_change": float}}
    or None if the Schwab client is unavailable.

    Only equity/ETF symbols are queried; unsupported symbols are skipped.
    """
    client = _get_client()
    if client is None:
        return None

    schwab_symbols = [s for s in symbols if _is_schwab_supported(s)]
    if not schwab_symbols:
        return None

    try:
        import httpx
        resp = client.get_quotes(schwab_symbols)
        if resp.status_code != httpx.codes.OK:
            logger.warning(f"Schwab get_quotes returned {resp.status_code}")
            return None

        data = resp.json()
        result: dict[str, dict[str, Any]] = {}

        for sym in schwab_symbols:
            entry = data.get(sym)
            if not entry:
                continue
            quote = entry.get("quote", entry)
            last_price = quote.get("lastPrice") or quote.get("mark")
            close_price = quote.get("closePrice") or quote.get("regularMarketLastPrice")
            if last_price is None:
                continue

            change = (last_price - close_price) if close_price else 0.0
            pct = (change / close_price * 100) if close_price else 0.0

            result[sym] = {
                "price": float(last_price),
                "change": float(change),
                "pct_change": float(pct),
            }

        logger.info(f"Schwab: fetched quotes for {len(result)}/{len(schwab_symbols)} symbols")
        return result if result else None

    except Exception as exc:
        logger.warning(f"Schwab get_quotes error: {exc}")
        return None


# ─── Price History (OHLCV) ────────────────────────────────────────────────────

def get_price_history(
    symbol: str,
    period_years: int = 2,
) -> pd.DataFrame | None:
    """
    Fetch daily OHLCV history from Schwab for a single equity/ETF.

    Returns a DataFrame with columns [Open, High, Low, Close, Volume] indexed by
    datetime — compatible with the format scan_ticker() expects from yfinance.

    Returns None if the client is unavailable or the symbol is unsupported.
    """
    if not _is_schwab_supported(symbol):
        return None

    client = _get_client()
    if client is None:
        return None

    try:
        import httpx
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=period_years * 365)

        resp = client.get_price_history_every_day(
            symbol,
            start_datetime=start_dt,
            end_datetime=end_dt,
            need_extended_hours_data=False,
        )
        if resp.status_code != httpx.codes.OK:
            logger.warning(f"Schwab price history for {symbol}: HTTP {resp.status_code}")
            return None

        data = resp.json()
        candles = data.get("candles", [])
        if not candles:
            return None

        df = pd.DataFrame(candles)
        df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
        df.set_index("datetime", inplace=True)
        df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            },
            inplace=True,
        )
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        return df

    except Exception as exc:
        logger.warning(f"Schwab price history error for {symbol}: {exc}")
        return None


# ─── Short History (for market snapshot) ──────────────────────────────────────

def get_recent_closes(symbol: str, days: int = 5) -> list[float] | None:
    """
    Return the last `days` daily closing prices from Schwab.
    Returns None if unavailable.
    """
    if not _is_schwab_supported(symbol):
        return None

    client = _get_client()
    if client is None:
        return None

    try:
        import httpx
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days + 5)

        resp = client.get_price_history_every_day(
            symbol,
            start_datetime=start_dt,
            end_datetime=end_dt,
            need_extended_hours_data=False,
        )
        if resp.status_code != httpx.codes.OK:
            return None

        candles = resp.json().get("candles", [])
        if not candles:
            return None

        closes = [c["close"] for c in candles if "close" in c]
        return closes[-days:] if closes else None

    except Exception:
        return None
