"""
Strategy Engine  —  powered by pandas-ta
Uses the pandas-ta library (130+ indicators) for all technical calculations
instead of manual implementations.  Backtesting computes proper Sharpe Ratio,
Max Drawdown, Sortino Ratio, and Profit Factor via numpy.

New strategies vs. previous version:
  + ADX Trend Strength  (trend quality filter)
  + Stochastic RSI      (faster / more sensitive than plain RSI)
  + VWAP Deviation      (institutional price anchor)
"""

import logging
import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pandas_ta as ta          # pip install pandas-ta
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

logger = logging.getLogger(__name__)

# ─── Strategy educational links ───────────────────────────────────────────────

STRATEGY_LINKS: Dict[str, str] = {
    "RSI Oversold":
        "https://www.investopedia.com/terms/r/rsi.asp",
    "RSI Overbought":
        "https://www.investopedia.com/terms/r/rsi.asp",
    "Stochastic RSI Oversold":
        "https://www.investopedia.com/terms/s/stochrsi.asp",
    "Stochastic RSI Overbought":
        "https://www.investopedia.com/terms/s/stochrsi.asp",
    "MACD Bullish Crossover":
        "https://www.investopedia.com/terms/m/macd.asp",
    "MACD Bearish Crossover":
        "https://www.investopedia.com/terms/m/macd.asp",
    "Golden Cross":
        "https://www.investopedia.com/terms/g/goldencross.asp",
    "Death Cross":
        "https://www.investopedia.com/terms/d/deathcross.asp",
    "Bollinger Lower Band Touch":
        "https://www.investopedia.com/terms/b/bollingerbands.asp",
    "Bollinger Upper Band Touch":
        "https://www.investopedia.com/terms/b/bollingerbands.asp",
    "52-Week Breakout":
        "https://www.investopedia.com/terms/b/breakout.asp",
    "ADX Strong Trend — Bullish":
        "https://www.investopedia.com/terms/a/adx.asp",
    "ADX Strong Trend — Bearish":
        "https://www.investopedia.com/terms/a/adx.asp",
    "VWAP Deviation — Oversold":
        "https://www.investopedia.com/terms/v/vwap.asp",
    "VWAP Deviation — Overbought":
        "https://www.investopedia.com/terms/v/vwap.asp",
}

VOLUME_SPIKE_LINK = "https://www.investopedia.com/terms/v/volumeoftrade.asp"


def strategy_learn_link(strategy_name: str, style: str = "badge") -> str:
    url = STRATEGY_LINKS.get(strategy_name)
    if not url and "Volume Spike" in strategy_name:
        url = VOLUME_SPIKE_LINK
    if not url:
        return ""
    if style == "badge":
        return (
            f'<a href="{url}" target="_blank" rel="noopener"'
            f' style="display:inline-block;background:#1e3a5f;color:#60a5fa;'
            f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;'
            f'text-decoration:none;letter-spacing:0.3px;border:1px solid #2563eb40;'
            f'white-space:nowrap">Learn More &#8599;</a>'
        )
    return (
        f'<a href="{url}" target="_blank" rel="noopener"'
        f' style="color:#60a5fa;font-size:12px;text-decoration:underline">'
        f'What is this? &#8599;</a>'
    )

# ─── Tickers to scan ─────────────────────────────────────────────────────────

SCAN_TICKERS: Dict[str, str] = {
    "NVDA":    "NVIDIA",
    "META":    "Meta",
    "TSLA":    "Tesla",
    "AVGO":    "Broadcom",
    "AAPL":    "Apple",
    "MSFT":    "Microsoft",
    "AMZN":    "Amazon",
    "GOOGL":   "Alphabet",
    "PLTR":    "Palantir",
    "IONQ":    "IonQ",
    "RKLB":    "Rocket Lab",
    "SMCI":    "Super Micro Computer",
    "SPY":     "S&P 500 ETF",
    "QQQ":     "NASDAQ ETF",
    "IWM":     "Russell 2000 ETF",
    "SMH":     "Semiconductors (SMH)",
    "ARKK":    "ARK Innovation",
    "XBI":     "Biotech (XBI)",
    "XLE":     "Energy (XLE)",
    "XLK":     "Tech (XLK)",
    "TQQQ":    "3x NASDAQ (TQQQ)",
    "UPRO":    "3x S&P (UPRO)",
    "SOXL":    "3x Semis (SOXL)",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "GC=F":    "Gold",
    "CL=F":    "Crude Oil",
}

