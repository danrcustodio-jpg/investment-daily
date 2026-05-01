"""
Strategy Engine  —  powered by pandas-ta
Uses the pandas-ta library (130+ indicators) for all technical calculations
instead of manual implementations.  Backtesting computes proper Sharpe Ratio,
Max Drawdown, Sortino Ratio, and Profit Factor via numpy.

The scan combines trend, momentum, volatility, and volume/flow tools (30 detector
modules, 2-year backtest per rule). The daily email includes methodology_newsletter_html().
"""

import datetime
import json
import logging
import urllib.request
import warnings

import numpy as np
import pandas as pd
import pandas_ta as ta  # noqa: F401 - importing registers the DataFrame .ta accessor
import yfinance as yf
from positioning_data import get_cot_positioning_summary

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

logger = logging.getLogger(__name__)

# Positioning-based score overlay (small and bounded so core backtest score remains primary).
POSITIONING_ADJ_MAX = 6.0
POSITIONING_ADJ_BY_CROWDING = {
    "crowded": {"follow": -4.0, "fade": 3.0},
    "extreme": {"follow": -6.0, "fade": 5.0},
}
POSITIONING_PROXY_MAP: dict[str, str] = {
    "SPY": "spx",
    "UPRO": "spx",
    "QQQ": "spx",
    "TQQQ": "spx",
    "IWM": "spx",
    "GC=F": "gold",
    "CL=F": "crude",
    "XLE": "crude",
}

# ─── Strategy educational links ───────────────────────────────────────────────

