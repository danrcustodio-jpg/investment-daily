# Strategy Alerts
**Last scan:** Wednesday June 17, 2026 at 04:33 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 94 |
| 🟢 Bullish | 76 |
| 🔴 Bearish | 48 |
| ✅ Fired this run (SMS + email) | 94 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 10 |

## 📲 SMS sent (3)

- One text per ticker: **XLE, GC=F, SOXL**
- Skipped — over per-scan cap: **MRVL, AVGO, SMH, CL=F, TQQQ, RKLB, AAPL, AMD, XLK, QQQ, ARM, GOOGL, PLTR, IONQ, NVDA, APP, ARKK, XRP-USD, BTC-USD, UPRO, SPY, AMZN, MARA, META, CEG, SOL-USD** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **77.4** (1 BULL signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **XLE** | VWAP Deviation — Oversold | 77.4 | 1 | Aroon — Strong Downtrend | 90.8 | 2 |
| **GC=F** | OBV — Accumulation | 78.3 | 3 | ADX Strong Trend — Bearish | 84.3 | 2 |
| **MRVL** | ADX Strong Trend — Bullish | 74.3 | 1 | Ulcer Index — Elevated | 81.8 | 2 |
| **SOXL** | Chaikin Money Flow — Bullish | 65.6 | 1 | Ulcer Index — Elevated | 81.8 | 1 |
| **AVGO** | VWAP Deviation — Oversold | 79.5 | 3 | Ulcer Index — Elevated | 81.3 | 2 |
| **SMH** | Aroon — Strong Uptrend | 76.2 | 2 | Ulcer Index — Elevated | 81.3 | 1 |
| **RKLB** | CCI — Extreme Oversold | 68.9 | 1 | Aroon — Strong Downtrend | 78.2 | 1 |
| **AMD** | Aroon — Strong Uptrend | 71.6 | 1 | VWAP Deviation — Overbought | 75.4 | 1 |
| **ARM** | 52-Week Breakout | 74.9 | 2 | Ulcer Index — Elevated | 68.4 | 1 |
| **PLTR** | VWAP Deviation — Oversold | 74.3 | 1 | Aroon — Strong Downtrend | 71.3 | 2 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **AVGO** | VWAP Deviation — Oversold | 79.5 | 64.7% | 3.43% | 3.16 |
| 🟢 BULLISH | **AVGO** | Stochastic RSI Oversold | 79.4 | 65.8% | 2.92% | 3.13 |
| 🟢 BULLISH | **CL=F** | Keltner — Lower Channel Touch | 79.3 | 63.3% | 1.83% | 2.9 |
| 🟢 BULLISH | **GC=F** | OBV — Accumulation | 78.3 | 68.4% | 0.95% | 2.09 |
| 🟢 BULLISH | **AVGO** | Stochastic (Full) — Oversold | 77.5 | 63.9% | 2.71% | 2.51 |
| 🟢 BULLISH | **XLE** | VWAP Deviation — Oversold | 77.4 | 75.8% | 0.95% | 1.84 |
| 🟢 BULLISH | **SMH** | Aroon — Strong Uptrend | 76.2 | 65.8% | 1.59% | 2.33 |
| 🟢 BULLISH | **CL=F** | RSI Oversold | 75.0 | 75.0% | 2.29% | 5.74 |
| 🟢 BULLISH | **ARM** | 52-Week Breakout | 74.9 | 58.3% | 5.85% | 2.15 |
| 🟢 BULLISH | **PLTR** | VWAP Deviation — Oversold | 74.3 | 58.2% | 2.88% | 2.36 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 74.3 | 59.2% | 3.32% | 2.14 |
| 🟢 BULLISH | **ARM** | MACD Bullish Crossover | 72.8 | 55.6% | 3.62% | 2.49 |
| 🟢 BULLISH | **CL=F** | Fisher Transform — Low Extreme | 72.7 | 64.5% | 1.24% | 2.37 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 71.6 | 62.4% | 3.56% | 2.42 |
| 🟢 BULLISH | **SMH** | Chaikin Money Flow — Bullish | 69.0 | 61.1% | 1.26% | 1.81 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 68.9 | 54.2% | 4.01% | 2.06 |
| 🟢 BULLISH | **CL=F** | VWAP Deviation — Oversold | 67.7 | 65.3% | 1.29% | 1.73 |
| 🟢 BULLISH | **CL=F** | Stochastic RSI Oversold | 67.1 | 61.3% | 1.5% | 2.02 |
| 🟢 BULLISH | **ARKK** | Awesome Oscillator — Bullish Zero Line | 66.6 | 63.6% | 0.79% | 1.54 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 65.9 | 68.7% | 0.76% | 1.38 |
| 🟢 BULLISH | **GC=F** | MACD Bullish Crossover | 65.8 | 60.0% | 0.7% | 1.87 |
| 🟢 BULLISH | **SOXL** | Chaikin Money Flow — Bullish | 65.6 | 60.2% | 3.88% | 1.73 |
| 🟢 BULLISH | **BTC-USD** | TRIX — Bullish Cross | 64.8 | 47.1% | 1.34% | 1.91 |
| 🟢 BULLISH | **GC=F** | Elder Force — Bullish | 64.1 | 53.3% | 0.59% | 1.67 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 64.1 | 59.4% | 3.25% | 1.93 |
| 🟢 BULLISH | **ARKK** | Chaikin Money Flow — Bullish | 63.1 | 59.1% | 1.39% | 1.6 |
| 🟢 BULLISH | **UPRO** | Awesome Oscillator — Bullish Zero Line | 60.2 | 50.0% | 1.02% | 1.53 |
| 🟢 BULLISH | **AMD** | ADX Strong Trend — Bullish | 59.9 | 59.4% | 2.49% | 1.63 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 59.6 | 57.3% | 2.02% | 1.48 |
| 🟢 BULLISH | **ARM** | Aroon — Strong Uptrend | 59.5 | 54.2% | 2.27% | 1.48 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 58.9 | 60.3% | 1.06% | 1.38 |
| 🟢 BULLISH | **QQQ** | ADX Strong Trend — Bullish | 58.7 | 58.7% | 0.57% | 1.24 |
| 🟢 BULLISH | **AMZN** | Williams %R — Oversold | 58.5 | 62.7% | 0.93% | 1.37 |
| 🟢 BULLISH | **CL=F** | Stochastic (Full) — Oversold | 58.5 | 60.6% | 0.99% | 1.5 |
| 🟢 BULLISH | **XLK** | Chaikin Money Flow — Bullish | 58.4 | 62.8% | 0.67% | 1.22 |
| 🟢 BULLISH | **MRVL** | CCI — Extreme Oversold | 57.3 | 58.7% | 1.88% | 1.34 |
| 🟢 BULLISH | **TQQQ** | Chaikin Money Flow — Bullish | 57.1 | 62.0% | 1.43% | 1.29 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 56.4 | 58.6% | 2.45% | 1.24 |
| 🟢 BULLISH | **MARA** | OBV — Accumulation | 55.7 | 53.1% | 2.4% | 1.39 |
| 🟢 BULLISH | **IONQ** | Stochastic RSI Oversold | 55.2 | 52.5% | 4.02% | 1.42 |
| 🟢 BULLISH | **RKLB** | VWAP Deviation — Oversold | 54.6 | 52.7% | 2.57% | 1.37 |
| 🟢 BULLISH | **PLTR** | Chaikin Money Flow — Bullish | 54.3 | 54.6% | 1.8% | 1.19 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 54.2 | 53.1% | 3.23% | 1.38 |
| 🟢 BULLISH | **AMZN** | VWAP Deviation — Oversold | 53.8 | 60.3% | 0.95% | 1.26 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 53.8 | 57.5% | 0.85% | 1.19 |
| 🟢 BULLISH | **CL=F** | Williams %R — Oversold | 53.8 | 58.7% | 0.87% | 1.31 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 53.5 | 58.6% | 2.91% | 1.23 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 52.9 | 59.6% | 0.48% | 0.94 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 52.7 | 60.9% | 0.36% | 0.83 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 51.7 | 58.8% | 0.61% | 0.98 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 51.6 | 56.5% | 1.57% | 1.21 |
| 🟢 BULLISH | **SOL-USD** | TRIX — Bullish Cross | 51.0 | 60.0% | 1.34% | 1.1 |
| 🟢 BULLISH | **APP** | VWAP Deviation — Oversold | 50.4 | 58.1% | 1.62% | 0.94 |
| 🟢 BULLISH | **XLE** | Williams %R — Oversold | 50.1 | 61.6% | 0.35% | 0.54 |
| 🔴 BEARISH | **XLE** | Aroon — Strong Downtrend | 90.8 | 85.7% | 1.89% | 5.44 |
| 🔴 BEARISH | **XLE** | Chaikin Money Flow — Bearish | 86.7 | 74.0% | 1.43% | 2.96 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 84.3 | 73.8% | 1.86% | 4.06 |
| 🔴 BEARISH | **GC=F** | MFI — Overbought | 83.1 | 68.9% | 1.2% | 2.68 |
| 🔴 BEARISH | **SOXL** | Ulcer Index — Elevated | 81.8 | 76.6% | 8.55% | 4.38 |
| 🔴 BEARISH | **MRVL** | Ulcer Index — Elevated | 81.8 | 74.7% | 3.81% | 4.28 |
| 🔴 BEARISH | **AVGO** | Ulcer Index — Elevated | 81.3 | 73.2% | 3.89% | 4.52 |
| 🔴 BEARISH | **SMH** | Ulcer Index — Elevated | 81.3 | 74.8% | 2.36% | 4.47 |
| 🔴 BEARISH | **TQQQ** | Ulcer Index — Elevated | 78.4 | 71.8% | 3.24% | 2.82 |
| 🔴 BEARISH | **RKLB** | Aroon — Strong Downtrend | 78.2 | 64.5% | 4.85% | 2.72 |
| 🔴 BEARISH | **AVGO** | Aroon — Strong Downtrend | 77.0 | 63.2% | 3.64% | 3.12 |
| 🔴 BEARISH | **AAPL** | Aroon — Strong Downtrend | 76.3 | 61.9% | 1.42% | 2.33 |
| 🔴 BEARISH | **AMD** | VWAP Deviation — Overbought | 75.4 | 63.8% | 3.61% | 2.59 |
| 🔴 BEARISH | **XLK** | Ulcer Index — Elevated | 75.3 | 66.7% | 1.31% | 2.66 |
| 🔴 BEARISH | **QQQ** | Ulcer Index — Elevated | 75.2 | 68.5% | 0.99% | 2.35 |
| 🔴 BEARISH | **GOOGL** | Elder Force — Bearish | 74.8 | 65.5% | 1.98% | 2.53 |
| 🔴 BEARISH | **MRVL** | VWAP Deviation — Overbought | 73.4 | 59.7% | 2.95% | 2.0 |
| 🔴 BEARISH | **PLTR** | Aroon — Strong Downtrend | 71.3 | 58.7% | 2.96% | 2.29 |
| 🔴 BEARISH | **IONQ** | ADX Strong Trend — Bearish | 70.9 | 55.7% | 5.27% | 2.25 |
| 🔴 BEARISH | **NVDA** | Aroon — Strong Downtrend | 69.5 | 61.8% | 2.13% | 2.07 |
| 🔴 BEARISH | **IONQ** | Ulcer Index — Elevated | 69.0 | 53.6% | 5.36% | 2.15 |
| 🔴 BEARISH | **APP** | Elder Force — Bearish | 68.9 | 57.7% | 4.15% | 1.59 |
| 🔴 BEARISH | **ARM** | Ulcer Index — Elevated | 68.4 | 63.4% | 2.77% | 2.05 |
| 🔴 BEARISH | **PLTR** | Ulcer Index — Elevated | 66.6 | 54.2% | 2.57% | 1.83 |
| 🔴 BEARISH | **XRP-USD** | Stochastic RSI Overbought | 66.6 | 49.4% | 4.15% | 2.02 |
| 🔴 BEARISH | **UPRO** | Ulcer Index — Elevated | 64.6 | 63.1% | 1.71% | 1.64 |
| 🔴 BEARISH | **XLK** | ADX Strong Trend — Bearish | 64.0 | 59.8% | 1.43% | 1.68 |
| 🔴 BEARISH | **SPY** | Ulcer Index — Elevated | 62.5 | 64.5% | 0.53% | 1.4 |
| 🔴 BEARISH | **MRVL** | TRIX — Bearish Cross | 59.8 | 60.0% | 0.85% | 1.48 |
| 🔴 BEARISH | **IONQ** | EMA 9/21 — Bearish Cross | 59.5 | 50.0% | 5.66% | 1.57 |
| 🔴 BEARISH | **SMH** | VWAP Deviation — Overbought | 58.0 | 58.5% | 0.93% | 1.22 |
| 🔴 BEARISH | **AAPL** | Ulcer Index — Elevated | 57.3 | 59.6% | 0.94% | 1.38 |
| 🔴 BEARISH | **META** | Aroon — Strong Downtrend | 54.9 | 59.0% | 1.13% | 1.22 |
| 🔴 BEARISH | **SMH** | Williams %R — Overbought | 54.1 | 56.1% | 0.86% | 1.11 |
| 🔴 BEARISH | **SMH** | Stochastic (Full) — Overbought | 53.8 | 57.7% | 0.79% | 1.01 |
| 🔴 BEARISH | **SOXL** | VWAP Deviation — Overbought | 53.6 | 55.4% | 2.87% | 1.23 |
| 🔴 BEARISH | **TQQQ** | ADX Strong Trend — Bearish | 52.7 | 59.2% | 2.04% | 1.05 |
| 🔴 BEARISH | **SOXL** | Vortex — Bearish | 52.2 | 47.8% | 3.46% | 1.49 |
| 🔴 BEARISH | **CEG** | Aroon — Strong Downtrend | 51.7 | 60.2% | 1.16% | 0.94 |
| 🔴 BEARISH | **ARM** | VWAP Deviation — Overbought | 50.6 | 52.3% | 1.62% | 1.0 |

---
*Not financial advice. Backtests use historical data.*