# ─── Backtesting with proper statistics ───────────────────────────────────────

RISK_FREE_RATE_DAILY = 0.05 / 252   # ~5% annual risk-free rate


def backtest_signal(
    closes: pd.Series,
    signal_mask: pd.Series,
    forward_days: List[int] = [5, 20],
) -> Dict:
    """
    Given a boolean mask of signal dates, compute forward return statistics
    including Sharpe Ratio, Max Drawdown, Sortino Ratio, and Profit Factor.
    All metrics are computed from the population of individual trade returns.
    """
    signal_dates = signal_mask[signal_mask == True].index
    if len(signal_dates) < 4:
        return {"count": int(len(signal_dates)), "insufficient_data": True}

    results: Dict = {"count": int(len(signal_dates))}

    for fwd in forward_days:
        trade_returns: List[float] = []
        for dt in signal_dates:
            try:
                idx     = closes.index.get_loc(dt)
                fwd_idx = idx + fwd
                if fwd_idx < len(closes):
                    r = (float(closes.iloc[fwd_idx]) / float(closes.iloc[idx]) - 1) * 100
                    trade_returns.append(r)
            except Exception:
                continue

        n = len(trade_returns)
        if n < 3:
            continue

        arr       = np.array(trade_returns)
        wins      = arr[arr > 0]
        losses    = arr[arr < 0]
        mean_r    = float(np.mean(arr))
        std_r     = float(np.std(arr, ddof=1)) if n > 1 else 0.0
        rf        = RISK_FREE_RATE_DAILY * fwd * 100  # risk-free for the forward period

        # Sharpe (annualised to the forward window)
        periods_per_year = 252 / fwd
        sharpe = (
            (mean_r - rf) / std_r * np.sqrt(periods_per_year)
            if std_r > 0 else 0.0
        )

        # Sortino (downside deviation only)
        downside = arr[arr < rf]
        down_std = float(np.std(downside, ddof=1)) if len(downside) > 1 else 0.0
        sortino  = (
            (mean_r - rf) / down_std * np.sqrt(periods_per_year)
            if down_std > 0 else sharpe
        )

        # Profit Factor
        gross_win  = float(np.sum(wins))   if len(wins)   > 0 else 0.0
        gross_loss = float(np.sum(losses)) if len(losses) > 0 else -1e-9
        profit_factor = gross_win / abs(gross_loss) if gross_loss < 0 else float("inf")

        # Max Drawdown (from equity curve of equal-size trades)
        equity        = np.cumprod(1 + arr / 100)
        rolling_max   = np.maximum.accumulate(equity)
        drawdowns     = (equity - rolling_max) / rolling_max * 100
        max_drawdown  = float(np.min(drawdowns))

        results[f"{fwd}d"] = {
            "win_rate":      round(len(wins) / n * 100, 1),
            "avg_return":    round(mean_r, 2),
            "std_return":    round(std_r, 2),
            "sharpe":        round(sharpe, 2),
            "sortino":       round(sortino, 2),
            "profit_factor": round(min(profit_factor, 99.9), 2),
            "max_drawdown":  round(max_drawdown, 2),
            "count":         n,
        }

    return results


