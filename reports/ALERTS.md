# Strategy Alerts
**Last scan:** Thursday June 25, 2026 at 01:42 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 108 |
| 🟢 Bullish | 99 |
| 🔴 Bearish | 43 |
| ✅ Fired this run (SMS + email) | 108 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 13 |

## 📲 SMS sent (3)

- One text per ticker: **PLTR, XLE, SPY**
- Skipped — over per-scan cap: **UPRO, AAPL, NVDA, MSFT, GC=F, META, SOXL, APP, SMH, ATOM-USD, MRVL, AVGO, AMD, RIOT, TQQQ, XLK, QQQ, AERO-USD, RKLB, MARA, IONQ, CEG, DOGE-USD, ARM, DOT-USD, CL=F, TSLA, GOOGL, AMZN, XBI, CRWD, LTC-USD, SMCI, XRP-USD** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **76.2** (3 BULL signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **XLE** | Fisher Transform — Low Extreme | 76.2 | 3 | Aroon — Strong Downtrend | 89.7 | 1 |
| **AAPL** | VWAP Deviation — Oversold | 82.0 | 3 | Chaikin Money Flow — Bearish | 86.5 | 2 |
| **NVDA** | Williams %R — Oversold | 86.2 | 2 | Aroon — Strong Downtrend | 69.4 | 1 |
| **MSFT** | MFI — Oversold | 83.3 | 2 | Chaikin Money Flow — Bearish | 79.6 | 1 |
| **GC=F** | OBV — Accumulation | 77.5 | 3 | MFI — Overbought | 83.1 | 2 |
| **SOXL** | Aroon — Strong Uptrend | 70.1 | 1 | Ulcer Index — Elevated | 82.3 | 1 |
| **META** | Keltner — Lower Channel Touch | 65.2 | 1 | Chaikin Money Flow — Bearish | 82.3 | 2 |
| **SMH** | Aroon — Strong Uptrend | 76.6 | 1 | Ulcer Index — Elevated | 81.9 | 1 |
| **MRVL** | Aroon — Strong Uptrend | 79.3 | 2 | Ulcer Index — Elevated | 81.1 | 1 |
| **AVGO** | VWAP Deviation — Oversold | 79.8 | 1 | Ulcer Index — Elevated | 80.3 | 1 |
| **AMD** | Aroon — Strong Uptrend | 72.2 | 2 | Williams %R — Overbought | 78.2 | 2 |
| **RIOT** | Aroon — Strong Uptrend | 76.4 | 1 | Elder Force — Bearish | 67.6 | 1 |
| **RKLB** | CCI — Extreme Oversold | 67.6 | 1 | Aroon — Strong Downtrend | 72.5 | 2 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **PLTR** | MFI — Oversold | 100.0 | 100.0% | 7.17% | 29.41 |
| 🟢 BULLISH | **NVDA** | Williams %R — Oversold | 86.2 | 78.7% | 4.22% | 4.75 |
| 🟢 BULLISH | **NVDA** | VWAP Deviation — Oversold | 84.3 | 73.8% | 3.97% | 3.91 |
| 🟢 BULLISH | **MSFT** | MFI — Oversold | 83.3 | 83.3% | 1.73% | 5.56 |
| 🟢 BULLISH | **AAPL** | VWAP Deviation — Oversold | 82.0 | 69.0% | 2.61% | 3.69 |
| 🟢 BULLISH | **APP** | Fisher Transform — Low Extreme | 81.9 | 71.4% | 5.6% | 3.61 |
| 🟢 BULLISH | **MSFT** | RSI Oversold | 81.4 | 72.4% | 2.64% | 5.52 |
| 🟢 BULLISH | **ATOM-USD** | Keltner — Lower Channel Touch | 81.3 | 76.9% | 5.22% | 4.31 |
| 🟢 BULLISH | **APP** | Keltner — Lower Channel Touch | 80.0 | 68.0% | 5.63% | 3.81 |
| 🟢 BULLISH | **AVGO** | VWAP Deviation — Oversold | 79.8 | 65.9% | 3.44% | 3.23 |
| 🟢 BULLISH | **MRVL** | Aroon — Strong Uptrend | 79.3 | 64.2% | 3.55% | 2.41 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 77.8 | 60.5% | 3.55% | 2.31 |
| 🟢 BULLISH | **GC=F** | OBV — Accumulation | 77.5 | 68.4% | 0.95% | 2.09 |
| 🟢 BULLISH | **SMH** | Aroon — Strong Uptrend | 76.6 | 66.1% | 1.61% | 2.36 |
| 🟢 BULLISH | **RIOT** | Aroon — Strong Uptrend | 76.4 | 63.0% | 4.43% | 2.45 |
| 🟢 BULLISH | **XLE** | Fisher Transform — Low Extreme | 76.2 | 76.3% | 0.9% | 1.77 |
| 🟢 BULLISH | **AAPL** | Williams %R — Oversold | 74.2 | 61.4% | 1.55% | 2.27 |
| 🟢 BULLISH | **AERO-USD** | RSI Oversold | 72.7 | 58.1% | 8.39% | 3.03 |
| 🟢 BULLISH | **GC=F** | Williams %R — Oversold | 72.2 | 65.1% | 1.24% | 1.94 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 72.2 | 62.9% | 3.56% | 2.45 |
| 🟢 BULLISH | **XLE** | Stochastic (Full) — Oversold | 71.9 | 69.2% | 0.81% | 1.7 |
| 🟢 BULLISH | **AERO-USD** | Williams %R — Oversold | 71.7 | 55.0% | 7.86% | 2.2 |
| 🟢 BULLISH | **AAPL** | Keltner — Lower Channel Touch | 71.0 | 55.0% | 1.66% | 2.13 |
| 🟢 BULLISH | **SOXL** | Aroon — Strong Uptrend | 70.1 | 61.1% | 4.43% | 2.09 |
| 🟢 BULLISH | **PLTR** | RSI Oversold | 69.7 | 56.2% | 3.27% | 2.19 |
| 🟢 BULLISH | **GC=F** | Keltner — Lower Channel Touch | 69.2 | 55.9% | 1.11% | 2.24 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 67.6 | 54.0% | 3.89% | 1.98 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 67.5 | 60.9% | 3.42% | 2.09 |
| 🟢 BULLISH | **CEG** | SMA 30 — Bullish Reclaim | 67.1 | 61.9% | 2.16% | 1.99 |
| 🟢 BULLISH | **XLE** | VWAP Deviation — Oversold | 66.9 | 69.4% | 0.72% | 1.35 |
| 🟢 BULLISH | **ATOM-USD** | Fisher Transform — Low Extreme | 66.2 | 62.6% | 2.46% | 1.96 |
| 🟢 BULLISH | **META** | Keltner — Lower Channel Touch | 65.2 | 52.2% | 1.57% | 1.8 |
| 🟢 BULLISH | **AERO-USD** | Stochastic (Full) — Oversold | 65.0 | 56.2% | 6.7% | 1.84 |
| 🟢 BULLISH | **DOGE-USD** | Keltner — Lower Channel Touch | 64.9 | 64.0% | 2.51% | 2.09 |
| 🟢 BULLISH | **PLTR** | VWAP Deviation — Oversold | 64.4 | 55.3% | 2.18% | 1.69 |
| 🟢 BULLISH | **GC=F** | Elder Force — Bullish | 64.1 | 53.3% | 0.59% | 1.67 |
| 🟢 BULLISH | **AERO-USD** | Keltner — Lower Channel Touch | 62.9 | 54.9% | 3.82% | 1.91 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 62.4 | 68.0% | 0.68% | 1.19 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 61.7 | 61.1% | 1.15% | 1.52 |
| 🟢 BULLISH | **DOT-USD** | RSI Oversold | 61.6 | 64.9% | 2.02% | 1.64 |
| 🟢 BULLISH | **CL=F** | Stochastic RSI Oversold | 60.7 | 60.3% | 1.31% | 1.66 |
| 🟢 BULLISH | **CL=F** | Fisher Transform — Low Extreme | 59.6 | 62.5% | 0.92% | 1.52 |
| 🟢 BULLISH | **TSLA** | VWAP Deviation — Oversold | 59.4 | 57.9% | 2.27% | 1.62 |
| 🟢 BULLISH | **PLTR** | Stochastic RSI Oversold | 58.8 | 54.0% | 2.24% | 1.42 |
| 🟢 BULLISH | **ARM** | Aroon — Strong Uptrend | 58.7 | 53.8% | 2.24% | 1.44 |
| 🟢 BULLISH | **MRVL** | CCI — Extreme Oversold | 58.4 | 59.2% | 1.95% | 1.39 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 58.1 | 57.1% | 1.95% | 1.41 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 56.1 | 59.4% | 3.19% | 1.36 |
| 🟢 BULLISH | **GOOGL** | Keltner — Lower Channel Touch | 55.9 | 57.8% | 1.07% | 1.49 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 55.8 | 58.4% | 2.4% | 1.22 |
| 🟢 BULLISH | **AMZN** | Williams %R — Oversold | 55.0 | 60.5% | 0.82% | 1.2 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 54.5 | 60.0% | 0.52% | 1.03 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 54.4 | 57.4% | 1.72% | 1.34 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 54.2 | 53.1% | 3.22% | 1.38 |
| 🟢 BULLISH | **XBI** | Aroon — Strong Uptrend | 54.2 | 58.3% | 0.56% | 1.05 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 54.1 | 57.7% | 0.85% | 1.2 |
| 🟢 BULLISH | **CRWD** | Chaikin Money Flow — Bullish | 53.8 | 56.7% | 1.26% | 1.19 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 53.6 | 61.3% | 0.37% | 0.88 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 53.5 | 59.4% | 0.65% | 1.07 |
| 🟢 BULLISH | **CRWD** | CCI — Extreme Oversold | 53.4 | 56.5% | 1.22% | 1.2 |
| 🟢 BULLISH | **XLK** | SMA 30 — Bullish Reclaim | 52.7 | 50.0% | 0.61% | 1.32 |
| 🟢 BULLISH | **DOGE-USD** | RSI Oversold | 52.7 | 60.7% | 1.5% | 1.21 |
| 🟢 BULLISH | **LTC-USD** | RSI Oversold | 52.7 | 65.9% | 1.2% | 1.16 |
| 🟢 BULLISH | **AMZN** | VWAP Deviation — Oversold | 52.3 | 58.9% | 0.89% | 1.17 |
| 🟢 BULLISH | **CL=F** | Keltner — Lower Channel Touch | 52.2 | 57.1% | 0.84% | 1.04 |
| 🟢 BULLISH | **APP** | Stochastic RSI Oversold | 51.8 | 51.2% | 2.89% | 1.19 |
| 🟢 BULLISH | **TQQQ** | CCI — Extreme Oversold | 51.2 | 59.4% | 1.29% | 0.98 |
| 🟢 BULLISH | **AVGO** | CCI — Extreme Oversold | 50.8 | 54.0% | 1.27% | 1.11 |
| 🟢 BULLISH | **XRP-USD** | VWAP Deviation — Oversold | 50.3 | 56.2% | 1.37% | 1.18 |
| 🟢 BULLISH | **UPRO** | CCI — Extreme Oversold | 50.1 | 59.6% | 0.86% | 0.83 |
| 🟢 BULLISH | **META** | Stochastic (Full) — Oversold | 50.0 | 52.5% | 0.86% | 1.11 |
| 🔴 BEARISH | **XLE** | Aroon — Strong Downtrend | 89.7 | 83.0% | 1.78% | 4.96 |
| 🔴 BEARISH | **SPY** | Chaikin Money Flow — Bearish | 88.7 | 73.0% | 1.99% | 4.06 |
| 🔴 BEARISH | **UPRO** | Chaikin Money Flow — Bearish | 88.2 | 71.8% | 5.82% | 4.24 |
| 🔴 BEARISH | **AAPL** | Chaikin Money Flow — Bearish | 86.5 | 78.8% | 4.15% | 6.08 |
| 🔴 BEARISH | **GC=F** | MFI — Overbought | 83.1 | 68.9% | 1.2% | 2.68 |
| 🔴 BEARISH | **META** | Chaikin Money Flow — Bearish | 82.3 | 64.5% | 2.51% | 3.43 |
| 🔴 BEARISH | **SOXL** | Ulcer Index — Elevated | 82.3 | 76.7% | 8.54% | 4.38 |
| 🔴 BEARISH | **SMH** | Ulcer Index — Elevated | 81.9 | 75.0% | 2.37% | 4.47 |
| 🔴 BEARISH | **MRVL** | Ulcer Index — Elevated | 81.1 | 72.9% | 3.64% | 4.02 |
| 🔴 BEARISH | **AVGO** | Ulcer Index — Elevated | 80.3 | 72.5% | 3.75% | 4.4 |
| 🔴 BEARISH | **MSFT** | Chaikin Money Flow — Bearish | 79.6 | 69.1% | 1.5% | 3.18 |
| 🔴 BEARISH | **AMD** | Williams %R — Overbought | 78.2 | 62.7% | 3.97% | 2.73 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 77.8 | 68.1% | 1.27% | 2.32 |
| 🔴 BEARISH | **AMD** | VWAP Deviation — Overbought | 76.5 | 64.0% | 3.68% | 2.66 |
| 🔴 BEARISH | **TQQQ** | EMA 9/21 — Bearish Cross | 76.0 | 70.0% | 3.64% | 2.74 |
| 🔴 BEARISH | **TQQQ** | Ulcer Index — Elevated | 75.7 | 70.5% | 3.02% | 2.62 |
| 🔴 BEARISH | **XLK** | Ulcer Index — Elevated | 74.6 | 66.4% | 1.27% | 2.58 |
| 🔴 BEARISH | **AAPL** | Aroon — Strong Downtrend | 73.5 | 60.0% | 1.3% | 2.1 |
| 🔴 BEARISH | **QQQ** | Ulcer Index — Elevated | 73.2 | 67.4% | 0.93% | 2.2 |
| 🔴 BEARISH | **RKLB** | Aroon — Strong Downtrend | 72.5 | 62.8% | 4.17% | 2.23 |
| 🔴 BEARISH | **NVDA** | Aroon — Strong Downtrend | 69.4 | 61.5% | 2.17% | 2.12 |
| 🔴 BEARISH | **META** | Ulcer Index — Elevated | 67.8 | 62.0% | 1.54% | 2.19 |
| 🔴 BEARISH | **MARA** | SMA 30 — Bearish Loss | 67.7 | 57.7% | 4.31% | 2.06 |
| 🔴 BEARISH | **RIOT** | Elder Force — Bearish | 67.6 | 59.4% | 3.8% | 2.02 |
| 🔴 BEARISH | **IONQ** | Ulcer Index — Elevated | 67.2 | 52.2% | 4.98% | 2.03 |
| 🔴 BEARISH | **RKLB** | Chaikin Money Flow — Bearish | 66.3 | 55.8% | 4.08% | 1.94 |
| 🔴 BEARISH | **ARM** | Ulcer Index — Elevated | 63.4 | 62.1% | 2.6% | 1.81 |
| 🔴 BEARISH | **PLTR** | Aroon — Strong Downtrend | 62.1 | 56.0% | 2.3% | 1.7 |
| 🔴 BEARISH | **UPRO** | Ulcer Index — Elevated | 60.7 | 62.1% | 1.52% | 1.45 |
| 🔴 BEARISH | **SPY** | Ulcer Index — Elevated | 59.1 | 63.5% | 0.47% | 1.23 |
| 🔴 BEARISH | **SMH** | VWAP Deviation — Overbought | 58.3 | 58.4% | 0.95% | 1.23 |
| 🔴 BEARISH | **APP** | Aroon — Strong Downtrend | 58.2 | 63.6% | 2.4% | 1.31 |
| 🔴 BEARISH | **PLTR** | Ulcer Index — Elevated | 57.4 | 52.3% | 2.01% | 1.37 |
| 🔴 BEARISH | **SOXL** | VWAP Deviation — Overbought | 55.8 | 56.1% | 3.11% | 1.34 |
| 🔴 BEARISH | **CEG** | Stochastic RSI Overbought | 54.1 | 58.4% | 1.69% | 1.27 |
| 🔴 BEARISH | **AAPL** | Ulcer Index — Elevated | 53.9 | 58.5% | 0.82% | 1.2 |
| 🔴 BEARISH | **SMCI** | Aroon — Strong Downtrend | 52.0 | 53.7% | 2.69% | 1.17 |

---
*Not financial advice. Backtests use historical data.*