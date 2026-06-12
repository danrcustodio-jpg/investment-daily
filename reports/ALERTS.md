# Strategy Alerts
**Last scan:** Friday June 12, 2026 at 04:12 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 105 |
| 🟢 Bullish | 95 |
| 🔴 Bearish | 45 |
| ✅ Fired this run (SMS + email) | 105 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 10 |

## 📲 SMS sent (3)

- One text per ticker: **NVDA, AVGO, XLE**
- Skipped — over per-scan cap: **GC=F, AAPL, SOXL, MRVL, CL=F, TQQQ, SMH, IONQ, GOOGL, IWM, PLTR, QQQ, XLK, AMD, RKLB, ARM, UPRO, CEG, SPY, TSLA, AMZN, APP, MARA, XRP-USD, META, AVAX-USD** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **81.9** (2 BEAR signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **AVGO** | Fisher Transform — Low Extreme | 88.7 | 5 | Ulcer Index — Elevated | 81.9 | 2 |
| **GC=F** | OBV — Accumulation | 78.3 | 2 | ADX Strong Trend — Bearish | 85.2 | 2 |
| **AAPL** | VWAP Deviation — Oversold | 81.0 | 3 | ADX Strong Trend — Bearish | 81.4 | 1 |
| **MRVL** | Aroon — Strong Uptrend | 77.7 | 2 | Ulcer Index — Elevated | 81.3 | 2 |
| **SOXL** | Aroon — Strong Uptrend | 66.8 | 1 | Ulcer Index — Elevated | 81.3 | 1 |
| **TQQQ** | SMA 30 — Bullish Reclaim | 69.0 | 1 | Awesome Oscillator — Bearish Zero Line | 81.1 | 2 |
| **SMH** | ADX Strong Trend — Bullish | 77.3 | 2 | Ulcer Index — Elevated | 80.7 | 1 |
| **IONQ** | Aroon — Strong Uptrend | 79.5 | 1 | Ulcer Index — Elevated | 69.3 | 2 |
| **PLTR** | VWAP Deviation — Oversold | 73.6 | 2 | Aroon — Strong Downtrend | 71.1 | 2 |
| **AMD** | ADX Strong Trend — Bullish | 70.6 | 2 | VWAP Deviation — Overbought | 71.8 | 1 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **NVDA** | Fisher Transform — Low Extreme | 90.9 | 100.0% | 9.45% | 13.38 |
| 🟢 BULLISH | **AVGO** | Fisher Transform — Low Extreme | 88.7 | 87.0% | 6.28% | 5.62 |
| 🟢 BULLISH | **NVDA** | Williams %R — Oversold | 85.4 | 76.8% | 4.51% | 4.96 |
| 🟢 BULLISH | **NVDA** | VWAP Deviation — Oversold | 83.0 | 70.1% | 3.87% | 3.67 |
| 🟢 BULLISH | **NVDA** | Stochastic (Full) — Oversold | 82.6 | 72.7% | 4.9% | 5.39 |
| 🟢 BULLISH | **CL=F** | VWAP Deviation — Oversold | 81.2 | 68.1% | 1.94% | 3.4 |
| 🟢 BULLISH | **AAPL** | VWAP Deviation — Oversold | 81.0 | 66.7% | 2.64% | 3.6 |
| 🟢 BULLISH | **AVGO** | VWAP Deviation — Oversold | 79.9 | 65.9% | 3.52% | 3.21 |
| 🟢 BULLISH | **IONQ** | Aroon — Strong Uptrend | 79.5 | 65.8% | 6.9% | 2.76 |
| 🟢 BULLISH | **AVGO** | Stochastic (Full) — Oversold | 78.7 | 65.5% | 2.81% | 2.57 |
| 🟢 BULLISH | **GC=F** | OBV — Accumulation | 78.3 | 68.4% | 0.95% | 2.09 |
| 🟢 BULLISH | **MRVL** | Aroon — Strong Uptrend | 77.7 | 63.4% | 3.41% | 2.31 |
| 🟢 BULLISH | **SMH** | ADX Strong Trend — Bullish | 77.3 | 64.4% | 1.57% | 2.34 |
| 🟢 BULLISH | **IWM** | Parabolic SAR — Bullish | 76.9 | 56.5% | 0.97% | 2.45 |
| 🟢 BULLISH | **NVDA** | Stochastic RSI Oversold | 75.5 | 66.7% | 2.66% | 2.55 |
| 🟢 BULLISH | **SMH** | Aroon — Strong Uptrend | 75.1 | 65.4% | 1.51% | 2.22 |
| 🟢 BULLISH | **PLTR** | VWAP Deviation — Oversold | 73.6 | 57.3% | 2.89% | 2.34 |
| 🟢 BULLISH | **AAPL** | Stochastic (Full) — Oversold | 73.0 | 59.3% | 1.59% | 2.12 |
| 🟢 BULLISH | **AAPL** | Williams %R — Oversold | 72.8 | 60.0% | 1.52% | 2.19 |
| 🟢 BULLISH | **CL=F** | Stochastic (Full) — Oversold | 71.8 | 62.0% | 1.33% | 2.48 |
| 🟢 BULLISH | **AVGO** | Williams %R — Oversold | 71.2 | 60.8% | 2.03% | 1.97 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 70.9 | 57.2% | 3.03% | 1.95 |
| 🟢 BULLISH | **AMD** | ADX Strong Trend — Bullish | 70.6 | 62.8% | 3.37% | 2.29 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 70.4 | 61.8% | 3.43% | 2.33 |
| 🟢 BULLISH | **TQQQ** | SMA 30 — Bullish Reclaim | 69.0 | 65.2% | 1.89% | 2.07 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 68.8 | 54.0% | 3.99% | 2.05 |
| 🟢 BULLISH | **GC=F** | Stochastic RSI Oversold | 67.3 | 66.7% | 0.9% | 1.57 |
| 🟢 BULLISH | **SOXL** | Aroon — Strong Uptrend | 66.8 | 60.2% | 3.94% | 1.88 |
| 🟢 BULLISH | **PLTR** | Stochastic RSI Oversold | 66.4 | 56.1% | 2.78% | 1.79 |
| 🟢 BULLISH | **AVGO** | Stochastic RSI Oversold | 65.9 | 59.2% | 1.93% | 1.84 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 64.7 | 68.3% | 0.73% | 1.31 |
| 🟢 BULLISH | **GC=F** | Elder Force — Bullish | 64.1 | 53.3% | 0.59% | 1.67 |
| 🟢 BULLISH | **GC=F** | Stochastic (Full) — Oversold | 63.8 | 64.3% | 0.97% | 1.43 |
| 🟢 BULLISH | **CEG** | Fisher Transform — Low Extreme | 61.1 | 56.5% | 1.58% | 1.48 |
| 🟢 BULLISH | **PLTR** | Williams %R — Oversold | 60.2 | 52.5% | 1.85% | 1.57 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 59.7 | 57.3% | 2.03% | 1.48 |
| 🟢 BULLISH | **CL=F** | Williams %R — Oversold | 59.6 | 59.2% | 1.01% | 1.65 |
| 🟢 BULLISH | **TSLA** | VWAP Deviation — Oversold | 58.8 | 56.4% | 2.3% | 1.62 |
| 🟢 BULLISH | **TQQQ** | OBV — Accumulation | 57.8 | 66.7% | 1.78% | 1.36 |
| 🟢 BULLISH | **AMZN** | Williams %R — Oversold | 57.6 | 61.3% | 0.93% | 1.34 |
| 🟢 BULLISH | **XLK** | Chaikin Money Flow — Bullish | 57.1 | 62.4% | 0.64% | 1.16 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 56.2 | 59.6% | 0.97% | 1.24 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 56.1 | 58.4% | 2.44% | 1.24 |
| 🟢 BULLISH | **SPY** | Stochastic RSI Oversold | 56.0 | 57.5% | 0.58% | 1.2 |
| 🟢 BULLISH | **IONQ** | Stochastic RSI Oversold | 55.8 | 54.0% | 4.09% | 1.44 |
| 🟢 BULLISH | **MARA** | OBV — Accumulation | 55.7 | 53.1% | 2.4% | 1.39 |
| 🟢 BULLISH | **XLK** | Stochastic RSI Oversold | 55.6 | 58.8% | 0.91% | 1.27 |
| 🟢 BULLISH | **XLK** | Aroon — Strong Uptrend | 55.6 | 61.5% | 0.62% | 1.1 |
| 🟢 BULLISH | **RKLB** | VWAP Deviation — Oversold | 55.5 | 53.3% | 2.68% | 1.41 |
| 🟢 BULLISH | **APP** | Stochastic RSI Oversold | 55.0 | 53.0% | 3.21% | 1.32 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 53.8 | 53.3% | 3.2% | 1.37 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 53.6 | 56.6% | 2.51% | 1.44 |
| 🟢 BULLISH | **MARA** | Chaikin Money Flow — Bullish | 53.4 | 58.8% | 1.62% | 1.07 |
| 🟢 BULLISH | **PLTR** | Stochastic (Full) — Oversold | 53.3 | 51.9% | 1.43% | 1.25 |
| 🟢 BULLISH | **XRP-USD** | VWAP Deviation — Oversold | 52.9 | 56.6% | 1.51% | 1.28 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 52.6 | 56.9% | 0.81% | 1.13 |
| 🟢 BULLISH | **AMZN** | VWAP Deviation — Oversold | 52.5 | 58.6% | 0.95% | 1.23 |
| 🟢 BULLISH | **RKLB** | Stochastic RSI Oversold | 51.7 | 44.0% | 3.12% | 1.33 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 51.2 | 60.3% | 0.33% | 0.76 |
| 🟢 BULLISH | **AVAX-USD** | Fisher Transform — Low Extreme | 51.2 | 56.0% | 2.06% | 1.19 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 51.1 | 57.9% | 2.61% | 1.1 |
| 🟢 BULLISH | **AMD** | Stochastic RSI Oversold | 51.0 | 54.5% | 1.43% | 1.28 |
| 🟢 BULLISH | **GC=F** | Fisher Transform — Low Extreme | 50.9 | 64.3% | 0.52% | 0.55 |
| 🟢 BULLISH | **AMZN** | Stochastic (Full) — Oversold | 50.8 | 60.9% | 0.66% | 1.01 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 50.8 | 59.0% | 0.44% | 0.83 |
| 🟢 BULLISH | **APP** | VWAP Deviation — Oversold | 50.4 | 57.8% | 1.62% | 0.95 |
| 🟢 BULLISH | **GOOGL** | Stochastic RSI Oversold | 50.3 | 55.8% | 0.71% | 0.95 |
| 🔴 BEARISH | **XLE** | Chaikin Money Flow — Bearish | 86.7 | 74.0% | 1.43% | 2.96 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 85.2 | 75.6% | 1.82% | 4.09 |
| 🔴 BEARISH | **GC=F** | Ulcer Index — Elevated | 83.2 | 72.8% | 1.89% | 4.01 |
| 🔴 BEARISH | **AVGO** | Ulcer Index — Elevated | 81.9 | 74.5% | 3.98% | 4.62 |
| 🔴 BEARISH | **AAPL** | ADX Strong Trend — Bearish | 81.4 | 68.1% | 2.37% | 3.46 |
| 🔴 BEARISH | **SOXL** | Ulcer Index — Elevated | 81.3 | 75.9% | 8.07% | 4.2 |
| 🔴 BEARISH | **MRVL** | Ulcer Index — Elevated | 81.3 | 73.9% | 3.63% | 4.12 |
| 🔴 BEARISH | **TQQQ** | Awesome Oscillator — Bearish Zero Line | 81.1 | 72.7% | 2.74% | 2.8 |
| 🔴 BEARISH | **SMH** | Ulcer Index — Elevated | 80.7 | 74.0% | 2.19% | 4.28 |
| 🔴 BEARISH | **GOOGL** | Chaikin Money Flow — Bearish | 77.3 | 72.7% | 1.88% | 2.9 |
| 🔴 BEARISH | **AVGO** | Aroon — Strong Downtrend | 77.0 | 62.9% | 3.49% | 2.92 |
| 🔴 BEARISH | **TQQQ** | Ulcer Index — Elevated | 76.3 | 71.1% | 3.0% | 2.62 |
| 🔴 BEARISH | **QQQ** | Ulcer Index — Elevated | 73.3 | 67.8% | 0.91% | 2.15 |
| 🔴 BEARISH | **XLK** | Ulcer Index — Elevated | 73.1 | 65.7% | 1.21% | 2.47 |
| 🔴 BEARISH | **MRVL** | VWAP Deviation — Overbought | 72.7 | 59.3% | 2.93% | 1.98 |
| 🔴 BEARISH | **AMD** | VWAP Deviation — Overbought | 71.8 | 62.8% | 3.3% | 2.31 |
| 🔴 BEARISH | **XLK** | ADX Strong Trend — Bearish | 71.5 | 63.0% | 1.74% | 2.05 |
| 🔴 BEARISH | **PLTR** | Aroon — Strong Downtrend | 71.1 | 57.8% | 2.97% | 2.28 |
| 🔴 BEARISH | **IONQ** | Ulcer Index — Elevated | 69.3 | 54.1% | 5.41% | 2.16 |
| 🔴 BEARISH | **ARM** | Ulcer Index — Elevated | 68.2 | 63.4% | 2.77% | 2.05 |
| 🔴 BEARISH | **PLTR** | Ulcer Index — Elevated | 66.6 | 54.2% | 2.57% | 1.83 |
| 🔴 BEARISH | **IONQ** | ADX Strong Trend — Bearish | 65.9 | 57.4% | 4.36% | 1.97 |
| 🔴 BEARISH | **NVDA** | Aroon — Strong Downtrend | 63.9 | 60.3% | 1.84% | 1.74 |
| 🔴 BEARISH | **UPRO** | Ulcer Index — Elevated | 61.5 | 62.0% | 1.56% | 1.47 |
| 🔴 BEARISH | **XLE** | Awesome Oscillator — Bearish Zero Line | 61.2 | 62.5% | 0.64% | 1.22 |
| 🔴 BEARISH | **SPY** | Ulcer Index — Elevated | 59.3 | 63.6% | 0.48% | 1.22 |
| 🔴 BEARISH | **SPY** | ADX Strong Trend — Bearish | 58.3 | 63.5% | 0.69% | 1.14 |
| 🔴 BEARISH | **SMH** | VWAP Deviation — Overbought | 58.0 | 58.5% | 0.93% | 1.22 |
| 🔴 BEARISH | **ARM** | PPO — Bearish Cross | 56.6 | 52.9% | 1.62% | 1.46 |
| 🔴 BEARISH | **AAPL** | Ulcer Index — Elevated | 56.5 | 59.3% | 0.93% | 1.34 |
| 🔴 BEARISH | **CL=F** | Chaikin Money Flow — Bearish | 56.5 | 54.0% | 1.07% | 1.48 |
| 🔴 BEARISH | **UPRO** | ADX Strong Trend — Bearish | 56.1 | 61.1% | 1.76% | 1.11 |
| 🔴 BEARISH | **APP** | PPO — Bearish Cross | 55.7 | 50.0% | 4.73% | 1.41 |
| 🔴 BEARISH | **QQQ** | ADX Strong Trend — Bearish | 55.4 | 61.8% | 0.81% | 1.08 |
| 🔴 BEARISH | **TQQQ** | ADX Strong Trend — Bearish | 53.4 | 59.8% | 2.19% | 1.1 |
| 🔴 BEARISH | **META** | Aroon — Strong Downtrend | 52.5 | 57.1% | 1.02% | 1.08 |
| 🔴 BEARISH | **RKLB** | Awesome Oscillator — Bearish Zero Line | 51.8 | 42.9% | 3.19% | 1.37 |
| 🔴 BEARISH | **SOXL** | VWAP Deviation — Overbought | 50.1 | 54.5% | 2.48% | 1.05 |

---
*Not financial advice. Backtests use historical data.*