def confidence_score(bt: Dict) -> float:
    """
    Composite 0-100 score.  Weights:
      40% → 5-day win rate
      20% → 5-day Sharpe (capped at 2.0 → 20pts)
      20% → 20-day win rate
      20% → profit factor (capped at 3.0 → 20pts)
    """
    if bt.get("insufficient_data") or "5d" not in bt:
        return 0.0
    d5  = bt["5d"]
    d20 = bt.get("20d", {})

    score  = d5["win_rate"] * 0.40
    score += min(max(d5["sharpe"], 0), 2.0) / 2.0 * 20
    if d20:
        score += d20["win_rate"] * 0.20
    pf     = d5.get("profit_factor", 1.0)
    score += min(max(pf - 1.0, 0), 2.0) / 2.0 * 20

    return round(score, 1)

# ─── Strategy Detectors (all using pandas-ta) ────────────────────────────────

def _make_signal(
    symbol, name, strategy, direction, indicator, detail, implication, bt
) -> Dict:
    return {
        "strategy":    strategy,
        "direction":   direction,
        "ticker":      symbol,
        "name":        name,
        "indicator":   indicator,
        "detail":      detail,
        "implication": implication,
        "backtest":    bt,
        "confidence":  confidence_score(bt),
    }


def detect_rsi(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    signals = []
    rsi_col = "RSI_14"
    if rsi_col not in df.columns or df[rsi_col].isna().iloc[-1]:
        return signals

    rsi   = df[rsi_col]
    price = df["Close"]
    cur   = float(rsi.iloc[-1])

    if cur < 32:
        bt = backtest_signal(price, rsi < 32)
        signals.append(_make_signal(
            symbol, name,
            "RSI Oversold", "BULLISH",
            f"RSI = {cur:.1f}  (oversold zone < 32)",
            f"RSI dropped to {cur:.1f}, indicating the asset has been sold off "
            f"more than its recent momentum typically sustains. Price is "
            f"statistically stretched to the downside.",
            "Historical mean-reversion setup. Watch for RSI turning up as entry confirmation.",
            bt,
        ))
    elif cur > 68:
        bt = backtest_signal(price, rsi > 68)
        signals.append(_make_signal(
            symbol, name,
            "RSI Overbought", "BEARISH",
            f"RSI = {cur:.1f}  (overbought zone > 68)",
            f"RSI reached {cur:.1f}, indicating sustained buying momentum that "
            f"may be outpacing fundamental support. Buyers are historically exhausted "
            f"at these levels.",
            "Consider partial profit-taking or tightening stops.",
            bt,
        ))
    return signals


def detect_stoch_rsi(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    """
    Stochastic RSI — faster and more sensitive than plain RSI.
    Uses the STOCHRSIk_14_14_3_3 column from pandas-ta.
    """
    signals = []
    k_col = "STOCHRSIk_14_14_3_3"
    d_col = "STOCHRSId_14_14_3_3"
    if k_col not in df.columns or df[k_col].isna().iloc[-1]:
        return signals

    k     = df[k_col]
    price = df["Close"]
    cur_k = float(k.iloc[-1])
    prev_k = float(k.iloc[-2]) if len(k) > 1 else cur_k

    # Oversold: StochRSI < 20 and starting to turn up
    if cur_k < 20 and cur_k >= prev_k - 5:
        mask = k < 20
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Stochastic RSI Oversold", "BULLISH",
            f"Stoch RSI K = {cur_k:.1f}  (oversold < 20)",
            f"The Stochastic RSI — a faster, more sensitive version of RSI — "
            f"is at {cur_k:.1f}, deep in oversold territory. This catches "
            f"short-term reversals earlier than standard RSI.",
            "Short-term bounce likely. Stoch RSI crossing back above 20 is the confirmation trigger.",
            bt,
        ))
    elif cur_k > 80 and cur_k <= prev_k + 5:
        mask = k > 80
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Stochastic RSI Overbought", "BEARISH",
            f"Stoch RSI K = {cur_k:.1f}  (overbought > 80)",
            f"Stochastic RSI at {cur_k:.1f} — the fastest momentum indicator "
            f"we track — is signaling overbought conditions. Short-term traders "
            f"historically fade these levels.",
            "Watch for Stoch RSI crossing back below 80 as a short-term sell signal.",
            bt,
        ))
    return signals


