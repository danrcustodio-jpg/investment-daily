# Strategy Alerts
**Last scan:** Wednesday June 10, 2026 at 04:30 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 116 |
| 🟢 Bullish | 109 |
| 🔴 Bearish | 45 |
| ✅ Fired this run (SMS + email) | 116 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 9 |

## 📲 SMS sent (3)

- One text per ticker: **GC=F, TQQQ, SOXL**
- Skipped — over per-scan cap: **NVDA, AVAX-USD, SPY, AVGO, MSFT, CL=F, AAPL, MRVL, SMH, IONQ, PLTR, QQQ, XLK, APP, RIOT, AMD, UPRO, RKLB, AERO-USD, XLE, ADA-USD, DOGE-USD, GOOGL, CEG, AMZN, TSLA, ARM, XRP-USD, MARA, META, CRWD** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **85.6** (1 BEAR signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **GC=F** | RSI Oversold | 100.0 | 4 | ADX Strong Trend — Bearish | 85.6 | 1 |
| **SOXL** | Aroon — Strong Uptrend | 65.6 | 1 | ATR — Volatility Surge (Down) | 89.3 | 2 |
| **AVGO** | VWAP Deviation — Oversold | 80.3 | 4 | Ulcer Index — Elevated | 82.6 | 2 |
| **AAPL** | VWAP Deviation — Oversold | 81.0 | 2 | ADX Strong Trend — Bearish | 81.0 | 1 |
| **MRVL** | Aroon — Strong Uptrend | 77.8 | 2 | Ulcer Index — Elevated | 81.0 | 1 |
| **SMH** | Aroon — Strong Uptrend | 74.5 | 1 | Ulcer Index — Elevated | 80.6 | 1 |
| **IONQ** | Aroon — Strong Uptrend | 79.1 | 2 | ADX Strong Trend — Bearish | 71.6 | 2 |
| **PLTR** | VWAP Deviation — Oversold | 73.7 | 2 | Aroon — Strong Downtrend | 71.1 | 1 |
| **AMD** | Aroon — Strong Uptrend | 69.9 | 1 | ADX Strong Trend — Bearish | 70.0 | 1 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **GC=F** | RSI Oversold | 100.0 | 100.0% | 3.93% | 10.92 |
| 🟢 BULLISH | **NVDA** | Williams %R — Oversold | 86.0 | 78.2% | 4.59% | 5.03 |
| 🟢 BULLISH | **AVAX-USD** | MFI — Oversold | 85.3 | 76.9% | 8.05% | 5.61 |
| 🟢 BULLISH | **NVDA** | VWAP Deviation — Oversold | 83.4 | 71.1% | 3.93% | 3.7 |
| 🟢 BULLISH | **NVDA** | Stochastic RSI Oversold | 82.7 | 72.3% | 3.46% | 3.75 |
| 🟢 BULLISH | **NVDA** | Stochastic (Full) — Oversold | 82.6 | 72.7% | 4.9% | 5.39 |
| 🟢 BULLISH | **CL=F** | VWAP Deviation — Oversold | 81.6 | 69.1% | 2.06% | 3.73 |
| 🟢 BULLISH | **AAPL** | VWAP Deviation — Oversold | 81.0 | 66.7% | 2.64% | 3.6 |
| 🟢 BULLISH | **AVGO** | VWAP Deviation — Oversold | 80.3 | 66.7% | 3.58% | 3.26 |
| 🟢 BULLISH | **IONQ** | Aroon — Strong Uptrend | 79.1 | 65.3% | 6.89% | 2.76 |
| 🟢 BULLISH | **AVGO** | Stochastic (Full) — Oversold | 78.7 | 65.5% | 2.81% | 2.57 |
| 🟢 BULLISH | **MRVL** | Aroon — Strong Uptrend | 77.8 | 63.2% | 3.43% | 2.32 |
| 🟢 BULLISH | **GC=F** | Keltner — Lower Channel Touch | 76.0 | 58.6% | 1.21% | 2.5 |
| 🟢 BULLISH | **SMH** | Aroon — Strong Uptrend | 74.5 | 65.3% | 1.48% | 2.17 |
| 🟢 BULLISH | **AVGO** | Williams %R — Oversold | 74.1 | 62.5% | 2.22% | 2.17 |
| 🟢 BULLISH | **PLTR** | VWAP Deviation — Oversold | 73.7 | 57.3% | 2.89% | 2.34 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 73.1 | 58.3% | 3.23% | 2.09 |
| 🟢 BULLISH | **AAPL** | Williams %R — Oversold | 72.8 | 60.0% | 1.52% | 2.19 |
| 🟢 BULLISH | **GC=F** | Williams %R — Oversold | 72.5 | 65.5% | 1.21% | 1.85 |
| 🟢 BULLISH | **APP** | Aroon — Strong Uptrend | 72.3 | 64.0% | 4.32% | 2.05 |
| 🟢 BULLISH | **AVGO** | Stochastic RSI Oversold | 71.4 | 60.2% | 2.15% | 2.16 |
| 🟢 BULLISH | **RIOT** | Williams %R — Oversold | 70.5 | 61.9% | 4.75% | 2.29 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 69.9 | 61.6% | 3.39% | 2.29 |
| 🟢 BULLISH | **GC=F** | Stochastic RSI Oversold | 69.7 | 68.2% | 0.92% | 1.65 |
| 🟢 BULLISH | **RIOT** | Aroon — Strong Uptrend | 69.4 | 59.7% | 3.72% | 1.99 |
| 🟢 BULLISH | **UPRO** | VWAP Deviation — Oversold | 69.3 | 62.3% | 2.85% | 1.98 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 69.2 | 54.4% | 4.05% | 2.08 |
| 🟢 BULLISH | **AERO-USD** | Stochastic (Full) — Oversold | 68.4 | 55.3% | 7.53% | 1.94 |
| 🟢 BULLISH | **XLE** | EMA 9/21 — Bullish Cross | 67.9 | 75.0% | 0.77% | 1.73 |
| 🟢 BULLISH | **UPRO** | Williams %R — Oversold | 67.9 | 63.0% | 2.41% | 1.93 |
| 🟢 BULLISH | **DOGE-USD** | Keltner — Lower Channel Touch | 66.4 | 65.3% | 2.44% | 2.02 |
| 🟢 BULLISH | **IONQ** | Chaikin Money Flow — Bullish | 66.3 | 55.8% | 5.42% | 2.01 |
| 🟢 BULLISH | **PLTR** | Stochastic RSI Oversold | 65.8 | 55.1% | 2.67% | 1.76 |
| 🟢 BULLISH | **SOXL** | Aroon — Strong Uptrend | 65.6 | 60.0% | 3.82% | 1.82 |
| 🟢 BULLISH | **GC=F** | Stochastic (Full) — Oversold | 63.8 | 64.3% | 0.97% | 1.43 |
| 🟢 BULLISH | **GOOGL** | ADX Strong Trend — Bullish | 63.4 | 55.5% | 1.11% | 1.7 |
| 🟢 BULLISH | **PLTR** | Williams %R — Oversold | 62.5 | 53.3% | 1.98% | 1.69 |
| 🟢 BULLISH | **CEG** | Fisher Transform — Low Extreme | 61.1 | 56.5% | 1.58% | 1.48 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 60.3 | 57.5% | 2.07% | 1.51 |
| 🟢 BULLISH | **AMZN** | Williams %R — Oversold | 59.6 | 62.0% | 1.0% | 1.45 |
| 🟢 BULLISH | **RIOT** | Stochastic RSI Oversold | 59.6 | 55.8% | 3.89% | 1.71 |
| 🟢 BULLISH | **SPY** | Aroon — Strong Uptrend | 59.3 | 61.5% | 0.35% | 1.14 |
| 🟢 BULLISH | **TSLA** | VWAP Deviation — Oversold | 59.2 | 56.9% | 2.33% | 1.64 |
| 🟢 BULLISH | **SMH** | Stochastic RSI Oversold | 59.1 | 61.8% | 1.29% | 1.47 |
| 🟢 BULLISH | **GOOGL** | Fisher Transform — Low Extreme | 58.7 | 62.2% | 1.26% | 1.63 |
| 🟢 BULLISH | **TQQQ** | Williams %R — Oversold | 57.7 | 62.3% | 2.26% | 1.35 |
| 🟢 BULLISH | **QQQ** | Aroon — Strong Uptrend | 57.4 | 61.1% | 0.49% | 1.12 |
| 🟢 BULLISH | **AMZN** | VWAP Deviation — Oversold | 57.1 | 60.3% | 1.11% | 1.48 |
| 🟢 BULLISH | **AMZN** | Stochastic (Full) — Oversold | 56.7 | 62.9% | 0.83% | 1.34 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 56.7 | 58.6% | 2.5% | 1.27 |
| 🟢 BULLISH | **RKLB** | Chaikin Money Flow — Bullish | 56.6 | 51.2% | 2.79% | 1.47 |
| 🟢 BULLISH | **RKLB** | VWAP Deviation — Oversold | 56.5 | 53.8% | 2.78% | 1.46 |
| 🟢 BULLISH | **XLK** | Chaikin Money Flow — Bullish | 56.5 | 62.0% | 0.63% | 1.14 |
| 🟢 BULLISH | **IONQ** | Stochastic RSI Oversold | 55.8 | 53.5% | 4.12% | 1.44 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 55.3 | 59.4% | 0.94% | 1.19 |
| 🟢 BULLISH | **XLK** | Stochastic RSI Oversold | 54.9 | 58.9% | 0.89% | 1.25 |
| 🟢 BULLISH | **TQQQ** | Aroon — Strong Uptrend | 54.8 | 61.1% | 1.18% | 1.06 |
| 🟢 BULLISH | **ARM** | Aroon — Strong Uptrend | 54.8 | 52.9% | 1.86% | 1.26 |
| 🟢 BULLISH | **AERO-USD** | Keltner — Lower Channel Touch | 54.7 | 50.0% | 2.99% | 1.43 |
| 🟢 BULLISH | **XLK** | Aroon — Strong Uptrend | 54.6 | 61.1% | 0.6% | 1.05 |
| 🟢 BULLISH | **AVAX-USD** | Fisher Transform — Low Extreme | 54.5 | 58.1% | 2.33% | 1.34 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 54.3 | 53.6% | 3.25% | 1.39 |
| 🟢 BULLISH | **PLTR** | Stochastic (Full) — Oversold | 53.5 | 51.9% | 1.43% | 1.25 |
| 🟢 BULLISH | **XRP-USD** | VWAP Deviation — Oversold | 53.1 | 56.7% | 1.52% | 1.28 |
| 🟢 BULLISH | **MARA** | Chaikin Money Flow — Bullish | 52.8 | 59.0% | 1.54% | 1.01 |
| 🟢 BULLISH | **SPY** | Stochastic RSI Oversold | 52.7 | 57.3% | 0.51% | 1.0 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 52.4 | 56.9% | 0.81% | 1.12 |
| 🟢 BULLISH | **RIOT** | VWAP Deviation — Oversold | 52.3 | 54.6% | 2.54% | 1.3 |
| 🟢 BULLISH | **AMD** | VWAP Deviation — Oversold | 52.2 | 56.0% | 1.2% | 1.33 |
| 🟢 BULLISH | **XLE** | SMA 30 — Bullish Reclaim | 51.8 | 61.5% | 0.6% | 1.07 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 51.7 | 56.6% | 2.36% | 1.35 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 51.5 | 60.3% | 0.34% | 0.78 |
| 🟢 BULLISH | **SOXL** | VWAP Deviation — Oversold | 51.3 | 62.8% | 2.76% | 1.08 |
| 🟢 BULLISH | **SOXL** | Stochastic RSI Oversold | 50.8 | 60.7% | 3.02% | 1.12 |
| 🟢 BULLISH | **RKLB** | Stochastic RSI Oversold | 50.6 | 43.7% | 2.98% | 1.26 |
| 🟢 BULLISH | **AMD** | Stochastic RSI Oversold | 50.6 | 54.0% | 1.43% | 1.28 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 50.5 | 58.8% | 0.43% | 0.82 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 50.5 | 57.9% | 2.54% | 1.07 |
| 🟢 BULLISH | **APP** | VWAP Deviation — Oversold | 50.4 | 57.8% | 1.62% | 0.95 |
| 🟢 BULLISH | **CRWD** | Aroon — Strong Uptrend | 50.0 | 55.3% | 1.1% | 1.04 |
| 🔴 BEARISH | **TQQQ** | ATR — Volatility Surge (Down) | 91.1 | 88.9% | 10.72% | 7.33 |
| 🔴 BEARISH | **SOXL** | ATR — Volatility Surge (Down) | 89.3 | 80.0% | 14.09% | 6.02 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 85.6 | 76.9% | 1.95% | 4.4 |
| 🔴 BEARISH | **SPY** | Vortex — Bearish | 84.3 | 78.9% | 0.95% | 2.83 |
| 🔴 BEARISH | **AVGO** | Ulcer Index — Elevated | 82.6 | 76.1% | 4.17% | 4.93 |
| 🔴 BEARISH | **MSFT** | Awesome Oscillator — Bearish Zero Line | 82.5 | 87.5% | 1.1% | 5.23 |
| 🔴 BEARISH | **SOXL** | Ulcer Index — Elevated | 81.2 | 75.7% | 7.87% | 4.13 |
| 🔴 BEARISH | **AAPL** | ADX Strong Trend — Bearish | 81.0 | 68.9% | 2.81% | 4.13 |
| 🔴 BEARISH | **MRVL** | Ulcer Index — Elevated | 81.0 | 73.6% | 3.59% | 4.06 |
| 🔴 BEARISH | **SMH** | Ulcer Index — Elevated | 80.6 | 73.7% | 2.12% | 4.2 |
| 🔴 BEARISH | **TQQQ** | Vortex — Bearish | 79.2 | 66.7% | 2.77% | 2.77 |
| 🔴 BEARISH | **AVGO** | Aroon — Strong Downtrend | 77.2 | 63.4% | 3.53% | 2.95 |
| 🔴 BEARISH | **TQQQ** | Ulcer Index — Elevated | 76.0 | 70.8% | 2.98% | 2.6 |
| 🔴 BEARISH | **QQQ** | Ulcer Index — Elevated | 73.0 | 67.5% | 0.9% | 2.12 |
| 🔴 BEARISH | **XLK** | Ulcer Index — Elevated | 72.7 | 65.4% | 1.2% | 2.43 |
| 🔴 BEARISH | **IONQ** | ADX Strong Trend — Bearish | 71.6 | 57.1% | 5.42% | 2.29 |
| 🔴 BEARISH | **PLTR** | Aroon — Strong Downtrend | 71.1 | 57.8% | 2.97% | 2.28 |
| 🔴 BEARISH | **AMD** | ADX Strong Trend — Bearish | 70.0 | 64.7% | 2.44% | 2.46 |
| 🔴 BEARISH | **XLK** | ADX Strong Trend — Bearish | 69.7 | 62.5% | 1.63% | 1.91 |
| 🔴 BEARISH | **IONQ** | Ulcer Index — Elevated | 69.3 | 54.1% | 5.41% | 2.16 |
| 🔴 BEARISH | **ADA-USD** | ATR — Volatility Surge (Down) | 67.2 | 55.6% | 7.1% | 3.37 |
| 🔴 BEARISH | **QQQ** | Vortex — Bearish | 66.9 | 62.5% | 0.7% | 1.8 |
| 🔴 BEARISH | **SPY** | ADX Strong Trend — Bearish | 63.0 | 65.9% | 0.83% | 1.39 |
| 🔴 BEARISH | **UPRO** | Ulcer Index — Elevated | 63.0 | 62.0% | 1.66% | 1.57 |
| 🔴 BEARISH | **CL=F** | Ulcer Index — Elevated | 61.7 | 60.0% | 1.47% | 1.75 |
| 🔴 BEARISH | **SPY** | Ulcer Index — Elevated | 60.9 | 63.6% | 0.51% | 1.32 |
| 🔴 BEARISH | **SMH** | ADX Strong Trend — Bearish | 60.7 | 59.7% | 1.72% | 1.64 |
| 🔴 BEARISH | **UPRO** | ADX Strong Trend — Bearish | 60.0 | 62.9% | 2.12% | 1.32 |
| 🔴 BEARISH | **AAPL** | Ulcer Index — Elevated | 59.1 | 60.0% | 1.0% | 1.47 |
| 🔴 BEARISH | **QQQ** | ADX Strong Trend — Bearish | 57.1 | 62.2% | 0.87% | 1.17 |
| 🔴 BEARISH | **CL=F** | Chaikin Money Flow — Bearish | 56.5 | 54.0% | 1.07% | 1.48 |
| 🔴 BEARISH | **SPY** | OBV — Distribution | 56.2 | 70.3% | 0.39% | 0.94 |
| 🔴 BEARISH | **TQQQ** | ADX Strong Trend — Bearish | 54.1 | 60.0% | 2.29% | 1.15 |
| 🔴 BEARISH | **TSLA** | Vortex — Bearish | 52.9 | 46.4% | 2.05% | 1.33 |
| 🔴 BEARISH | **META** | Aroon — Strong Downtrend | 52.3 | 56.7% | 1.01% | 1.07 |
| 🔴 BEARISH | **CEG** | PPO — Bearish Cross | 51.5 | 50.0% | 1.38% | 1.17 |

---
*Not financial advice. Backtests use historical data.*