STRATEGY_LINKS: dict[str, str] = {
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
    "Williams %R — Oversold":
        "https://www.investopedia.com/terms/w/williamsr.asp",
    "Williams %R — Overbought":
        "https://www.investopedia.com/terms/w/williamsr.asp",
    "CCI — Extreme Oversold":
        "https://www.investopedia.com/terms/c/commoditychannelindex.asp",
    "CCI — Extreme Overbought":
        "https://www.investopedia.com/terms/c/commoditychannelindex.asp",
    "MFI — Oversold":
        "https://www.investopedia.com/terms/m/mfi.asp",
    "MFI — Overbought":
        "https://www.investopedia.com/terms/m/mfi.asp",
    "Chaikin Money Flow — Bullish":
        "https://www.investopedia.com/articles/active-trading/201403/introduction-chaikin-money-flow.asp",
    "Chaikin Money Flow — Bearish":
        "https://www.investopedia.com/articles/active-trading/201403/introduction-chaikin-money-flow.asp",
    "Aroon — Strong Uptrend":
        "https://www.investopedia.com/terms/a/aroon.asp",
    "Aroon — Strong Downtrend":
        "https://www.investopedia.com/terms/a/aroon.asp",
    "EMA 9/21 — Bullish Cross":
        "https://www.investopedia.com/terms/m/movingaverage.asp",
    "EMA 9/21 — Bearish Cross":
        "https://www.investopedia.com/terms/m/movingaverage.asp",
    "TRIX — Bullish Cross":
        "https://www.investopedia.com/terms/t/trix.asp",
    "TRIX — Bearish Cross":
        "https://www.investopedia.com/terms/t/trix.asp",
    "OBV — Accumulation":
        "https://www.investopedia.com/terms/o/onbalancevolume.asp",
    "OBV — Distribution":
        "https://www.investopedia.com/terms/o/onbalancevolume.asp",
    "Parabolic SAR — Bullish":
        "https://www.investopedia.com/terms/p/parabolicindicator.asp",
    "Parabolic SAR — Bearish":
        "https://www.investopedia.com/terms/p/parabolicindicator.asp",
    "Stochastic (Full) — Oversold":
        "https://www.investopedia.com/terms/s/stochasticoscillator.asp",
    "Stochastic (Full) — Overbought":
        "https://www.investopedia.com/terms/s/stochasticoscillator.asp",
    "Keltner — Lower Channel Touch":
        "https://www.investopedia.com/terms/k/keltnerchannel.asp",
    "Keltner — Upper Channel Touch":
        "https://www.investopedia.com/terms/k/keltnerchannel.asp",
    "Donchian — 20D High Breakout":
        "https://www.investopedia.com/terms/d/donchianchannels.asp",
    "Donchian — 20D Low Breakdown":
        "https://www.investopedia.com/terms/d/donchianchannels.asp",
    "Supertrend — Bullish Flip":
        "https://www.investopedia.com/technical/indicator-supertrend-7976167",
    "Supertrend — Bearish Flip":
        "https://www.investopedia.com/technical/indicator-supertrend-7976167",
    "PPO — Bullish Cross":
        "https://www.investopedia.com/ask/answers/112814/what-difference-between-ppo-and-macd-indicators.asp",
    "PPO — Bearish Cross":
        "https://www.investopedia.com/ask/answers/112814/what-difference-between-ppo-and-macd-indicators.asp",
    "Awesome Oscillator — Bullish Zero Line":
        "https://www.investopedia.com/terms/a/awesomeoscillator.asp",
    "Awesome Oscillator — Bearish Zero Line":
        "https://www.investopedia.com/terms/a/awesomeoscillator.asp",
    "Elder Force — Bullish":
        "https://www.investopedia.com/articles/trading/11/02-elder-force-index-efi.asp",
    "Elder Force — Bearish":
        "https://www.investopedia.com/articles/trading/11/02-elder-force-index-efi.asp",
    "DPO — Extreme Low":
        "https://www.investopedia.com/terms/d/dpo.asp",
    "DPO — Extreme High":
        "https://www.investopedia.com/terms/d/dpo.asp",
    "Vortex — Bullish":
        "https://www.investopedia.com/articles/technical/11/trading-with-vortex-indicator.asp",
    "Vortex — Bearish":
        "https://www.investopedia.com/articles/technical/11/trading-with-vortex-indicator.asp",
    "ATR — Volatility Surge (Up)":
        "https://www.investopedia.com/terms/a/atr.asp",
    "ATR — Volatility Surge (Down)":
        "https://www.investopedia.com/terms/a/atr.asp",
    "Ulcer Index — Elevated":
        "https://www.investopedia.com/terms/u/ulcerindex.asp",
    "Fisher Transform — Low Extreme":
        "https://www.investopedia.com/terms/f/fisher-transform.asp",
    "Fisher Transform — High Extreme":
        "https://www.investopedia.com/terms/f/fisher-transform.asp",
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


def methodology_newsletter_html() -> str:
    """
    Rich summary of what the engine evaluates — embedded in the daily HTML newsletter.
    """
    n = len(SCAN_TICKERS)
    m = 30
    return f"""
    <div style="background:#0a1628;border-radius:10px;padding:16px 18px;margin-bottom:20px;
                border:1px solid #1e3a5f;line-height:1.65">
      <h2 style="color:#a5b4fc;margin:0 0 8px;font-size:14px;font-weight:800;
                 letter-spacing:0.5px;text-transform:uppercase">
        Technical coverage
      </h2>
      <p style="color:#94a3b8;font-size:12px;margin:0 0 12px">
        Each rule is scored from <strong style="color:#e2e8f0">5-day and 20-day forward returns</strong>
        over ~two years (Sharpe, drawdown, win rate). The headline
        <strong style="color:#e2e8f0">backtest score</strong> (0–100) combines those stats with fixed weights;
        the email shows the point breakdown (5d win %, Sharpe, 20d win %, profit factor), trade count
        <em>n</em>, how many rules agree on direction, and price vs the 200-day MA (50-day when history is short)
        as <strong style="color:#e2e8f0">regime context</strong> only.
        A <strong style="color:#e2e8f0">recent slice</strong> rescores using only the latest 20% of signal dates by time
        (a simple holdout-style check — not a full walk-forward engine).
        <strong style="color:#e2e8f0">{m} strategy detectors</strong> on
        <strong style="color:#e2e8f0">{n} tickers</strong> (plus DEX when configured), pandas-ta.
        Rows group by asset and direction (top rule + runner-up when multiple rules align).
        <strong>Intraday alerts</strong> use score ≥&nbsp;52; the table below uses ≥&nbsp;45.
      </p>
      <ul style="margin:0;padding:0 0 0 18px;color:#cbd5e1;font-size:12px">
        <li><strong style="color:#f1f5f9">Trend &amp; structure:</strong> ADX+DI, 50/200 SMA,
            9/21 EMA, Supertrend, Vortex, Parabolic SAR, 52-week &amp; Donchian breakouts, Aroon</li>
        <li><strong style="color:#f1f5f9">Momentum:</strong> RSI, Stoch RSI, full Stochastic,
            MACD, PPO, TRIX, Williams %R, CCI, MFI, Awesome Oscillator, Elder Force, DPO, Fisher</li>
        <li><strong style="color:#f1f5f9">Volatility &amp; bands:</strong> Bollinger, Keltner channels,
            ATR surge vs baseline, Ulcer index stress</li>
        <li><strong style="color:#f1f5f9">Flow &amp; position:</strong> OBV, Chaikin money flow, VWAP
            deviation, unusual volume spike detection; each row links to a plain-English explainer</li>
      </ul>
    </div>"""


# ─── Tickers to scan ─────────────────────────────────────────────────────────

SCAN_TICKERS: dict[str, str] = {
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
    # New additions
    "APP":     "AppLovin",
    "AMD":     "AMD",
    "CRWD":    "CrowdStrike",
    "ARM":     "ARM Holdings",
    "MRVL":   "Marvell Technology",
    "CEG":     "Constellation Energy",
    "COIN":    "Coinbase",
    "RIOT":    "Riot Platforms",
    "MARA":    "Marathon Digital",
    "XRP-USD": "XRP",
}

# DEX tokens not on yfinance — keyed by display symbol, value is contract address.
# Data is fetched via DexScreener + GeckoTerminal (no API key required).
DEX_TICKERS: dict[str, str] = {
    "SKI": "0x768be13e1680b5ebe0024c42c896e3db59ec0149",   # Ski Mask Dog (Base chain)
}

# ─── Backtesting with proper statistics ───────────────────────────────────────

RISK_FREE_RATE_DAILY = 0.05 / 252   # ~5% annual risk-free rate

# Recent-slice validation: stats computed only on the latest fraction of signal dates (by time).
BACKTEST_HOLDOUT_FRAC = 0.20


def _forward_period_stats(closes: pd.Series, signal_dates, fwd: int) -> dict | None:
    """Trade statistics for one forward window; dates evaluated in chronological order."""
    ordered = sorted(signal_dates)
    trade_returns: list[float] = []
    for dt in ordered:
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
        return None

    arr       = np.array(trade_returns)
    wins      = arr[arr > 0]
    losses    = arr[arr < 0]
    mean_r    = float(np.mean(arr))
    std_r     = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    rf        = RISK_FREE_RATE_DAILY * fwd * 100

    periods_per_year = 252 / fwd
    sharpe = (
        (mean_r - rf) / std_r * np.sqrt(periods_per_year)
        if std_r > 0 else 0.0
    )

    downside = arr[arr < rf]
    down_std = float(np.std(downside, ddof=1)) if len(downside) > 1 else 0.0
    sortino  = (
        (mean_r - rf) / down_std * np.sqrt(periods_per_year)
        if down_std > 0 else sharpe
    )

    gross_win  = float(np.sum(wins))   if len(wins)   > 0 else 0.0
    gross_loss = float(np.sum(losses)) if len(losses) > 0 else -1e-9
    profit_factor = gross_win / abs(gross_loss) if gross_loss < 0 else float("inf")

    equity        = np.cumprod(1 + arr / 100)
    rolling_max   = np.maximum.accumulate(equity)
    drawdowns     = (equity - rolling_max) / rolling_max * 100
    max_drawdown  = float(np.min(drawdowns))

    return {
        "win_rate":      round(len(wins) / n * 100, 1),
        "avg_return":    round(mean_r, 2),
        "std_return":    round(std_r, 2),
        "sharpe":        round(sharpe, 2),
        "sortino":       round(sortino, 2),
        "profit_factor": round(min(profit_factor, 99.9), 2),
        "max_drawdown":  round(max_drawdown, 2),
        "count":         n,
    }


def backtest_signal(
    closes: pd.Series,
    signal_mask: pd.Series,
    forward_days: list[int] | None = None,
    holdout_frac: float | None = None,
) -> dict:
    """
    Given a boolean mask of signal dates, compute forward return statistics
    including Sharpe Ratio, Max Drawdown, Sortino Ratio, and Profit Factor.
    All metrics are computed from the population of individual trade returns.

    When holdout_frac is set (default BACKTEST_HOLDOUT_FRAC), also computes the same
    metrics on the most recent fraction of signal dates by time — a simple out-of-sample-style slice.
    """
    if forward_days is None:
        forward_days = [5, 20]
    if holdout_frac is None:
        holdout_frac = BACKTEST_HOLDOUT_FRAC

    signal_dates = signal_mask[signal_mask].index
    if len(signal_dates) < 4:
        return {"count": int(len(signal_dates)), "insufficient_data": True}

    results: dict = {"count": int(len(signal_dates))}

    for fwd in forward_days:
        st = _forward_period_stats(closes, signal_dates, fwd)
        if st:
            results[f"{fwd}d"] = st

    if holdout_frac > 0 and len(signal_dates) >= 10:
        sd    = signal_dates.sort_values()
        start = int(len(sd) * (1 - holdout_frac))
        ho_idx = sd[start:]
        if len(ho_idx) >= 3:
            ho_body: dict = {}
            for fwd in forward_days:
                st = _forward_period_stats(closes, ho_idx, fwd)
                if st:
                    ho_body[f"{fwd}d"] = st
            if ho_body:
                pct_lab = int(round(holdout_frac * 100))
                results["holdout"] = {
                    **ho_body,
                    "signal_count": len(ho_idx),
                    "span_note": f"last {pct_lab}% of signal dates (by time)",
                }

    return results


def confidence_score(bt: dict) -> float:
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


def confidence_breakdown(bt: dict) -> dict | None:
    """
    Point contributions that sum to confidence_score(bt). Used for transparent UI.
    """
    if bt.get("insufficient_data") or "5d" not in bt:
        return None
    d5  = bt["5d"]
    d20 = bt.get("20d") or {}

    wr5_pts    = d5["win_rate"] * 0.40
    sharpe_pts = min(max(d5["sharpe"], 0), 2.0) / 2.0 * 20
    wr20_pts   = d20["win_rate"] * 0.20 if d20 else 0.0
    pf         = d5.get("profit_factor", 1.0)
    pf_pts     = min(max(pf - 1.0, 0), 2.0) / 2.0 * 20

    total = round(wr5_pts + sharpe_pts + wr20_pts + pf_pts, 1)
    return {
        "total": total,
        "wr5_pts": round(wr5_pts, 1),
        "sharpe_pts": round(sharpe_pts, 1),
        "wr20_pts": round(wr20_pts, 1),
        "pf_pts": round(pf_pts, 1),
        "n_5d": d5.get("count"),
        "has_20d": bool(d20),
    }


def holdout_backtest_score(bt: dict) -> tuple[float | None, int | None]:
    """Same scoring formula applied to the recent holdout slice only (if present)."""
    ho = bt.get("holdout")
    if not ho or "5d" not in ho:
        return None, None
    syn: dict = {"5d": ho["5d"]}
    if ho.get("20d"):
        syn["20d"] = ho["20d"]
    return confidence_score(syn), ho.get("signal_count")


def regime_label(df: pd.DataFrame) -> str:
    """Price vs long moving average — regime context only, not a standalone signal."""
    n = len(df)
    if n < 50:
        return "Thin history"
    w = 200 if n >= 200 else 50
    close = float(df["Close"].iloc[-1])
    ma = float(df["Close"].rolling(w).mean().iloc[-1])
    if pd.isna(ma):
        return "—"
    suf = "" if w == 200 else " · short hist."
    side = "Above" if close > ma else "Below"
    return f"{side} {w}d MA{suf}"

# ─── Strategy Detectors (all using pandas-ta) ────────────────────────────────

def _make_signal(
    symbol, name, strategy, direction, indicator, detail, implication, bt
) -> dict:
    base = confidence_score(bt)
    return {
        "strategy":    strategy,
        "direction":   direction,
        "ticker":      symbol,
        "name":        name,
        "indicator":   indicator,
        "detail":      detail,
        "implication": implication,
        "backtest":    bt,
        "confidence":  base,
        "confidence_base": base,
        "confidence_adj": 0.0,
        "confidence_adj_reason": "",
    }


def _positioning_adjustment_for_signal(signal: dict, cot_summary: dict | None) -> tuple[float, str]:
    """Small score modifier based on weekly COT crowding context."""
    if not cot_summary or cot_summary.get("status") != "ok":
        return 0.0, ""

    ticker = signal.get("ticker", "")
    asset_key = POSITIONING_PROXY_MAP.get(ticker)
    if not asset_key:
        return 0.0, ""

    items = cot_summary.get("items") or []
    item = next((x for x in items if x.get("asset_key") == asset_key), None)
    if not item:
        return 0.0, ""

    crowding = str(item.get("crowding") or "unknown")
    side = str(item.get("crowded_side") or "flat")
    if crowding not in POSITIONING_ADJ_BY_CROWDING or side not in ("long", "short"):
        return 0.0, ""

    direction = signal.get("direction")
    signal_side = "long" if direction == "BULLISH" else ("short" if direction == "BEARISH" else "flat")
    if signal_side == "flat":
        return 0.0, ""

    profile = POSITIONING_ADJ_BY_CROWDING[crowding]
    if signal_side == side:
        points = profile["follow"]
        reason = f"COT {crowding} {side}: follow-crowd penalty"
    else:
        points = profile["fade"]
        reason = f"COT {crowding} {side}: contrarian boost"
    return points, reason


def _apply_positioning_overlay(signals: list[dict], cot_summary: dict | None) -> None:
    """Mutates signal confidence fields in-place."""
    for s in signals:
        base = float(s.get("confidence_base", s.get("confidence", 0.0)))
        points, reason = _positioning_adjustment_for_signal(s, cot_summary)
        points = max(-POSITIONING_ADJ_MAX, min(POSITIONING_ADJ_MAX, points))
        adj = round(base + points, 1)
        s["confidence_base"] = round(base, 1)
        s["confidence_adj"] = round(points, 1)
        s["confidence_adj_reason"] = reason
        s["confidence"] = max(0.0, min(100.0, adj))


def positioning_overlay_diagnostics(signals: list[dict]) -> dict:
    """Summarize how many signals received positioning adjustments."""
    diag = {
        "total": len(signals),
        "adjusted": 0,
        "boosted": 0,
        "penalized": 0,
        "by_ticker": {},
    }
    by_ticker: dict[str, dict] = {}
    for s in signals:
        adj = float(s.get("confidence_adj", 0.0) or 0.0)
        if abs(adj) <= 0:
            continue
        ticker = s.get("ticker", "?")
        bucket = by_ticker.setdefault(
            ticker,
            {"adjusted": 0, "boosted": 0, "penalized": 0},
        )
        diag["adjusted"] += 1
        bucket["adjusted"] += 1
        if adj > 0:
            diag["boosted"] += 1
            bucket["boosted"] += 1
        else:
            diag["penalized"] += 1
            bucket["penalized"] += 1
    diag["by_ticker"] = by_ticker
    return diag


def apply_extended_ta(df: pd.DataFrame) -> None:
    """Append extra pandas-ta columns for Williams %R, CCI, MFI, CMF, Aroon, fast EMA, OBV, TRIX, PSAR, Stochastic."""
    try:
        df.ta.willr(length=14, append=True)
        df.ta.cci(length=20, append=True)
        df.ta.mfi(length=14, append=True)
        df.ta.cmf(length=20, append=True)
        df.ta.aroon(length=25, append=True)
        df.ta.ema(length=9, append=True)
        df.ta.ema(length=21, append=True)
        df.ta.obv(append=True)
        df.ta.trix(length=15, signal=9, append=True)
        df.ta.psar(append=True)
        df.ta.stoch(k=14, d=3, smooth_k=3, append=True)
    except Exception as exc:
        logger.warning(f"  pandas-ta extended stack: {exc}")


def apply_comprehensive_ta(df: pd.DataFrame) -> None:
    """Keltner, Donchian, Supertrend, PPO, Awesome, EFI, DPO, Vortex, ATR, Ulcer, Fisher."""
    try:
        df.ta.kc(length=20, scalar=2, append=True)
        df.ta.donchian(lower_length=20, upper_length=20, append=True)
        df.ta.supertrend(length=10, multiplier=3, append=True)
        df.ta.ppo(fast=12, slow=26, signal=9, append=True)
        df.ta.ao(append=True)
        df.ta.efi(length=13, append=True)
        df.ta.dpo(length=20, append=True)
        df.ta.vortex(length=14, append=True)
        df.ta.atr(length=14, append=True)
        df.ta.ui(length=14, append=True)
        df.ta.fisher(length=9, signal=1, append=True)
    except Exception as exc:
        logger.warning(f"  pandas-ta comprehensive stack: {exc}")


def detect_rsi(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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


def detect_stoch_rsi(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """
    Stochastic RSI — faster and more sensitive than plain RSI.
    Uses the STOCHRSIk_14_14_3_3 column from pandas-ta.
    """
    signals = []
    k_col = "STOCHRSIk_14_14_3_3"
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


def detect_macd(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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
            "The MACD line (12-day EMA minus 26-day EMA) crossed above its "
            "9-day signal line today. This crossover indicates that short-term "
            "momentum is accelerating faster than the recent trend.",
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
            "The MACD line crossed below its signal line today — upward momentum "
            "is weakening relative to the recent trend. A common signal that "
            "selling pressure is building.",
            "Consider reducing exposure. Watch for price to break below recent support.",
            bt,
        ))
    return signals


def detect_ma_cross(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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
            "The Golden Cross — one of the most widely followed signals in "
            "technical analysis. The 50-day simple moving average crossed above "
            "the 200-day, confirming a long-term trend reversal to bullish.",
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
            "The Death Cross — the bearish counterpart to the Golden Cross. "
            "The 50-day SMA has crossed below the 200-day, signaling a "
            "long-term shift toward downward momentum.",
            "Long-term trend turning bearish. Consider reducing long positions.",
            bt,
        ))
    return signals


def detect_bollinger(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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


def detect_adx(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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


def detect_vwap(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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


def detect_breakout(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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


def detect_volume_spike(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
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


def detect_williams_r(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Williams %R — range -100 to 0; extreme oversold / overbought."""
    signals: list[dict] = []
    col = "WILLR_14"
    if col not in df.columns or df[col].isna().iloc[-1]:
        return signals
    w = df[col]
    price = df["Close"]
    cur = float(w.iloc[-1])
    if cur < -80:
        bt = backtest_signal(price, w < -80)
        signals.append(_make_signal(
            symbol, name,
            "Williams %R — Oversold", "BULLISH",
            f"Williams %%R = {cur:.1f}  (oversold < -80)",
            f"Williams %%R is at {cur:.1f}. Readings below -80 show price is closing "
            f"near the 14-day low — classic mean-reversion oversold context.",
            "Watch for a bounce; confirm with higher closes or volume.",
            bt,
        ))
    elif cur > -20:
        bt = backtest_signal(price, w > -20)
        signals.append(_make_signal(
            symbol, name,
            "Williams %R — Overbought", "BEARISH",
            f"Williams %%R = {cur:.1f}  (overbought > -20)",
            "Williams %%R above -20 means closes are hugging the top of the 14-day range — "
            "short-term overextension.",
            "Tighten risk; look for a pullback or consolidation.",
            bt,
        ))
    return signals


def detect_cci(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Commodity Channel Index — extreme readings vs 20-day mean price."""
    signals: list[dict] = []
    col = "CCI_20_0.015"
    if col not in df.columns or df[col].isna().iloc[-1]:
        return signals
    cci = df[col]
    price = df["Close"]
    cur = float(cci.iloc[-1])
    if cur < -100:
        bt = backtest_signal(price, cci < -100)
        signals.append(_make_signal(
            symbol, name,
            "CCI — Extreme Oversold", "BULLISH",
            f"CCI = {cur:.0f}  (below -100)",
            "CCI measures deviation from the 20-day average price. Below -100, "
            "the market is extremely stretched to the downside vs its recent mean.",
            "Common bounce zone; use price action to confirm a reversal.",
            bt,
        ))
    elif cur > 100:
        bt = backtest_signal(price, cci > 100)
        signals.append(_make_signal(
            symbol, name,
            "CCI — Extreme Overbought", "BEARISH",
            f"CCI = {cur:.0f}  (above +100)",
            "Above +100, price is anomalously high vs its 20-day average — a statistical overextension.",
            "Fade or de-risk; mean reversion often follows.",
            bt,
        ))
    return signals


def detect_mfi(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Money Flow Index — volume-weighted RSI-style oscillator."""
    signals: list[dict] = []
    col = "MFI_14"
    if col not in df.columns or df[col].isna().iloc[-1]:
        return signals
    mfi = df[col]
    price = df["Close"]
    cur = float(mfi.iloc[-1])
    if cur < 20:
        bt = backtest_signal(price, mfi < 20)
        signals.append(_make_signal(
            symbol, name,
            "MFI — Oversold", "BULLISH",
            f"MFI = {cur:.0f}  (oversold < 20)",
            "MFI combines price and volume. Below 20, selling pressure (by volume) has dominated.",
            "Potential accumulation zone if fundamentals support a bounce.",
            bt,
        ))
    elif cur > 80:
        bt = backtest_signal(price, mfi > 80)
        signals.append(_make_signal(
            symbol, name,
            "MFI — Overbought", "BEARISH",
            f"MFI = {cur:.0f}  (overbought > 80)",
            "Above 80, buying pressure has been extreme — risk of a snapback.",
            "Consider taking partial profits on extended runs.",
            bt,
        ))
    return signals


def detect_cmf(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Chaikin Money Flow — 20-day money-flow accumulation / distribution."""
    signals: list[dict] = []
    col = "CMF_20"
    if col not in df.columns or "Volume" not in df.columns or df[col].isna().iloc[-1]:
        return signals
    cmf = df[col]
    price = df["Close"]
    cur = float(cmf.iloc[-1])
    if cur > 0.1:
        mask = cmf > 0.1
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Chaikin Money Flow — Bullish", "BULLISH",
            f"CMF = {cur:+.2f}  (strong inflow > +0.1)",
            "Chaikin Money Flow is strongly positive: buying pressure has been sustained over 20 days.",
            "Institutional accumulation often coincides; trend continuation possible.",
            bt,
        ))
    elif cur < -0.1:
        mask = cmf < -0.1
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Chaikin Money Flow — Bearish", "BEARISH",
            f"CMF = {cur:+.2f}  (outflow < -0.1)",
            "Sustained net selling pressure over 20 days — distribution in the name.",
            "Avoid catch-the-fall unless thesis changes.",
            bt,
        ))
    return signals


def detect_aroon(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Aroon — time since 25-day high/low; strong when one leg dominates."""
    signals: list[dict] = []
    uc, dc = "AROONU_25", "AROOND_25"
    if uc not in df.columns or df[uc].isna().iloc[-1]:
        return signals
    u, d, price = df[uc], df[dc], df["Close"]
    cu, cd = float(u.iloc[-1]), float(d.iloc[-1])
    if cu > 70 and cu > cd:
        mask = (u > 70) & (u > d)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Aroon — Strong Uptrend", "BULLISH",
            f"Aroon Up {cu:.0f}  vs  Down {cd:.0f}  (Up > 70 & leads)",
            "Aroon Up is high: a new 25-day high was recent; Up is above Down — "
            "momentum favors buyers.",
            "Trend-following: strength until Down catches up or Up rolls over.",
            bt,
        ))
    elif cd > 70 and cd > cu:
        mask = (d > 70) & (d > u)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Aroon — Strong Downtrend", "BEARISH",
            f"Aroon Down {cd:.0f}  vs  Up {cu:.0f}  (Down > 70 & leads)",
            "Aroon Down dominates — new lows are fresh; structural weakness vs highs.",
            "Avoid premature longs; wait for Up to recover or Down to fade.",
            bt,
        ))
    return signals


def detect_ema_fast_cross(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """9 EMA vs 21 EMA — short-term trend shifts."""
    signals: list[dict] = []
    e9c, e21c = "EMA_9", "EMA_21"
    if e9c not in df.columns or e21c not in df.columns or df[e9c].isna().iloc[-1]:
        return signals
    e9, e21, price = df[e9c], df[e21c], df["Close"]
    if e9.iloc[-1] > e21.iloc[-1] and e9.iloc[-2] <= e21.iloc[-2]:
        mask = (e9 > e21) & (e9.shift(1) <= e21.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "EMA 9/21 — Bullish Cross", "BULLISH",
            f"9-EMA {float(e9.iloc[-1]):.2f} crossed above 21-EMA {float(e21.iloc[-1]):.2f}",
            "The faster average crossed the slower to the upside — short-term "
            "momentum is accelerating vs the 3-4 week trend.",
            "Often used for swing entries; size smaller than a Golden Cross (50/200).",
            bt,
        ))
    elif e9.iloc[-1] < e21.iloc[-1] and e9.iloc[-2] >= e21.iloc[-2]:
        mask = (e9 < e21) & (e9.shift(1) >= e21.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "EMA 9/21 — Bearish Cross", "BEARISH",
            f"9-EMA {float(e9.iloc[-1]):.2f} crossed below 21-EMA {float(e21.iloc[-1]):.2f}",
            "Short-term trend rolling over vs the medium band — first line of risk management.",
            "Use as a stop or reduce signal alongside structure.",
            bt,
        ))
    return signals


def detect_trix(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """TRIX / signal line — triple-smoothed rate of change, crossover signals."""
    signals: list[dict] = []
    tc, sc = "TRIX_15_9", "TRIXs_15_9"
    if tc not in df.columns or sc not in df.columns or df[tc].isna().iloc[-1]:
        return signals
    t, ts, price = df[tc], df[sc], df["Close"]
    if t.iloc[-1] > ts.iloc[-1] and t.iloc[-2] <= ts.iloc[-2]:
        mask = (t > ts) & (t.shift(1) <= ts.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "TRIX — Bullish Cross", "BULLISH",
            f"TRIX {float(t.iloc[-1]):.4f} crossed above signal {float(ts.iloc[-1]):.4f}",
            "TRIX is triple-smoothed momentum; crossing its signal line filters noise vs raw MACD.",
            "Momentum build — confirm with price above a recent swing high.",
            bt,
        ))
    elif t.iloc[-1] < ts.iloc[-1] and t.iloc[-2] >= ts.iloc[-2]:
        mask = (t < ts) & (t.shift(1) >= ts.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "TRIX — Bearish Cross", "BEARISH",
            f"TRIX {float(t.iloc[-1]):.4f} crossed below signal {float(ts.iloc[-1]):.4f}",
            "Smoothed momentum is rolling over — early warning of deceleration.",
            "Tighten stops on longs; consider hedges in bear regimes.",
            bt,
        ))
    return signals


def detect_obv_cross(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """On-balance volume vs its 20-day average — flow confirmation."""
    signals: list[dict] = []
    if "OBV" not in df.columns or len(df) < 25 or df["OBV"].isna().iloc[-1]:
        return signals
    obv = df["OBV"]
    obv_ma = obv.rolling(20).mean()
    if obv_ma.isna().iloc[-1]:
        return signals
    price = df["Close"]
    if obv.iloc[-1] > obv_ma.iloc[-1] and obv.iloc[-2] <= obv_ma.iloc[-2]:
        mask = (obv > obv_ma) & (obv.shift(1) <= obv_ma.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "OBV — Accumulation", "BULLISH",
            "OBV crossed above 20-day OBV average  (flow turning positive vs recent norm)",
            "On-balance volume adds volume to the up/down day count; crossing its average "
            "often precedes price catch-up.",
            "Volume leaders institutions watch — potential continuation.",
            bt,
        ))
    elif obv.iloc[-1] < obv_ma.iloc[-1] and obv.iloc[-2] >= obv_ma.iloc[-2]:
        mask = (obv < obv_ma) & (obv.shift(1) >= obv_ma.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "OBV — Distribution", "BEARISH",
            "OBV crossed below 20-day OBV average  (flow deteriorating)",
            "Net volume pressure turning negative even if price is flat — distribution warning.",
            "Price may follow; reduce size into weak OBV unless catalyzed.",
            bt,
        ))
    return signals


def detect_psar_flip(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Parabolic SAR trend flips (price vs SAR)."""
    signals: list[dict] = []
    pl_col, ps_col = "PSARl_0.02_0.2", "PSARs_0.02_0.2"
    if pl_col not in df.columns or len(df) < 3:
        return signals
    price = df["Close"]
    psar = df[pl_col].combine_first(df[ps_col])
    if psar.isna().iloc[-1] or psar.isna().iloc[-2]:
        return signals
    c, s, p0, p1 = float(price.iloc[-1]), float(psar.iloc[-1]), float(price.iloc[-2]), float(psar.iloc[-2])
    if c > s and p0 <= p1:
        mask = (price > psar) & (price.shift(1) <= psar.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Parabolic SAR — Bullish", "BULLISH",
            f"Price {c:.2f} crossed above Parabolic SAR {s:.2f}  (stop-and-reverse up)",
            "SAR flipped under price — the default trend following system is now long.",
            "Use SAR as a trailing stop; not for choppy, range-bound names.",
            bt,
        ))
    elif c < s and p0 >= p1:
        mask = (price < psar) & (price.shift(1) >= psar.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Parabolic SAR — Bearish", "BEARISH",
            f"Price {c:.2f} crossed below Parabolic SAR {s:.2f}  (stop-and-reverse down)",
            "The SAR is now capping price from below — short-term structure turned defensive.",
            "Often used to lock gains or add hedges in downtrends.",
            bt,
        ))
    return signals


def detect_stoch_full(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Classic Stochastic (14,3) — independent of Stochastic RSI."""
    signals: list[dict] = []
    k_col = "STOCHk_14_3_3"
    if k_col not in df.columns or df[k_col].isna().iloc[-1]:
        return signals
    k, price = df[k_col], df["Close"]
    cur_k = float(k.iloc[-1])
    prev_k = float(k.iloc[-2]) if len(k) > 1 else cur_k
    if cur_k < 20 and cur_k >= prev_k - 5:
        mask = k < 20
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Stochastic (Full) — Oversold", "BULLISH",
            f"%%K = {cur_k:.0f}  (oversold < 20, turning)",
            "Full stochastic compares the close to the 14-day range. Deep oversold with an upturn "
            "often front-runs a bounce vs slower oscillators.",
            "Confirm with a cross of %%K above %%D for entries.",
            bt,
        ))
    elif cur_k > 80 and cur_k <= prev_k + 5:
        mask = k > 80
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Stochastic (Full) — Overbought", "BEARISH",
            f"%%K = {cur_k:.0f}  (overbought > 80, rolling over)",
            "Classic stochastic in the upper band — range traders often fade here.",
            "Watch for %%K to cross below %%D to validate a short-term pullback.",
            bt,
        ))
    return signals


def detect_keltner(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Keltner channels (ATR-based) — price at envelope vs Bollinger (volatility)."""
    signals: list[dict] = []
    lc, uc = "KCLe_20_2", "KCUe_20_2"
    if lc not in df.columns or df[lc].isna().iloc[-1]:
        return signals
    price, lo, hi = df["Close"], df[lc], df[uc]
    cur, l0, h0 = float(price.iloc[-1]), float(lo.iloc[-1]), float(hi.iloc[-1])
    if cur <= l0 * 1.01:
        mask = price <= lo * 1.01
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Keltner — Lower Channel Touch", "BULLISH",
            f"Close {cur:.2f} at/inside lower Keltner {l0:.2f}",
            "Keltner uses ATR for channel width. At the lower band, price is "
            "stretched vs the 20-day EMA midline in a volatility-aware way (distinct from Bollinger).",
            "Mean-reversion or dip-buying context; confirm with volume.",
            bt,
        ))
    elif cur >= h0 * 0.99:
        mask = price >= hi * 0.99
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Keltner — Upper Channel Touch", "BEARISH",
            f"Close {cur:.2f} at/above upper Keltner {h0:.2f}",
            "Price is pressing the upper volatility envelope; risk of giveback toward the EMA center.",
            "Consider trimming into strength; trend-follow with a tight plan.",
            bt,
        ))
    return signals


