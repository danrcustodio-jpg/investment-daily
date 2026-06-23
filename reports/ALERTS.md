# Strategy Alerts
**Last scan:** Tuesday June 23, 2026 at 01:51 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 96 |
| 🟢 Bullish | 78 |
| 🔴 Bearish | 42 |
| ✅ Fired this run (SMS + email) | 96 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 8 |

## 📲 SMS sent (3)

- One text per ticker: **PLTR, XLE, GC=F**
- Skipped — over per-scan cap: **NVDA, SPY, AAPL, XLK, MSFT, APP, SOXL, MRVL, QQQ, AVGO, RKLB, TQQQ, AMD, SMH, RIOT, CL=F, IONQ, AERO-USD, ARM, ETH-USD, DOGE-USD, UPRO, TSLA, LINK-USD, CEG, AMZN, DOT-USD, ADA-USD, GOOGL, CRWD, XBI, META, XRP-USD, SMCI** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **68.1** (1 BEAR signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **PLTR** | MFI — Oversold | 100.0 | 2 | Aroon — Strong Downtrend | 68.1 | 1 |
| **XLE** | Stochastic (Full) — Oversold | 73.9 | 2 | Aroon — Strong Downtrend | 90.4 | 2 |
| **GC=F** | VWAP Deviation — Oversold | 87.7 | 3 | ADX Strong Trend — Bearish | 84.3 | 1 |
| **SOXL** | Aroon — Strong Uptrend | 70.0 | 1 | Ulcer Index — Elevated | 81.9 | 1 |
| **MRVL** | ADX Strong Trend — Bullish | 80.2 | 2 | Ulcer Index — Elevated | 81.8 | 2 |
| **AVGO** | VWAP Deviation — Oversold | 79.9 | 2 | Ulcer Index — Elevated | 80.8 | 1 |
| **RKLB** | CCI — Extreme Oversold | 68.6 | 1 | Aroon — Strong Downtrend | 78.2 | 1 |
| **AMD** | Aroon — Strong Uptrend | 71.8 | 3 | Stochastic (Full) — Overbought | 77.4 | 1 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **PLTR** | MFI — Oversold | 100.0 | 100.0% | 7.17% | 29.41 |
| 🟢 BULLISH | **GC=F** | VWAP Deviation — Oversold | 87.7 | 79.3% | 2.64% | 5.31 |
| 🟢 BULLISH | **NVDA** | Williams %R — Oversold | 86.7 | 80.0% | 4.35% | 4.93 |
| 🟢 BULLISH | **NVDA** | VWAP Deviation — Oversold | 84.7 | 74.7% | 4.06% | 4.01 |
| 🟢 BULLISH | **MSFT** | MFI — Oversold | 83.3 | 83.3% | 1.73% | 5.56 |
| 🟢 BULLISH | **APP** | Fisher Transform — Low Extreme | 81.9 | 71.4% | 5.6% | 3.61 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 80.2 | 62.2% | 3.92% | 2.52 |
| 🟢 BULLISH | **AVGO** | VWAP Deviation — Oversold | 79.9 | 66.3% | 3.54% | 3.31 |
| 🟢 BULLISH | **MRVL** | Aroon — Strong Uptrend | 79.3 | 64.2% | 3.55% | 2.41 |
| 🟢 BULLISH | **SMH** | Aroon — Strong Uptrend | 76.5 | 65.9% | 1.62% | 2.37 |
| 🟢 BULLISH | **RIOT** | Aroon — Strong Uptrend | 76.5 | 63.0% | 4.43% | 2.45 |
| 🟢 BULLISH | **CL=F** | Stochastic RSI Oversold | 76.1 | 66.0% | 1.89% | 2.54 |
| 🟢 BULLISH | **XLE** | Stochastic (Full) — Oversold | 73.9 | 70.3% | 0.85% | 1.79 |
| 🟢 BULLISH | **XLE** | VWAP Deviation — Oversold | 73.8 | 73.5% | 0.87% | 1.68 |
| 🟢 BULLISH | **CL=F** | Fisher Transform — Low Extreme | 72.7 | 64.5% | 1.24% | 2.37 |
| 🟢 BULLISH | **AERO-USD** | RSI Oversold | 72.6 | 57.1% | 6.26% | 3.2 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 71.8 | 62.5% | 3.56% | 2.43 |
| 🟢 BULLISH | **AERO-USD** | Williams %R — Oversold | 71.8 | 55.0% | 7.86% | 2.2 |
| 🟢 BULLISH | **PLTR** | VWAP Deviation — Oversold | 71.1 | 56.4% | 2.56% | 2.08 |
| 🟢 BULLISH | **AVGO** | Williams %R — Oversold | 70.9 | 60.0% | 1.99% | 1.98 |
| 🟢 BULLISH | **GC=F** | Keltner — Lower Channel Touch | 70.2 | 55.9% | 1.11% | 2.24 |
| 🟢 BULLISH | **SOXL** | Aroon — Strong Uptrend | 70.0 | 61.1% | 4.43% | 2.09 |
| 🟢 BULLISH | **AMD** | ADX Strong Trend — Bullish | 69.5 | 61.4% | 3.21% | 2.2 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 68.6 | 54.1% | 3.99% | 2.05 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 66.8 | 60.2% | 3.41% | 2.06 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 65.6 | 68.5% | 0.75% | 1.36 |
| 🟢 BULLISH | **DOGE-USD** | Keltner — Lower Channel Touch | 65.2 | 64.0% | 2.51% | 2.09 |
| 🟢 BULLISH | **CL=F** | Keltner — Lower Channel Touch | 65.0 | 59.4% | 1.27% | 1.77 |
| 🟢 BULLISH | **AERO-USD** | Keltner — Lower Channel Touch | 63.3 | 54.9% | 3.82% | 1.91 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 61.1 | 60.8% | 1.14% | 1.49 |
| 🟢 BULLISH | **ARM** | Aroon — Strong Uptrend | 61.0 | 54.4% | 2.4% | 1.55 |
| 🟢 BULLISH | **PLTR** | Stochastic RSI Oversold | 60.9 | 53.7% | 2.3% | 1.52 |
| 🟢 BULLISH | **TSLA** | VWAP Deviation — Oversold | 60.4 | 58.3% | 2.33% | 1.67 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 59.2 | 57.2% | 2.02% | 1.47 |
| 🟢 BULLISH | **MRVL** | CCI — Extreme Oversold | 58.4 | 59.2% | 1.95% | 1.39 |
| 🟢 BULLISH | **AMZN** | Williams %R — Oversold | 56.8 | 61.2% | 0.88% | 1.3 |
| 🟢 BULLISH | **PLTR** | Williams %R — Oversold | 56.7 | 51.5% | 1.58% | 1.37 |
| 🟢 BULLISH | **DOT-USD** | RSI Oversold | 56.6 | 63.0% | 1.73% | 1.38 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 56.1 | 58.5% | 2.44% | 1.23 |
| 🟢 BULLISH | **ADA-USD** | RSI Oversold | 55.7 | 63.3% | 2.19% | 1.36 |
| 🟢 BULLISH | **TQQQ** | VWAP Deviation — Oversold | 55.5 | 62.2% | 2.26% | 1.23 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 55.4 | 59.1% | 3.13% | 1.33 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 54.7 | 57.9% | 0.87% | 1.23 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 54.7 | 60.2% | 0.52% | 1.03 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 54.5 | 53.2% | 3.25% | 1.39 |
| 🟢 BULLISH | **AMZN** | VWAP Deviation — Oversold | 54.2 | 60.3% | 0.95% | 1.26 |
| 🟢 BULLISH | **CRWD** | Chaikin Money Flow — Bullish | 54.0 | 57.1% | 1.27% | 1.2 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 53.8 | 61.4% | 0.37% | 0.89 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 53.7 | 57.1% | 1.69% | 1.31 |
| 🟢 BULLISH | **CRWD** | CCI — Extreme Oversold | 53.4 | 56.6% | 1.22% | 1.2 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 53.2 | 59.3% | 0.65% | 1.06 |
| 🟢 BULLISH | **CL=F** | VWAP Deviation — Oversold | 53.2 | 62.7% | 0.8% | 0.93 |
| 🟢 BULLISH | **DOGE-USD** | RSI Oversold | 52.3 | 60.3% | 1.46% | 1.19 |
| 🟢 BULLISH | **RKLB** | VWAP Deviation — Oversold | 52.1 | 51.3% | 2.33% | 1.24 |
| 🟢 BULLISH | **XBI** | Aroon — Strong Uptrend | 51.9 | 57.8% | 0.5% | 0.92 |
| 🟢 BULLISH | **TQQQ** | CCI — Extreme Oversold | 51.3 | 59.5% | 1.29% | 0.98 |
| 🟢 BULLISH | **AVGO** | CCI — Extreme Oversold | 50.6 | 53.9% | 1.27% | 1.1 |
| 🟢 BULLISH | **XRP-USD** | VWAP Deviation — Oversold | 50.4 | 56.2% | 1.37% | 1.18 |
| 🟢 BULLISH | **UPRO** | CCI — Extreme Oversold | 50.3 | 59.7% | 0.87% | 0.84 |
| 🔴 BEARISH | **XLE** | Aroon — Strong Downtrend | 90.4 | 84.8% | 1.86% | 5.29 |
| 🔴 BEARISH | **SPY** | SMA 30 — Bearish Loss | 86.7 | 82.4% | 1.31% | 4.23 |
| 🔴 BEARISH | **AAPL** | Chaikin Money Flow — Bearish | 86.5 | 78.8% | 4.15% | 6.08 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 84.3 | 72.9% | 1.71% | 3.78 |
| 🔴 BEARISH | **XLK** | OBV — Distribution | 84.1 | 73.9% | 1.6% | 2.79 |
| 🔴 BEARISH | **SOXL** | Ulcer Index — Elevated | 81.9 | 76.3% | 8.62% | 4.4 |
| 🔴 BEARISH | **MRVL** | Ulcer Index — Elevated | 81.8 | 74.5% | 3.8% | 4.23 |
| 🔴 BEARISH | **QQQ** | SMA 30 — Bearish Loss | 81.2 | 69.6% | 1.1% | 3.07 |
| 🔴 BEARISH | **AVGO** | Ulcer Index — Elevated | 80.8 | 73.0% | 3.84% | 4.5 |
| 🔴 BEARISH | **MRVL** | MACD Bearish Crossover | 80.0 | 68.4% | 4.36% | 3.65 |
| 🔴 BEARISH | **XLE** | Chaikin Money Flow — Bearish | 79.8 | 71.1% | 1.2% | 2.34 |
| 🔴 BEARISH | **RKLB** | Aroon — Strong Downtrend | 78.2 | 64.5% | 4.85% | 2.72 |
| 🔴 BEARISH | **TQQQ** | Ulcer Index — Elevated | 77.7 | 71.7% | 3.17% | 2.77 |
| 🔴 BEARISH | **AMD** | Stochastic (Full) — Overbought | 77.4 | 60.5% | 4.11% | 2.73 |
| 🔴 BEARISH | **TQQQ** | SMA 30 — Bearish Loss | 76.9 | 70.8% | 2.25% | 2.32 |
| 🔴 BEARISH | **TQQQ** | Elder Force — Bearish | 76.3 | 69.4% | 2.35% | 2.34 |
| 🔴 BEARISH | **XLK** | Ulcer Index — Elevated | 75.4 | 66.7% | 1.31% | 2.67 |
| 🔴 BEARISH | **QQQ** | Ulcer Index — Elevated | 74.9 | 68.5% | 0.97% | 2.32 |
| 🔴 BEARISH | **IONQ** | Awesome Oscillator — Bearish Zero Line | 72.7 | 75.0% | 6.31% | 2.31 |
| 🔴 BEARISH | **ARM** | Ulcer Index — Elevated | 69.4 | 63.5% | 3.0% | 2.15 |
| 🔴 BEARISH | **IONQ** | Ulcer Index — Elevated | 68.3 | 53.1% | 5.17% | 2.09 |
| 🔴 BEARISH | **PLTR** | Aroon — Strong Downtrend | 68.1 | 57.0% | 2.66% | 2.04 |
| 🔴 BEARISH | **ETH-USD** | Parabolic SAR — Bearish | 66.9 | 59.4% | 2.84% | 1.88 |
| 🔴 BEARISH | **SOXL** | Stochastic (Full) — Overbought | 64.7 | 60.0% | 3.98% | 1.69 |
| 🔴 BEARISH | **UPRO** | Ulcer Index — Elevated | 63.2 | 63.2% | 1.62% | 1.56 |
| 🔴 BEARISH | **PLTR** | Ulcer Index — Elevated | 63.1 | 53.2% | 2.36% | 1.67 |
| 🔴 BEARISH | **SPY** | Ulcer Index — Elevated | 61.4 | 64.6% | 0.51% | 1.33 |
| 🔴 BEARISH | **RIOT** | Vortex — Bearish | 58.7 | 50.0% | 4.34% | 1.71 |
| 🔴 BEARISH | **AAPL** | Ulcer Index — Elevated | 58.4 | 60.9% | 0.94% | 1.41 |
| 🔴 BEARISH | **LINK-USD** | Parabolic SAR — Bearish | 58.4 | 51.7% | 2.34% | 1.62 |
| 🔴 BEARISH | **APP** | Aroon — Strong Downtrend | 57.2 | 63.1% | 2.31% | 1.26 |
| 🔴 BEARISH | **CEG** | Stochastic RSI Overbought | 57.2 | 58.5% | 1.93% | 1.46 |
| 🔴 BEARISH | **SMH** | Stochastic (Full) — Overbought | 55.5 | 58.0% | 0.84% | 1.1 |
| 🔴 BEARISH | **SOXL** | VWAP Deviation — Overbought | 55.5 | 55.7% | 3.11% | 1.33 |
| 🔴 BEARISH | **ARM** | MACD Bearish Crossover | 53.6 | 44.4% | 2.26% | 1.52 |
| 🔴 BEARISH | **META** | Aroon — Strong Downtrend | 51.1 | 56.8% | 0.98% | 1.05 |
| 🔴 BEARISH | **SMCI** | Aroon — Strong Downtrend | 50.0 | 52.8% | 2.5% | 1.08 |

---
*Not financial advice. Backtests use historical data.*