def detect_macd(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    signals = []
    macd_col = "MACD_12_26_9"
    sig_col  = "MACDs_12_26_9"
    if macd_col not in df.columns or df[macd_col].isna().iloc[-1]:
        return signals

    macd  = df[macd_col]
    sig   = df[sig_col]
    price = df["Close"]

    # Bullish crossover today
    if macd.iloc[-1] > sig.iloc[-1] and macd.iloc[-2] <= sig.iloc[-2]:
        mask = (macd > sig) & (macd.shift(1) <= sig.shift(1))
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "MACD Bullish Crossover", "BULLISH",
            f"MACD {float(macd.iloc[-1]):.3f} crossed above Signal {float(sig.iloc[-1]):.3f}",
            f"The MACD line (12-day EMA minus 26-day EMA) crossed above its "
            f"9-day signal line today. This crossover indicates that short-term "
            f"momentum is accelerating faster than the recent trend.",
            "Momentum shifting upward — often signals the start of a short-to-medium term rally.",
            bt,
        ))
    elif macd.iloc[-1] < sig.iloc[-1] and macd.iloc[-2] >= sig.iloc[-2]:
        mask = (macd < sig) & (macd.shift(1) >= sig.shift(1))
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "MACD Bearish Crossover", "BEARISH",
            f"MACD {float(macd.iloc[-1]):.3f} crossed below Signal {float(sig.iloc[-1]):.3f}",
            f"The MACD line crossed below its signal line today — upward momentum "
            f"is weakening relative to the recent trend. A common signal that "
            f"selling pressure is building.",
            "Consider reducing exposure. Watch for price to break below recent support.",
            bt,
        ))
    return signals


def detect_ma_cross(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    signals = []
    sma50_col  = "SMA_50"
    sma200_col = "SMA_200"
    if sma50_col not in df.columns or df[sma50_col].isna().iloc[-1]:
        return signals
    if sma200_col not in df.columns or df[sma200_col].isna().iloc[-1]:
        return signals

    ma50  = df[sma50_col]
    ma200 = df[sma200_col]
    price = df["Close"]

    if ma50.iloc[-1] > ma200.iloc[-1] and ma50.iloc[-2] <= ma200.iloc[-2]:
        mask = (ma50 > ma200) & (ma50.shift(1) <= ma200.shift(1))
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Golden Cross", "BULLISH",
            f"50-day SMA {float(ma50.iloc[-1]):.2f} crossed above 200-day SMA {float(ma200.iloc[-1]):.2f}",
            f"The Golden Cross — one of the most widely followed signals in "
            f"technical analysis. The 50-day simple moving average crossed above "
            f"the 200-day, confirming a long-term trend reversal to bullish.",
            "Institutional algorithms often trigger buy orders on this signal. Strong long-term setup.",
            bt,
        ))
    elif ma50.iloc[-1] < ma200.iloc[-1] and ma50.iloc[-2] >= ma200.iloc[-2]:
        mask = (ma50 < ma200) & (ma50.shift(1) >= ma200.shift(1))
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Death Cross", "BEARISH",
            f"50-day SMA {float(ma50.iloc[-1]):.2f} crossed below 200-day SMA {float(ma200.iloc[-1]):.2f}",
            f"The Death Cross — the bearish counterpart to the Golden Cross. "
            f"The 50-day SMA has crossed below the 200-day, signaling a "
            f"long-term shift toward downward momentum.",
            "Long-term trend turning bearish. Consider reducing long positions.",
            bt,
        ))
    return signals


