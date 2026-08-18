"""Aroon should alert only on regime-start days, not every day the trend is on."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy_engine import _regime_start, detect_aroon


def _frame(up, down, close=100.0) -> pd.DataFrame:
    n = len(up)
    idx = pd.date_range("2024-01-02", periods=n, freq="B")
    return pd.DataFrame(
        {
            "AROONU_25": up,
            "AROOND_25": down,
            "Close": [close + i * 0.1 for i in range(n)],
        },
        index=idx,
    )


def test_regime_start_is_first_day_only():
    active = pd.Series([False, True, True, True, False, True])
    starts = _regime_start(active)
    assert starts.tolist() == [False, True, False, False, False, True]


def test_aroon_silent_while_uptrend_continues():
    # Regime already on for several days — should not emit today.
    df = _frame(
        up=[80, 84, 88, 92, 88],
        down=[20, 16, 12, 8, 12],
    )
    sigs = detect_aroon("VOO", "Vanguard S&P 500 ETF", df)
    assert sigs == []


def test_aroon_fires_on_uptrend_start():
    df = _frame(
        up=[40, 50, 60, 80],
        down=[60, 50, 40, 20],
    )
    sigs = detect_aroon("VOO", "Vanguard S&P 500 ETF", df)
    assert len(sigs) == 1
    assert sigs[0]["strategy"] == "Aroon — Strong Uptrend"
    assert sigs[0]["direction"] == "BULLISH"


def test_aroon_fires_on_downtrend_start():
    df = _frame(
        up=[60, 50, 40, 20],
        down=[40, 50, 60, 80],
    )
    sigs = detect_aroon("QQQ", "NASDAQ ETF", df)
    assert len(sigs) == 1
    assert sigs[0]["strategy"] == "Aroon — Strong Downtrend"
    assert sigs[0]["direction"] == "BEARISH"


if __name__ == "__main__":
    test_regime_start_is_first_day_only()
    test_aroon_silent_while_uptrend_continues()
    test_aroon_fires_on_uptrend_start()
    test_aroon_fires_on_downtrend_start()
    print("OK: Aroon fires only on regime-start days.")
