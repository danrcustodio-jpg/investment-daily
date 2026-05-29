"""Unit tests for Schwab OHLCV parsing (no API calls)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from schwab_market_data import price_history_to_dataframe, use_schwab_for_symbol


def test_price_history_to_dataframe_shape():
    now = pd.Timestamp.now(tz="UTC")
    t0 = int((now - pd.Timedelta(days=1)).timestamp() * 1000)
    t1 = int(now.timestamp() * 1000)
    payload = {
        "candles": [
            {
                "open": 10.0,
                "high": 11.0,
                "low": 9.0,
                "close": 10.5,
                "volume": 1_000_000,
                "datetime": t0,
            },
            {
                "open": 10.5,
                "high": 12.0,
                "low": 10.0,
                "close": 11.5,
                "volume": 2_000_000,
                "datetime": t1,
            },
        ]
    }
    df = price_history_to_dataframe(payload, years=2.0)
    assert not df.empty
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert len(df) == 2
    assert df["Close"].iloc[-1] == 11.5


def test_use_schwab_for_symbol_respects_env():
    keys = ("SCHWAB_MARKET_DATA", "SCHWAB_CLIENT_ID", "SCHWAB_CLIENT_SECRET")
    saved = {k: os.environ.get(k) for k in keys}
    try:
        for k in keys:
            os.environ.pop(k, None)
        assert use_schwab_for_symbol("AAPL") is False

        os.environ["SCHWAB_MARKET_DATA"] = "1"
        os.environ["SCHWAB_CLIENT_ID"] = "x"
        os.environ["SCHWAB_CLIENT_SECRET"] = "y"
        assert use_schwab_for_symbol("AAPL") is True
        assert use_schwab_for_symbol("BTC-USD") is False
        assert use_schwab_for_symbol("GC=F") is False
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


if __name__ == "__main__":
    test_price_history_to_dataframe_shape()
    test_use_schwab_for_symbol_respects_env()
    print("schwab_market_data tests passed.")