def detect_bollinger(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    signals = []
    lower_col = "BBL_20_2.0"
    upper_col = "BBU_20_2.0"
    if lower_col not in df.columns or df[lower_col].isna().iloc[-1]:
        return signals

    lower = df[lower_col]
    upper = df[upper_col]
    price = df["Close"]
    cur   = float(price.iloc[-1])

    if cur <= float(lower.iloc[-1]) * 1.015:
        pct_below = (float(lower.iloc[-1]) - cur) / float(lower.iloc[-1]) * 100
        mask = price <= lower * 1.015
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Bollinger Lower Band Touch", "BULLISH",
            f"Price {cur:.2f} at/below Lower BB {float(lower.iloc[-1]):.2f}  ({abs(pct_below):.1f}% below 20-day MA)",
            f"Price touched the lower Bollinger Band — {abs(pct_below):.1f}% below "
            f"its 20-day moving average. Bollinger Bands use 2 standard deviations, "
            f"so statistically only ~5% of closes should reach this level.",
            "Mean reversion opportunity. Price tends to snap back toward the 20-day MA midline.",
            bt,
        ))
    elif cur >= float(upper.iloc[-1]) * 0.985:
        pct_above = (cur - float(upper.iloc[-1])) / float(upper.iloc[-1]) * 100
        mask = price >= upper * 0.985
        bt   = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Bollinger Upper Band Touch", "BEARISH",
            f"Price {cur:.2f} at/above Upper BB {float(upper.iloc[-1]):.2f}  ({abs(pct_above):.1f}% above 20-day MA)",
            f"Price touched the upper Bollinger Band — {abs(pct_above):.1f}% above "
            f"its 20-day moving average. Statistically extended to the upside within "
            f"recent volatility range.",
            "Watch for mean reversion pullback toward the 20-day midline.",
            bt,
        ))
    return signals


