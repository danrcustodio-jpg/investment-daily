"""Tests for daily OHLCV snapshot + merged daily tail (no live Yahoo in merge test)."""

import pandas as pd


def test_normalize_daily_index_strips_tz():
    from strategy_engine import _normalize_daily_index

    ts = pd.Timestamp("2025-06-10 16:00:00", tz="America/New_York")
    df = pd.DataFrame({"Close": [1.0]}, index=[ts])
    out = _normalize_daily_index(df)
    assert len(out) == 1
    assert out.index[0] == pd.Timestamp("2025-06-10")


def test_merge_recent_daily_prefers_recent_values(monkeypatch):
    import strategy_engine as se

    base = pd.DataFrame(
        {
            "Open": [1.0],
            "High": [2.0],
            "Low": [0.5],
            "Close": [1.5],
            "Volume": [100.0],
        },
        index=[pd.Timestamp("2025-06-02")],
    )
    upd = pd.DataFrame(
        {
            "Open": [10.0],
            "High": [20.0],
            "Low": [9.0],
            "Close": [15.0],
            "Volume": [999.0],
        },
        index=[pd.Timestamp("2025-06-02")],
    )

    class FTicker:
        def __init__(self, _s):
            pass

        def history(self, period, interval, auto_adjust=False):
            return upd.copy()

    monkeypatch.setattr(se.yf, "Ticker", lambda _sym: FTicker(_sym))
    merged = se.merge_recent_daily_bars(base, "FAKE")
    row = merged.loc[merged.index[0]]
    assert float(row["Close"]) == 15.0
    assert float(row["Volume"]) == 999.0


def test_reset_signal_overlay_for_reapply():
    from strategy_engine import _reset_signal_overlay_for_reapply

    s = {
        "ticker": "X",
        "confidence": 75.0,
        "confidence_base": 60.0,
        "confidence_adj": 15.0,
        "confidence_adj_reason": "COT boost",
    }
    _reset_signal_overlay_for_reapply([s])
    assert s["confidence"] == 60.0
    assert s["confidence_base"] == 60.0
    assert s["confidence_adj"] == 0.0
    assert s["confidence_adj_reason"] == ""
