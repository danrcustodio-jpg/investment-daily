# Strategy Alerts
**Last scan:** Friday July 31, 2026 at 03:13 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 88 |
| 🟢 Bullish | 83 |
| 🔴 Bearish | 34 |
| ✅ Fired this run (SMS + email) | 88 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 5 |

## 📲 SMS sent (3)

- One text per ticker: **GOOGL, AMZN, IONQ**
- Skipped — over per-scan cap: **NVDA, AAPL, CRWD, ATOM-USD, GC=F, XBI, META, RKLB, APP, ARM, AERO-USD, SMH, ARKK, MSFT, SOXL, ETH-USD, AMD, COIN, LINK-USD, PLTR, QQQ, CEG, BTC-USD, TQQQ, TSLA, MRVL, SPY, XLK** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **84.1** (2 BULL signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **GOOGL** | SMA 30 — Bullish Reclaim | 84.1 | 2 | Chaikin Money Flow — Bearish | 88.9 | 1 |
| **IONQ** | PPO — Bullish Cross | 84.5 | 1 | ADX Strong Trend — Bearish | 67.5 | 1 |
| **AAPL** | VWAP Deviation — Oversold | 82.4 | 3 | ADX Strong Trend — Bearish | 80.2 | 2 |
| **XBI** | Fisher Transform — Low Extreme | 79.4 | 4 | Ulcer Index — Elevated | 76.4 | 1 |
| **META** | Fisher Transform — Low Extreme | 78.8 | 1 | Ulcer Index — Elevated | 68.0 | 1 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **AMZN** | EMA 9/21 — Bullish Cross | 87.6 | 85.7% | 3.92% | 4.45 |
| 🟢 BULLISH | **IONQ** | PPO — Bullish Cross | 84.5 | 77.8% | 11.04% | 7.48 |
| 🟢 BULLISH | **GOOGL** | SMA 30 — Bullish Reclaim | 84.1 | 76.9% | 2.38% | 2.8 |
| 🟢 BULLISH | **NVDA** | Stochastic (Full) — Oversold | 82.9 | 75.0% | 4.89% | 5.83 |
| 🟢 BULLISH | **AAPL** | VWAP Deviation — Oversold | 82.4 | 69.0% | 2.99% | 3.91 |
| 🟢 BULLISH | **CRWD** | Vortex — Bullish | 82.1 | 73.3% | 3.22% | 2.86 |
| 🟢 BULLISH | **ATOM-USD** | MFI — Oversold | 81.5 | 80.0% | 3.98% | 3.57 |
| 🟢 BULLISH | **GC=F** | Parabolic SAR — Bullish | 81.1 | 66.7% | 1.09% | 3.01 |
| 🟢 BULLISH | **GOOGL** | MACD Bullish Crossover | 81.0 | 70.0% | 2.36% | 3.33 |
| 🟢 BULLISH | **GC=F** | Vortex — Bullish | 80.5 | 68.0% | 0.95% | 2.92 |
| 🟢 BULLISH | **AAPL** | Williams %R — Oversold | 79.8 | 63.3% | 1.9% | 2.74 |
| 🟢 BULLISH | **AMZN** | Supertrend — Bullish Flip | 79.5 | 57.1% | 2.95% | 3.35 |
| 🟢 BULLISH | **XBI** | Fisher Transform — Low Extreme | 79.4 | 69.6% | 1.21% | 1.99 |
| 🟢 BULLISH | **GC=F** | CCI — Extreme Oversold | 79.2 | 68.5% | 0.89% | 2.41 |
| 🟢 BULLISH | **META** | Fisher Transform — Low Extreme | 78.8 | 67.6% | 2.98% | 4.16 |
| 🟢 BULLISH | **RKLB** | Parabolic SAR — Bullish | 78.0 | 59.1% | 5.43% | 2.67 |
| 🟢 BULLISH | **RKLB** | MACD Bullish Crossover | 77.4 | 56.2% | 5.14% | 2.35 |
| 🟢 BULLISH | **AAPL** | Keltner — Lower Channel Touch | 74.2 | 56.1% | 1.91% | 2.4 |
| 🟢 BULLISH | **APP** | Keltner — Lower Channel Touch | 73.6 | 60.0% | 3.5% | 2.59 |
| 🟢 BULLISH | **ATOM-USD** | Keltner — Lower Channel Touch | 73.3 | 63.8% | 3.42% | 2.6 |
| 🟢 BULLISH | **ARM** | PPO — Bullish Cross | 72.6 | 62.5% | 3.86% | 2.34 |
| 🟢 BULLISH | **AERO-USD** | RSI Oversold | 72.6 | 57.1% | 5.64% | 3.07 |
| 🟢 BULLISH | **XBI** | Williams %R — Oversold | 72.2 | 62.7% | 1.4% | 1.99 |
| 🟢 BULLISH | **XBI** | Stochastic RSI Oversold | 67.9 | 60.7% | 1.04% | 1.76 |
| 🟢 BULLISH | **ATOM-USD** | RSI Oversold | 67.8 | 65.4% | 2.9% | 2.16 |
| 🟢 BULLISH | **XBI** | VWAP Deviation — Oversold | 67.4 | 73.9% | 1.19% | 1.4 |
| 🟢 BULLISH | **NVDA** | Aroon — Strong Uptrend | 67.2 | 61.8% | 1.36% | 1.84 |
| 🟢 BULLISH | **AERO-USD** | Williams %R — Oversold | 67.1 | 52.8% | 6.75% | 1.94 |
| 🟢 BULLISH | **AMD** | VWAP Deviation — Oversold | 65.4 | 58.7% | 1.72% | 2.11 |
| 🟢 BULLISH | **META** | Keltner — Lower Channel Touch | 63.2 | 51.1% | 1.48% | 1.7 |
| 🟢 BULLISH | **PLTR** | VWAP Deviation — Oversold | 62.9 | 54.2% | 2.15% | 1.66 |
| 🟢 BULLISH | **GC=F** | ADX Strong Trend — Bullish | 62.7 | 62.5% | 0.78% | 1.43 |
| 🟢 BULLISH | **AERO-USD** | Stochastic (Full) — Oversold | 61.4 | 54.9% | 5.88% | 1.67 |
| 🟢 BULLISH | **CEG** | Aroon — Strong Uptrend | 61.1 | 58.9% | 2.24% | 1.82 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 60.7 | 52.9% | 3.32% | 1.68 |
| 🟢 BULLISH | **AERO-USD** | Keltner — Lower Channel Touch | 60.3 | 53.4% | 3.37% | 1.77 |
| 🟢 BULLISH | **CRWD** | Stochastic RSI Oversold | 59.2 | 56.4% | 1.56% | 1.6 |
| 🟢 BULLISH | **GOOGL** | Vortex — Bullish | 58.3 | 55.6% | 0.97% | 1.45 |
| 🟢 BULLISH | **AMZN** | Vortex — Bullish | 57.6 | 66.7% | 0.96% | 1.22 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 57.0 | 60.0% | 0.97% | 1.27 |
| 🟢 BULLISH | **META** | Stochastic (Full) — Oversold | 56.7 | 54.5% | 1.12% | 1.45 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 56.5 | 56.5% | 1.88% | 1.36 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 56.2 | 66.4% | 0.57% | 0.94 |
| 🟢 BULLISH | **ARKK** | Fisher Transform — Low Extreme | 56.1 | 64.0% | 1.36% | 1.35 |
| 🟢 BULLISH | **SOXL** | Parabolic SAR — Bullish | 56.1 | 59.3% | 3.69% | 1.48 |
| 🟢 BULLISH | **TSLA** | VWAP Deviation — Oversold | 54.4 | 57.4% | 2.04% | 1.37 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 54.3 | 57.9% | 0.88% | 1.21 |
| 🟢 BULLISH | **PLTR** | Chaikin Money Flow — Bullish | 54.2 | 55.3% | 1.86% | 1.21 |
| 🟢 BULLISH | **AMZN** | SMA 30 — Bullish Reclaim | 54.0 | 56.5% | 0.82% | 1.15 |
| 🟢 BULLISH | **MRVL** | Parabolic SAR — Bullish | 54.0 | 55.0% | 1.5% | 1.44 |
| 🟢 BULLISH | **SOXL** | Stochastic (Full) — Oversold | 53.9 | 60.7% | 3.43% | 1.3 |
| 🟢 BULLISH | **CRWD** | CCI — Extreme Oversold | 53.9 | 56.7% | 1.28% | 1.23 |
| 🟢 BULLISH | **META** | Williams %R — Oversold | 51.9 | 56.2% | 0.85% | 1.05 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 51.7 | 56.9% | 1.57% | 1.21 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 51.6 | 60.0% | 0.34% | 0.81 |
| 🟢 BULLISH | **TQQQ** | VWAP Deviation — Oversold | 51.5 | 59.8% | 1.9% | 1.1 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 51.2 | 56.8% | 2.11% | 1.05 |
| 🟢 BULLISH | **CRWD** | SMA 30 — Bullish Reclaim | 51.0 | 57.1% | 0.95% | 0.76 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 50.8 | 58.2% | 2.52% | 1.06 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 50.4 | 58.8% | 0.43% | 0.84 |
| 🟢 BULLISH | **ATOM-USD** | Fisher Transform — Low Extreme | 50.4 | 57.7% | 1.56% | 1.22 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 50.1 | 58.6% | 0.56% | 0.91 |
| 🔴 BEARISH | **GOOGL** | Chaikin Money Flow — Bearish | 88.9 | 85.2% | 3.31% | 5.38 |
| 🔴 BEARISH | **AAPL** | ADX Strong Trend — Bearish | 80.2 | 65.5% | 2.02% | 3.11 |
| 🔴 BEARISH | **XBI** | Ulcer Index — Elevated | 76.4 | 63.1% | 1.4% | 2.85 |
| 🔴 BEARISH | **SMH** | Chaikin Money Flow — Bearish | 71.7 | 61.9% | 2.04% | 2.29 |
| 🔴 BEARISH | **ARKK** | Chaikin Money Flow — Bearish | 71.4 | 68.8% | 1.86% | 2.2 |
| 🔴 BEARISH | **MSFT** | RSI Overbought | 68.4 | 73.3% | 0.67% | 1.51 |
| 🔴 BEARISH | **SOXL** | Chaikin Money Flow — Bearish | 68.3 | 61.8% | 6.51% | 2.38 |
| 🔴 BEARISH | **META** | Ulcer Index — Elevated | 68.0 | 61.7% | 1.61% | 2.22 |
| 🔴 BEARISH | **IONQ** | ADX Strong Trend — Bearish | 67.5 | 55.8% | 3.92% | 1.91 |
| 🔴 BEARISH | **ETH-USD** | Parabolic SAR — Bearish | 66.6 | 57.6% | 2.76% | 1.86 |
| 🔴 BEARISH | **AAPL** | Parabolic SAR — Bearish | 65.9 | 56.0% | 0.97% | 1.94 |
| 🔴 BEARISH | **XBI** | Aroon — Strong Downtrend | 63.3 | 62.5% | 1.05% | 1.61 |
| 🔴 BEARISH | **COIN** | MACD Bearish Crossover | 63.3 | 43.8% | 4.49% | 2.24 |
| 🔴 BEARISH | **LINK-USD** | TRIX — Bearish Cross | 63.0 | 47.4% | 2.72% | 1.79 |
| 🔴 BEARISH | **QQQ** | ADX Strong Trend — Bearish | 61.5 | 61.4% | 0.95% | 1.44 |
| 🔴 BEARISH | **COIN** | PPO — Bearish Cross | 60.7 | 58.3% | 4.27% | 1.75 |
| 🔴 BEARISH | **AAPL** | Supertrend — Bearish Flip | 60.2 | 57.1% | 1.56% | 1.64 |
| 🔴 BEARISH | **BTC-USD** | EMA 9/21 — Bearish Cross | 55.1 | 56.2% | 0.77% | 1.25 |
| 🔴 BEARISH | **TQQQ** | ADX Strong Trend — Bearish | 54.9 | 60.4% | 2.14% | 1.18 |
| 🔴 BEARISH | **TSLA** | ADX Strong Trend — Bearish | 54.7 | 50.6% | 1.92% | 1.44 |
| 🔴 BEARISH | **META** | Aroon — Strong Downtrend | 53.7 | 56.7% | 1.13% | 1.2 |
| 🔴 BEARISH | **MSFT** | Keltner — Upper Channel Touch | 53.2 | 68.4% | 0.44% | 0.89 |
| 🔴 BEARISH | **SOXL** | ADX Strong Trend — Bearish | 53.0 | 57.4% | 3.91% | 1.31 |
| 🔴 BEARISH | **ARKK** | Ulcer Index — Elevated | 52.6 | 60.4% | 0.88% | 1.12 |
| 🔴 BEARISH | **SMH** | Aroon — Strong Downtrend | 51.6 | 58.5% | 0.93% | 1.08 |
| 🔴 BEARISH | **AMZN** | Williams %R — Overbought | 50.7 | 58.0% | 0.74% | 1.08 |

---
*Not financial advice. Backtests use historical data.*