def detect_adx(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    """
    NEW — ADX (Average Directional Index)
    Measures trend STRENGTH rather than direction.
    ADX > 25 = strong trend; combines with DI+/DI- to confirm direction.
    """
    signals = []
    adx_col = "ADX_14"
    dmp_col = "DMP_14"   # positive directional movement (DI+)
    dmn_col = "DMN_14"   # negative directional movement (DI-)
    if adx_col not in df.columns or df[adx_col].isna().iloc[-1]:
        return signals

    adx   = float(df[adx_col].iloc[-1])
    dmp   = float(df[dmp_col].iloc[-1]) if dmp_col in df.columns else None
    dmn   = float(df[dmn_col].iloc[-1]) if dmn_col in df.columns else None
    price = df["Close"]

    if adx > 25 and dmp is not None and dmn is not None:
        if dmp > dmn:
            # Strong uptrend
            mask = (df[adx_col] > 25) & (df.get(dmp_col, pd.Series()) > df.get(dmn_col, pd.Series()))
            bt   = backtest_signal(price, mask.fillna(False))
            signals.append(_make_signal(
                symbol, name,
                "ADX Strong Trend — Bullish", "BULLISH",
                f"ADX = {adx:.1f}  (strong trend > 25) | DI+ {dmp:.1f} > DI- {dmn:.1f}",
                f"The ADX is at {adx:.1f}, indicating a strong and accelerating "
                f"uptrend. DI+ ({dmp:.1f}) exceeds DI- ({dmn:.1f}), confirming "
                f"buyers are in control. ADX above 25 means the trend has real "
                f"institutional momentum behind it.",
                "Trend-following entry: the move has strength. Ride with stops below recent swing lows.",
                bt,
            ))
        elif dmn > dmp:
            # Strong downtrend
            mask = (df[adx_col] > 25) & (df.get(dmn_col, pd.Series()) > df.get(dmp_col, pd.Series()))
            bt   = backtest_signal(price, mask.fillna(False))
            signals.append(_make_signal(
                symbol, name,
                "ADX Strong Trend — Bearish", "BEARISH",
                f"ADX = {adx:.1f}  (strong trend > 25) | DI- {dmn:.1f} > DI+ {dmp:.1f}",
                f"The ADX is at {adx:.1f}, confirming a strong downtrend. "
                f"DI- ({dmn:.1f}) exceeds DI+ ({dmp:.1f}), meaning sellers are "
                f"dominating with institutional momentum.",
                "Avoid buying into this trend. Consider shorts or wait for ADX to weaken below 20.",
                bt,
            ))
    return signals


def detect_vwap(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    """
    NEW — VWAP Deviation
    VWAP (Volume-Weighted Average Price) is the institutional benchmark price.
    A significant deviation below VWAP = institutions getting a discount.
    pandas-ta computes VWAP daily; we use a rolling 20-day proxy.
    """
    signals = []
    if "Volume" not in df.columns or df["Volume"].isna().all():
        return signals

    closes  = df["Close"]
    volumes = df["Volume"].replace(0, np.nan)

    # Rolling 20-day VWAP proxy
    typical  = (df["High"] + df["Low"] + df["Close"]) / 3
    vwap_20  = (typical * volumes).rolling(20).sum() / volumes.rolling(20).sum()

    if vwap_20.isna().iloc[-1]:
        return signals

    price    = float(closes.iloc[-1])
    vwap_val = float(vwap_20.iloc[-1])
    dev_pct  = (price - vwap_val) / vwap_val * 100

    if dev_pct < -4.0:
        mask = (closes - vwap_20) / vwap_20 * 100 < -4.0
        bt   = backtest_signal(closes, mask.fillna(False))
        signals.append(_make_signal(
            symbol, name,
            "VWAP Deviation — Oversold", "BULLISH",
            f"Price {price:.2f} is {abs(dev_pct):.1f}% below 20-day VWAP ({vwap_val:.2f})",
            f"The price is {abs(dev_pct):.1f}% below the 20-day Volume-Weighted "
            f"Average Price — the benchmark price institutional traders (funds, "
            f"banks, algorithms) use. Trading below VWAP means buyers are getting "
            f"a discount relative to where most volume traded.",
            "Institutions often step in to buy below VWAP. Strong mean-reversion setup.",
            bt,
        ))
    elif dev_pct > 4.0:
        mask = (closes - vwap_20) / vwap_20 * 100 > 4.0
        bt   = backtest_signal(closes, mask.fillna(False))
        signals.append(_make_signal(
            symbol, name,
            "VWAP Deviation — Overbought", "BEARISH",
            f"Price {price:.2f} is {abs(dev_pct):.1f}% above 20-day VWAP ({vwap_val:.2f})",
            f"The price is {abs(dev_pct):.1f}% above the VWAP — institutional "
            f"traders are paying a premium. Algorithms that trade against VWAP "
            f"will begin selling to bring price back toward equilibrium.",
            "Watch for price to revert toward VWAP. Momentum could be exhausted.",
            bt,
        ))
    return signals


def detect_breakout(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    signals = []
    closes = df["Close"]
    if len(closes) < 253:
        return signals

    high_52w = float(closes.iloc[-252:-1].max())
    price    = float(closes.iloc[-1])

    if price > high_52w:
        pct_above = (price - high_52w) / high_52w * 100
        mask = closes == closes.rolling(252).max()
        bt   = backtest_signal(closes, mask)
        signals.append(_make_signal(
            symbol, name,
            "52-Week Breakout", "BULLISH",
            f"Price {price:.2f} broke 52-week high {high_52w:.2f}  (+{pct_above:.1f}%)",
            f"Price closed at a new 52-week high of {price:.2f}, surpassing the "
            f"previous high of {high_52w:.2f}. There is no overhead resistance — "
            f"no prior sellers sitting at these prices waiting to exit.",
            "Strong momentum signal. Institutions often chase breakouts. Trend-follow with stops.",
            bt,
        ))
    return signals


def detect_volume_spike(symbol: str, name: str, df: pd.DataFrame) -> List[Dict]:
    signals = []
    if "Volume" not in df.columns or len(df) < 22:
        return signals

    vol      = df["Volume"].replace(0, np.nan)
    closes   = df["Close"]
    avg_vol  = vol.rolling(20).mean()

    if avg_vol.isna().iloc[-1] or float(avg_vol.iloc[-1]) == 0:
        return signals

    cur_vol   = float(vol.iloc[-1])
    vol_ratio = cur_vol / float(avg_vol.iloc[-1])
    day_ret   = (float(closes.iloc[-1]) / float(closes.iloc[-2]) - 1) * 100

    if vol_ratio >= 2.0 and abs(day_ret) >= 2.0:
        direction = "BULLISH" if day_ret > 0 else "BEARISH"
        mask = (vol >= avg_vol * 2.0) & (closes.pct_change().abs() >= 0.02)
        bt   = backtest_signal(closes, mask.fillna(False))
        signals.append(_make_signal(
            symbol, name,
            f"Volume Spike + {'Surge' if day_ret > 0 else 'Drop'}", direction,
            f"Volume {vol_ratio:.1f}x 20-day avg  |  Price {day_ret:+.1f}% today",
            f"Today's volume ({cur_vol:,.0f} shares) is {vol_ratio:.1f}× the "
            f"20-day average, accompanied by a {day_ret:+.1f}% price move. "
            f"Unusual volume signals institutional participation — funds, hedge "
            f"funds, or algorithmic programs driving price with conviction.",
            "High-volume moves carry conviction and often continue. The direction of the move is the signal.",
            bt,
        ))
    return signals

# ─── Main Scanner ─────────────────────────────────────────────────────────────

def scan_ticker(symbol: str, name: str) -> List[Dict]:
    """Fetch 2 years of data, compute all pandas-ta indicators, run all strategies."""
    try:
        raw = yf.Ticker(symbol).history(period="2y")
        if raw.empty or len(raw) < 50:
            return []
    except Exception as exc:
        logger.warning(f"  Could not fetch {symbol}: {exc}")
        return []

    df = raw.copy()

    # Compute all indicators in one pass using pandas-ta
    try:
        df.ta.rsi(length=14, append=True)
        df.ta.stochrsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.sma(length=50,  append=True)
        df.ta.sma(length=200, append=True)
        df.ta.bbands(length=20, std=2.0, append=True)
        df.ta.adx(length=14, append=True)
    except Exception as exc:
        logger.warning(f"  pandas-ta error on {symbol}: {exc}")

    signals: List[Dict] = []
    signals += detect_rsi(symbol, name, df)
    signals += detect_stoch_rsi(symbol, name, df)
    signals += detect_macd(symbol, name, df)
    signals += detect_ma_cross(symbol, name, df)
    signals += detect_bollinger(symbol, name, df)
    signals += detect_adx(symbol, name, df)
    signals += detect_vwap(symbol, name, df)
    signals += detect_breakout(symbol, name, df)
    signals += detect_volume_spike(symbol, name, df)

    return signals


def run_full_scan(tickers: Optional[Dict[str, str]] = None) -> List[Dict]:
    """
    Scan all tickers. Returns signals sorted by confidence (highest first),
    filtered to confidence >= 45.
    """
    if tickers is None:
        tickers = SCAN_TICKERS

    logger.info(f"Scanning {len(tickers)} tickers across 9 strategies (pandas-ta) ...")
    all_signals: List[Dict] = []

    for symbol, name in tickers.items():
        try:
            sigs = scan_ticker(symbol, name)
            if sigs:
                logger.info(f"  {symbol}: {len(sigs)} signal(s)")
            all_signals.extend(sigs)
        except Exception as exc:
            logger.warning(f"  Scan error {symbol}: {exc}")

    filtered = [s for s in all_signals if s.get("confidence", 0) >= 45]
    filtered.sort(key=lambda s: (
        0 if s["direction"] == "BULLISH" else 1,
        -s.get("confidence", 0),
    ))

    logger.info(f"Scan complete: {len(all_signals)} raw → {len(filtered)} after confidence filter")
    return filtered


def format_backtest_summary(bt: Dict) -> str:
    if bt.get("insufficient_data") or "5d" not in bt:
        return f"Insufficient history ({bt.get('count', 0)} signals)"
    d5 = bt["5d"]
    return (
        f"5d: {d5['win_rate']}% wins | avg {d5['avg_return']:+.1f}% | "
        f"Sharpe {d5['sharpe']:.2f} | MaxDD {d5['max_drawdown']:.1f}%"
    )