def detect_donchian(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """N-period Donchian breakouts (shorter horizon than 52-week)."""
    signals: list[dict] = []
    ll, uu = "DCL_20_20", "DCU_20_20"
    if uu not in df.columns or len(df) < 25 or df[uu].isna().iloc[-1]:
        return signals
    price, lo, hi = df["Close"], df[ll], df[uu]
    cur, l0, h0 = float(price.iloc[-1]), float(lo.iloc[-1]), float(hi.iloc[-1])
    if cur >= h0 * 0.999:
        mask = price >= df[uu] * 0.999
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Donchian — 20D High Breakout", "BULLISH",
            f"Close {cur:.2f} at/above 20-day Donchian high {h0:.2f}",
            "A 20-day channel breakout: short-term range expansion; useful for "
            "momentum systems independent of 52-week lookback.",
            "Trend-follow: invalid if price fails back into the range.",
            bt,
        ))
    elif cur <= l0 * 1.001:
        mask = price <= df[ll] * 1.001
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Donchian — 20D Low Breakdown", "BEARISH",
            f"Close {cur:.2f} at/under 20-day Donchian low {l0:.2f}",
            "Short-term support shelf gave way — path of least resistance may stay lower near-term.",
            "Avoid premature counter-trend buys until structure improves.",
            bt,
        ))
    return signals


def detect_supertrend_flip(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    signals: list[dict] = []
    col = "SUPERTd_10_3"
    if col not in df.columns or len(df) < 3 or df[col].isna().iloc[-1]:
        return signals
    d = df[col]
    price = df["Close"]
    if d.iloc[-1] > 0 and d.iloc[-2] < 0:
        mask = (d > 0) & (d.shift(1) < 0)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Supertrend — Bullish Flip", "BULLISH",
            "Supertrend direction flipped to bullish (10/3 params)",
            "The Supertrend stop switched under price — default trend state is long until the next flip.",
            "Works best in clean trends; choppy markets produce whipsaw.",
            bt,
        ))
    elif d.iloc[-1] < 0 and d.iloc[-2] > 0:
        mask = (d < 0) & (d.shift(1) > 0)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Supertrend — Bearish Flip", "BEARISH",
            "Supertrend direction flipped to bearish (10/3 params)",
            "The stop/anchor moved above price — system suggests defensive positioning.",
            "Often used for exits or to trail shorts in downtrends.",
            bt,
        ))
    return signals


def detect_ppo(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Percentage Price Oscillator — scale-free cousin of MACD."""
    signals: list[dict] = []
    pc, sc = "PPO_12_26_9", "PPOs_12_26_9"
    if pc not in df.columns or df[pc].isna().iloc[-1]:
        return signals
    ppo, psig, price = df[pc], df[sc], df["Close"]
    if ppo.iloc[-1] > psig.iloc[-1] and ppo.iloc[-2] <= psig.iloc[-2]:
        mask = (ppo > psig) & (ppo.shift(1) <= psig.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "PPO — Bullish Cross", "BULLISH",
            f"PPO {float(ppo.iloc[-1]):.3f} crossed above signal {float(psig.iloc[-1]):.3f}",
            "PPO is MACD as a percentage — comparable across different-priced names.",
            "Confirm with price; combine with longer trend filters in volatile tape.",
            bt,
        ))
    elif ppo.iloc[-1] < psig.iloc[-1] and ppo.iloc[-2] >= psig.iloc[-2]:
        mask = (ppo < psig) & (ppo.shift(1) >= psig.shift(1))
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "PPO — Bearish Cross", "BEARISH",
            f"PPO {float(ppo.iloc[-1]):.3f} crossed below signal {float(psig.iloc[-1]):.3f}",
            "Short-term momentum is lagging the signal line — waning impulsive strength.",
            "Risk management signal for longs; watch support.",
            bt,
        ))
    return signals


def detect_awesome_osc(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    signals: list[dict] = []
    col = "AO_5_34"
    if col not in df.columns or len(df) < 3 or df[col].isna().iloc[-1]:
        return signals
    ao, price = df[col], df["Close"]
    if ao.iloc[-1] > 0 and ao.iloc[-2] <= 0:
        mask = (ao > 0) & (ao.shift(1) <= 0)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Awesome Oscillator — Bullish Zero Line", "BULLISH",
            f"AO = {float(ao.iloc[-1]):.3f} crossed above zero",
            "Bill Williams' AO uses 5 vs 34 median prices — quick read on short-term vs medium momentum.",
            "Often used with confirmation from trend or volume.",
            bt,
        ))
    elif ao.iloc[-1] < 0 and ao.iloc[-2] >= 0:
        mask = (ao < 0) & (ao.shift(1) >= 0)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Awesome Oscillator — Bearish Zero Line", "BEARISH",
            f"AO = {float(ao.iloc[-1]):.3f} crossed below zero",
            "Short-term pressure has turned negative relative to the 34-period baseline.",
            "Watch for follow-through; not a stand-alone short signal in isolation.",
            bt,
        ))
    return signals


def detect_efi_cross(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    if "Volume" not in df.columns or df["Volume"].isna().all():
        return []
    signals: list[dict] = []
    col = "EFI_13"
    if col not in df.columns or len(df) < 3 or df[col].isna().iloc[-1]:
        return signals
    efi, price = df[col], df["Close"]
    if efi.iloc[-1] > 0 and efi.iloc[-2] <= 0:
        mask = (efi > 0) & (efi.shift(1) <= 0)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Elder Force — Bullish", "BULLISH",
            "Elder Force Index crossed above zero  (13-day)",
            "Elder Force marries price change and volume — a pulse on power behind the move.",
            "Bulls want rising EFI with an uptrend.",
            bt,
        ))
    elif efi.iloc[-1] < 0 and efi.iloc[-2] >= 0:
        mask = (efi < 0) & (efi.shift(1) >= 0)
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Elder Force — Bearish", "BEARISH",
            "Elder Force Index crossed below zero  (13-day)",
            "Sellers' volume power is now dominating on this definition.",
            "Aligns with risk-off or profit-taking in existing longs.",
            bt,
        ))
    return signals


def detect_dpo_extreme(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    signals: list[dict] = []
    col = "DPO_20"
    if col not in df.columns or len(df) < 30 or df[col].isna().iloc[-1]:
        return signals
    dpo, price = df[col], df["Close"]
    cur = float(dpo.iloc[-1])
    if cur < -8:
        mask = dpo < -8
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "DPO — Extreme Low", "BULLISH",
            f"DPO = {cur:.1f}  (deeply below 20-day detrended mean)",
            "The Detrended Price Oscillator strips trend to highlight cycles — deep lows are cycle trough candidates.",
            "Pair with trend filter; mean reversion, not a guaranteed bottom.",
            bt,
        ))
    elif cur > 8:
        mask = dpo > 8
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "DPO — Extreme High", "BEARISH",
            f"DPO = {cur:.1f}  (stretched above 20-day detrended mean)",
            "Price is anomalously high vs its detrended baseline — late-cycle feel within the window.",
            "Consider trimming or waiting for a reset.",
            bt,
        ))
    return signals


def detect_vortex_cross(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """VMI: positive vortex > negative — trend init."""
    signals: list[dict] = []
    vp, vm = "VTXP_14", "VTXM_14"
    if vp not in df.columns or len(df) < 3 or df[vp].isna().iloc[-1]:
        return signals
    p, m, c = df[vp], df[vm], df["Close"]
    if p.iloc[-1] > m.iloc[-1] and p.iloc[-2] <= m.iloc[-2]:
        mask = (p > m) & (p.shift(1) <= m.shift(1))
        bt = backtest_signal(c, mask)
        signals.append(_make_signal(
            symbol, name,
            "Vortex — Bullish", "BULLISH",
            f"VI+ {float(p.iloc[-1]):.2f} crossed above VI- {float(m.iloc[-1]):.2f}",
            "The Vortex Indicator separates directional from random movement — a fresh VI+ lead.",
            "Use like other cross systems: best with broader trend agreement.",
            bt,
        ))
    elif p.iloc[-1] < m.iloc[-1] and p.iloc[-2] >= m.iloc[-2]:
        mask = (p < m) & (p.shift(1) >= m.shift(1))
        bt = backtest_signal(c, mask)
        signals.append(_make_signal(
            symbol, name,
            "Vortex — Bearish", "BEARISH",
            f"VI- {float(m.iloc[-1]):.2f} crossed above VI+ {float(p.iloc[-1]):.2f}",
            "Down-move definition now dominates the Vortex pair on this horizon.",
            "Defensive bias until leadership returns to VI+.",
            bt,
        ))
    return signals


def detect_atr_surge(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """ATR% vs its rolling median — only fires on genuine vol expansion with directional day."""
    signals: list[dict] = []
    col = "ATRr_14"
    if col not in df.columns or len(df) < 40 or df[col].isna().iloc[-1]:
        return signals
    atr, close = df[col], df["Close"]
    ratio = atr / close.replace(0, np.nan) * 100.0
    med = ratio.rolling(20).median()
    if med.isna().iloc[-1]:
        return signals
    r, m0 = float(ratio.iloc[-1]), float(med.iloc[-1])
    r1 = (float(close.iloc[-1]) / float(close.iloc[-2]) - 1) * 100.0
    if r > m0 * 1.6 and m0 > 0 and r1 > 0.5:
        daych = close.pct_change() * 100.0
        mask = (ratio > med * 1.6) & (daych > 0.5)
        bt = backtest_signal(close, mask.fillna(False))
        signals.append(_make_signal(
            symbol, name,
            "ATR — Volatility Surge (Up)", "BULLISH",
            f"ATR% = {r:.2f} vs 20d median {m0:.2f}  |  day {r1:+.1f}%",
            "True range is in the top tier vs recent history while price is green — an expansion day with a bid.",
            "Breakout/continuation or news tail-risk; size for volatility.",
            bt,
        ))
    elif r > m0 * 1.6 and m0 > 0 and r1 < -0.5:
        daych = close.pct_change() * 100.0
        mask = (ratio > med * 1.6) & (daych < -0.5)
        bt = backtest_signal(close, mask.fillna(False))
        signals.append(_make_signal(
            symbol, name,
            "ATR — Volatility Surge (Down)", "BEARISH",
            f"ATR% = {r:.2f} vs 20d median {m0:.2f}  |  day {r1:+.1f}%",
            "Range expansion with a down close — either liquidation or a regime shift.",
            "Reduce position size; wait for vol to compress before aggressive entries.",
            bt,
        ))
    return signals


def detect_ulcer_elevated(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    """Ulcer Index — drawdown pain; elevated = stress regime."""
    signals: list[dict] = []
    col = "UI_14"
    if col not in df.columns or len(df) < 30 or df[col].isna().iloc[-1]:
        return signals
    ui, price = df[col], df["Close"]
    base = float(ui.iloc[-1])
    m20 = float(ui.rolling(20).mean().iloc[-1]) if not ui.rolling(20).mean().isna().iloc[-1] else None
    if m20 is not None and m20 > 0 and base > m20 * 1.4:
        mask = ui > ui.rolling(20).mean() * 1.4
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Ulcer Index — Elevated", "BEARISH",
            f"UI = {base:.2f}  (>1.4× 20d average {m20:.2f})",
            "The Ulcer Index punishes both depth and duration of drawdowns — spiking means "
            "pain is worse than a normal pull-in.",
            "Risk management: wider stops do not help if path is jagged. Prefer smaller size.",
            bt,
        ))
    return signals


def detect_fisher_extreme(symbol: str, name: str, df: pd.DataFrame) -> list[dict]:
    signals: list[dict] = []
    col = "FISHERT_9_1"
    if col not in df.columns or df[col].isna().iloc[-1]:
        return signals
    f, price = df[col], df["Close"]
    cur = float(f.iloc[-1])
    if cur < -2.2:
        mask = f < -2.2
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Fisher Transform — Low Extreme", "BULLISH",
            f"Fisher = {cur:.2f}  (deep negative)",
            "The Fisher transform compresses price near extremes; deep lows are statistical outliers that often revert.",
            "Counter-trend bounce candidate — confirm on structure.",
            bt,
        ))
    elif cur > 2.2:
        mask = f > 2.2
        bt = backtest_signal(price, mask)
        signals.append(_make_signal(
            symbol, name,
            "Fisher Transform — High Extreme", "BEARISH",
            f"Fisher = {cur:.2f}  (deep positive)",
            "Stretched to the high side in transformed space — more prone to giveback or stall.",
            "Take profits into euphoric extensions.",
            bt,
        ))
    return signals


# ─── DEX Token Data Fetcher ───────────────────────────────────────────────────

def fetch_dex_df(contract_address: str, days: int = 365) -> pd.DataFrame | None:
    """
    Fetches daily OHLCV candles for a DEX token via DexScreener + GeckoTerminal.
    Returns a DataFrame with Open/High/Low/Close/Volume columns, or None on failure.
    """
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        pairs = data.get("pairs") or []
        if not pairs:
            return None
        pairs.sort(key=lambda p: float(p.get("liquidity", {}).get("usd", 0)), reverse=True)
        best = pairs[0]
        chain = best["chainId"]
        pool_address = best["pairAddress"]
    except Exception:
        return None

    try:
        gt_url = (
            f"https://api.geckoterminal.com/api/v2/networks/{chain}"
            f"/pools/{pool_address}/ohlcv/day?limit={min(days, 1000)}&currency=usd"
        )
        req2 = urllib.request.Request(gt_url, headers=headers)
        with urllib.request.urlopen(req2, timeout=10) as r2:
            gt_data = json.loads(r2.read())

        ohlcv = gt_data.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
        if len(ohlcv) < 30:
            return None

        # GeckoTerminal format: [timestamp_s, open, high, low, close, volume]
        rows = [
            {"Open": float(c[1]), "High": float(c[2]), "Low": float(c[3]),
             "Close": float(c[4]), "Volume": float(c[5])}
            for c in ohlcv
        ]
        df = pd.DataFrame(
            rows,
            index=pd.to_datetime([datetime.datetime.fromtimestamp(c[0]) for c in ohlcv]),
        ).sort_index()
        return df
    except Exception:
        return None


def scan_ticker_dex(symbol: str, name: str, contract_address: str) -> list[dict]:
    """Fetch DEX token OHLCV via DexScreener/GeckoTerminal and run all strategy scans."""
    df = fetch_dex_df(contract_address, days=365)
    if df is None or len(df) < 30:
        logger.warning(f"  {symbol} (DEX): insufficient data or fetch failed")
        return []

    try:
        df.ta.rsi(length=14, append=True)
        df.ta.stochrsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.sma(length=50,  append=True)
        df.ta.sma(length=200, append=True)
        df.ta.bbands(length=20, std=2.0, append=True)
        df.ta.adx(length=14, append=True)
    except Exception as exc:
        logger.warning(f"  pandas-ta error on {symbol} (DEX): {exc}")
    apply_extended_ta(df)
    apply_comprehensive_ta(df)

    signals: list[dict] = []
    signals += detect_rsi(symbol, name, df)
    signals += detect_stoch_rsi(symbol, name, df)
    signals += detect_macd(symbol, name, df)
    signals += detect_ma_cross(symbol, name, df)
    signals += detect_bollinger(symbol, name, df)
    signals += detect_adx(symbol, name, df)
    signals += detect_vwap(symbol, name, df)
    signals += detect_breakout(symbol, name, df)
    signals += detect_volume_spike(symbol, name, df)
    signals += detect_williams_r(symbol, name, df)
    signals += detect_cci(symbol, name, df)
    signals += detect_mfi(symbol, name, df)
    signals += detect_cmf(symbol, name, df)
    signals += detect_aroon(symbol, name, df)
    signals += detect_ema_fast_cross(symbol, name, df)
    signals += detect_trix(symbol, name, df)
    signals += detect_obv_cross(symbol, name, df)
    signals += detect_psar_flip(symbol, name, df)
    signals += detect_stoch_full(symbol, name, df)
    signals += detect_keltner(symbol, name, df)
    signals += detect_donchian(symbol, name, df)
    signals += detect_supertrend_flip(symbol, name, df)
    signals += detect_ppo(symbol, name, df)
    signals += detect_awesome_osc(symbol, name, df)
    signals += detect_efi_cross(symbol, name, df)
    signals += detect_dpo_extreme(symbol, name, df)
    signals += detect_vortex_cross(symbol, name, df)
    signals += detect_atr_surge(symbol, name, df)
    signals += detect_ulcer_elevated(symbol, name, df)
    signals += detect_fisher_extreme(symbol, name, df)

    reg = regime_label(df)
    for sig in signals:
        sig["regime"] = reg
    return signals


# ─── Main Scanner ─────────────────────────────────────────────────────────────

def scan_ticker(symbol: str, name: str) -> list[dict]:
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
    apply_extended_ta(df)
    apply_comprehensive_ta(df)

    signals: list[dict] = []
    signals += detect_rsi(symbol, name, df)
    signals += detect_stoch_rsi(symbol, name, df)
    signals += detect_macd(symbol, name, df)
    signals += detect_ma_cross(symbol, name, df)
    signals += detect_bollinger(symbol, name, df)
    signals += detect_adx(symbol, name, df)
    signals += detect_vwap(symbol, name, df)
    signals += detect_breakout(symbol, name, df)
    signals += detect_volume_spike(symbol, name, df)
    signals += detect_williams_r(symbol, name, df)
    signals += detect_cci(symbol, name, df)
    signals += detect_mfi(symbol, name, df)
    signals += detect_cmf(symbol, name, df)
    signals += detect_aroon(symbol, name, df)
    signals += detect_ema_fast_cross(symbol, name, df)
    signals += detect_trix(symbol, name, df)
    signals += detect_obv_cross(symbol, name, df)
    signals += detect_psar_flip(symbol, name, df)
    signals += detect_stoch_full(symbol, name, df)
    signals += detect_keltner(symbol, name, df)
    signals += detect_donchian(symbol, name, df)
    signals += detect_supertrend_flip(symbol, name, df)
    signals += detect_ppo(symbol, name, df)
    signals += detect_awesome_osc(symbol, name, df)
    signals += detect_efi_cross(symbol, name, df)
    signals += detect_dpo_extreme(symbol, name, df)
    signals += detect_vortex_cross(symbol, name, df)
    signals += detect_atr_surge(symbol, name, df)
    signals += detect_ulcer_elevated(symbol, name, df)
    signals += detect_fisher_extreme(symbol, name, df)

    reg = regime_label(df)
    for sig in signals:
        sig["regime"] = reg
    return signals


def run_full_scan(
    tickers: dict[str, str] | None = None,
    dex_tickers: dict[str, str] | None = None,
) -> list[dict]:
    """
    Scan all tickers. Returns signals sorted by confidence (highest first),
    filtered to confidence >= 45.
    dex_tickers: symbol -> contract_address mapping for DEX tokens (optional).
    """
    if tickers is None:
        tickers = SCAN_TICKERS
    if dex_tickers is None:
        dex_tickers = {}

    logger.info(
        f"Scanning {len(tickers)} tickers + {len(dex_tickers)} DEX tokens "
        f"across 30 strategy detectors (pandas-ta) ..."
    )
    all_signals: list[dict] = []

    for symbol, name in tickers.items():
        try:
            sigs = scan_ticker(symbol, name)
            if sigs:
                logger.info(f"  {symbol}: {len(sigs)} signal(s)")
            all_signals.extend(sigs)
        except Exception as exc:
            logger.warning(f"  Scan error {symbol}: {exc}")

    for symbol, contract in dex_tickers.items():
        try:
            sigs = scan_ticker_dex(symbol, symbol, contract)
            if sigs:
                logger.info(f"  {symbol} (DEX): {len(sigs)} signal(s)")
            all_signals.extend(sigs)
        except Exception as exc:
            logger.warning(f"  DEX scan error {symbol}: {exc}")

    cot_summary = get_cot_positioning_summary()
    _apply_positioning_overlay(all_signals, cot_summary)
    diag = positioning_overlay_diagnostics(all_signals)
    if diag["adjusted"]:
        top = sorted(
            diag["by_ticker"].items(),
            key=lambda kv: kv[1]["adjusted"],
            reverse=True,
        )[:5]
        top_str = ", ".join(
            f"{ticker}:{vals['adjusted']}" for ticker, vals in top
        )
        logger.info(
            "COT overlay active | adjusted=%s boosted=%s penalized=%s | top=%s | regime=%s",
            diag["adjusted"],
            diag["boosted"],
            diag["penalized"],
            top_str,
            cot_summary.get("regime", "Unknown"),
        )
    else:
        logger.info(
            "COT overlay inactive | adjusted=0/%s | regime=%s",
            diag["total"],
            cot_summary.get("regime", "Unknown"),
        )

    filtered = [s for s in all_signals if s.get("confidence", 0) >= 45]
    filtered.sort(key=lambda s: (
        0 if s["direction"] == "BULLISH" else 1,
        -s.get("confidence", 0),
    ))

    logger.info(f"Scan complete: {len(all_signals)} raw → {len(filtered)} after confidence filter")
    return filtered


def group_signals_primary_secondary(signals: list[dict]) -> list[dict]:
    """
    Group by (ticker, direction), keep the two highest-confidence rules per group.
    Returns [{"primary": dict, "secondary": dict | None, "agreement_count": int}, ...]
    in the same order as run_full_scan: bullish groups first, then by primary score descending.
    agreement_count is how many raw rules fired for that ticker and direction.
    """
    from collections import defaultdict

    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for s in signals:
        buckets[(s["ticker"], s["direction"])].append(s)

    out: list[dict] = []
    for sigs in buckets.values():
        sigs.sort(key=lambda x: -x.get("confidence", 0))
        out.append(
            {
                "primary": sigs[0],
                "secondary": sigs[1] if len(sigs) > 1 else None,
                "agreement_count": len(sigs),
            }
        )

    out.sort(
        key=lambda g: (
            0 if g["primary"]["direction"] == "BULLISH" else 1,
            -g["primary"].get("confidence", 0),
        )
    )
    return out


def format_backtest_summary(bt: dict) -> str:
    if bt.get("insufficient_data") or "5d" not in bt:
        return f"Insufficient history ({bt.get('count', 0)} signals)"
    d5 = bt["5d"]
    return (
        f"5d: {d5['win_rate']}% wins | avg {d5['avg_return']:+.1f}% | "
        f"Sharpe {d5['sharpe']:.2f} | MaxDD {d5['max_drawdown']:.1f}%"
    )
