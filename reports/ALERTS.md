# Strategy Alerts
**Last scan:** Monday August 10, 2026 at 02:14 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 102 |
| 🟢 Bullish | 59 |
| 🔴 Bearish | 67 |
| ✅ Fired this run (SMS + email) | 102 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 4 |

## 📲 SMS sent (3)

- One text per ticker: **GOOGL, GC=F, AAPL**
- Skipped — over per-scan cap: **ARKK, SOL-USD, ADA-USD, XLK, CEG, APP, RKLB, MRVL, NVDA, MARA, MSFT, IONQ, META, XBI, CRWD, SMH, QQQ, AMD, XLE, AERO-USD, CL=F, SPY, UPRO, PLTR, RIOT, SOXL, TSLA, AVGO, AMZN, TQQQ** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **66.9** (1 BULL signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **GOOGL** | Aroon — Strong Uptrend | 66.9 | 1 | Chaikin Money Flow — Bearish | 89.1 | 1 |
| **AAPL** | VWAP Deviation — Oversold | 83.0 | 2 | Aroon — Strong Downtrend | 71.8 | 1 |
| **RKLB** | ADX Strong Trend — Bullish | 68.3 | 1 | Stochastic RSI Overbought | 75.2 | 4 |
| **IONQ** | ADX Strong Trend — Bullish | 69.7 | 1 | Fisher Transform — High Extreme | 70.1 | 2 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **GC=F** | OBV — Accumulation | 85.6 | 77.8% | 1.21% | 2.74 |
| 🟢 BULLISH | **AAPL** | VWAP Deviation — Oversold | 83.0 | 70.5% | 2.9% | 3.88 |
| 🟢 BULLISH | **AAPL** | Williams %R — Oversold | 80.1 | 64.2% | 1.88% | 2.74 |
| 🟢 BULLISH | **ARKK** | PPO — Bullish Cross | 80.0 | 68.4% | 3.09% | 2.84 |
| 🟢 BULLISH | **SOL-USD** | EMA 9/21 — Bullish Cross | 80.0 | 71.4% | 3.11% | 2.86 |
| 🟢 BULLISH | **ARKK** | TRIX — Bullish Cross | 79.3 | 76.9% | 2.56% | 2.55 |
| 🟢 BULLISH | **APP** | Keltner — Lower Channel Touch | 76.4 | 64.0% | 3.6% | 2.68 |
| 🟢 BULLISH | **APP** | RSI Oversold | 74.3 | 66.7% | 4.17% | 2.41 |
| 🟢 BULLISH | **NVDA** | Aroon — Strong Uptrend | 70.8 | 62.6% | 1.54% | 2.04 |
| 🟢 BULLISH | **IONQ** | ADX Strong Trend — Bullish | 69.7 | 59.6% | 5.61% | 2.16 |
| 🟢 BULLISH | **RKLB** | ADX Strong Trend — Bullish | 68.3 | 55.3% | 4.11% | 2.13 |
| 🟢 BULLISH | **CRWD** | 52-Week Breakout | 67.5 | 64.7% | 2.83% | 2.01 |
| 🟢 BULLISH | **GOOGL** | Aroon — Strong Uptrend | 66.9 | 60.1% | 1.27% | 1.86 |
| 🟢 BULLISH | **SMH** | TRIX — Bullish Cross | 66.7 | 66.7% | 1.2% | 1.66 |
| 🟢 BULLISH | **QQQ** | Aroon — Strong Uptrend | 66.6 | 63.8% | 0.65% | 1.62 |
| 🟢 BULLISH | **GC=F** | Aroon — Strong Uptrend | 65.5 | 64.1% | 0.8% | 1.53 |
| 🟢 BULLISH | **XLE** | Vortex — Bullish | 65.2 | 63.2% | 0.7% | 1.66 |
| 🟢 BULLISH | **AERO-USD** | Williams %R — Oversold | 64.8 | 51.1% | 6.31% | 1.85 |
| 🟢 BULLISH | **XLK** | Aroon — Strong Uptrend | 64.2 | 63.9% | 0.84% | 1.59 |
| 🟢 BULLISH | **CL=F** | Stochastic RSI Oversold | 64.2 | 61.3% | 1.41% | 1.78 |
| 🟢 BULLISH | **CRWD** | ADX Strong Trend — Bullish | 64.1 | 60.0% | 1.65% | 1.53 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 61.8 | 53.4% | 3.49% | 1.75 |
| 🟢 BULLISH | **SPY** | Aroon — Strong Uptrend | 61.8 | 62.1% | 0.38% | 1.32 |
| 🟢 BULLISH | **AAPL** | Stochastic RSI Oversold | 60.4 | 57.9% | 1.09% | 1.49 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 60.1 | 60.7% | 1.1% | 1.46 |
| 🟢 BULLISH | **XLK** | Donchian — 20D High Breakout | 60.1 | 65.0% | 0.69% | 1.21 |
| 🟢 BULLISH | **GC=F** | ADX Strong Trend — Bullish | 59.7 | 61.1% | 0.75% | 1.32 |
| 🟢 BULLISH | **AERO-USD** | Stochastic (Full) — Oversold | 59.3 | 52.8% | 5.44% | 1.59 |
| 🟢 BULLISH | **PLTR** | Chaikin Money Flow — Bullish | 59.0 | 56.5% | 2.37% | 1.45 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 58.3 | 66.5% | 0.65% | 1.08 |
| 🟢 BULLISH | **RIOT** | VWAP Deviation — Oversold | 58.3 | 54.9% | 3.04% | 1.59 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 58.2 | 58.8% | 1.02% | 1.43 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 58.2 | 56.9% | 2.09% | 1.45 |
| 🟢 BULLISH | **UPRO** | Aroon — Strong Uptrend | 58.1 | 62.4% | 0.86% | 1.27 |
| 🟢 BULLISH | **CRWD** | CCI — Extreme Oversold | 58.1 | 57.8% | 1.52% | 1.46 |
| 🟢 BULLISH | **SOL-USD** | TRIX — Bullish Cross | 55.3 | 57.9% | 1.46% | 1.37 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 55.0 | 60.9% | 0.4% | 1.0 |
| 🟢 BULLISH | **CEG** | Aroon — Strong Uptrend | 54.6 | 57.3% | 1.78% | 1.5 |
| 🟢 BULLISH | **MSFT** | ADX Strong Trend — Bullish | 54.4 | 60.5% | 0.5% | 1.13 |
| 🟢 BULLISH | **PLTR** | Aroon — Strong Uptrend | 54.2 | 57.3% | 1.78% | 1.17 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 53.6 | 59.7% | 0.51% | 1.03 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 53.4 | 58.8% | 2.91% | 1.23 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 53.3 | 59.2% | 0.66% | 1.11 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 52.3 | 57.2% | 1.62% | 1.25 |
| 🟢 BULLISH | **AVGO** | CCI — Extreme Oversold | 52.2 | 54.8% | 1.34% | 1.2 |
| 🟢 BULLISH | **CRWD** | OBV — Accumulation | 52.2 | 60.5% | 0.86% | 1.05 |
| 🟢 BULLISH | **UPRO** | CCI — Extreme Oversold | 51.4 | 59.5% | 0.95% | 0.95 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 51.2 | 51.5% | 3.09% | 1.3 |
| 🟢 BULLISH | **MRVL** | CCI — Extreme Oversold | 51.0 | 57.1% | 1.57% | 1.05 |
| 🟢 BULLISH | **TQQQ** | CCI — Extreme Oversold | 50.3 | 59.2% | 1.27% | 0.98 |
| 🔴 BEARISH | **GOOGL** | Chaikin Money Flow — Bearish | 89.1 | 85.7% | 3.45% | 5.63 |
| 🔴 BEARISH | **ADA-USD** | MFI — Overbought | 79.9 | 68.4% | 5.8% | 3.52 |
| 🔴 BEARISH | **XLK** | VWAP Deviation — Overbought | 78.7 | 67.4% | 1.63% | 2.54 |
| 🔴 BEARISH | **CEG** | PPO — Bearish Cross | 77.3 | 60.0% | 4.31% | 2.89 |
| 🔴 BEARISH | **RKLB** | Stochastic RSI Overbought | 75.2 | 58.5% | 4.72% | 2.52 |
| 🔴 BEARISH | **RKLB** | Stochastic (Full) — Overbought | 75.1 | 60.7% | 4.67% | 2.46 |
| 🔴 BEARISH | **MRVL** | Stochastic (Full) — Overbought | 74.7 | 61.4% | 3.27% | 2.12 |
| 🔴 BEARISH | **RKLB** | VWAP Deviation — Overbought | 73.2 | 57.1% | 4.52% | 2.41 |
| 🔴 BEARISH | **MRVL** | VWAP Deviation — Overbought | 72.0 | 58.9% | 3.04% | 2.02 |
| 🔴 BEARISH | **AAPL** | Aroon — Strong Downtrend | 71.8 | 58.8% | 1.34% | 1.98 |
| 🔴 BEARISH | **RKLB** | Williams %R — Overbought | 70.7 | 59.2% | 4.23% | 2.18 |
| 🔴 BEARISH | **MARA** | PPO — Bearish Cross | 70.6 | 52.9% | 6.28% | 2.58 |
| 🔴 BEARISH | **MSFT** | Fisher Transform — High Extreme | 70.2 | 67.6% | 0.62% | 1.81 |
| 🔴 BEARISH | **IONQ** | Fisher Transform — High Extreme | 70.1 | 59.7% | 5.95% | 2.39 |
| 🔴 BEARISH | **META** | Ulcer Index — Elevated | 69.8 | 62.9% | 1.7% | 2.36 |
| 🔴 BEARISH | **MRVL** | Williams %R — Overbought | 67.9 | 60.3% | 2.55% | 1.81 |
| 🔴 BEARISH | **XBI** | Aroon — Strong Downtrend | 67.7 | 63.7% | 1.19% | 1.84 |
| 🔴 BEARISH | **AMD** | Chaikin Money Flow — Bearish | 66.6 | 64.5% | 2.13% | 2.43 |
| 🔴 BEARISH | **MSFT** | RSI Overbought | 66.3 | 67.0% | 0.71% | 1.55 |
| 🔴 BEARISH | **IONQ** | Stochastic (Full) — Overbought | 65.5 | 57.7% | 4.62% | 1.9 |
| 🔴 BEARISH | **GC=F** | Keltner — Upper Channel Touch | 64.9 | 65.7% | 0.8% | 1.5 |
| 🔴 BEARISH | **SMH** | VWAP Deviation — Overbought | 63.6 | 60.8% | 1.14% | 1.51 |
| 🔴 BEARISH | **SMH** | Vortex — Bearish | 61.9 | 65.6% | 1.12% | 1.53 |
| 🔴 BEARISH | **IONQ** | VWAP Deviation — Overbought | 61.8 | 56.1% | 4.2% | 1.77 |
| 🔴 BEARISH | **NVDA** | Keltner — Upper Channel Touch | 61.2 | 65.6% | 0.82% | 1.32 |
| 🔴 BEARISH | **UPRO** | VWAP Deviation — Overbought | 61.2 | 59.3% | 1.04% | 1.45 |
| 🔴 BEARISH | **SMH** | Stochastic (Full) — Overbought | 61.0 | 60.2% | 1.03% | 1.38 |
| 🔴 BEARISH | **PLTR** | RSI Overbought | 60.0 | 59.3% | 1.7% | 1.43 |
| 🔴 BEARISH | **MSFT** | Keltner — Upper Channel Touch | 59.9 | 69.1% | 0.64% | 1.27 |
| 🔴 BEARISH | **AAPL** | Ulcer Index — Elevated | 59.8 | 60.2% | 1.07% | 1.46 |
| 🔴 BEARISH | **ADA-USD** | Fisher Transform — High Extreme | 59.0 | 48.9% | 4.27% | 1.96 |
| 🔴 BEARISH | **SOXL** | VWAP Deviation — Overbought | 58.0 | 57.6% | 3.42% | 1.46 |
| 🔴 BEARISH | **IONQ** | Stochastic RSI Overbought | 57.2 | 52.2% | 3.73% | 1.55 |
| 🔴 BEARISH | **XLK** | Stochastic (Full) — Overbought | 57.1 | 60.8% | 0.68% | 1.13 |
| 🔴 BEARISH | **CRWD** | Williams %R — Overbought | 56.6 | 58.7% | 1.52% | 1.38 |
| 🔴 BEARISH | **PLTR** | Williams %R — Overbought | 56.3 | 58.3% | 1.8% | 1.29 |
| 🔴 BEARISH | **GC=F** | Stochastic (Full) — Overbought | 56.1 | 62.0% | 0.58% | 1.09 |
| 🔴 BEARISH | **XLK** | Williams %R — Overbought | 55.7 | 60.0% | 0.66% | 1.12 |
| 🔴 BEARISH | **CRWD** | Stochastic RSI Overbought | 55.7 | 55.4% | 1.46% | 1.39 |
| 🔴 BEARISH | **CRWD** | VWAP Deviation — Overbought | 55.4 | 57.5% | 1.34% | 1.26 |
| 🔴 BEARISH | **PLTR** | Stochastic (Full) — Overbought | 54.8 | 58.7% | 1.76% | 1.19 |
| 🔴 BEARISH | **META** | Aroon — Strong Downtrend | 54.6 | 57.2% | 1.19% | 1.26 |
| 🔴 BEARISH | **TSLA** | ADX Strong Trend — Bearish | 54.1 | 49.3% | 2.08% | 1.46 |
| 🔴 BEARISH | **SMH** | Williams %R — Overbought | 54.0 | 56.8% | 0.85% | 1.08 |
| 🔴 BEARISH | **GC=F** | Williams %R — Overbought | 53.2 | 59.3% | 0.53% | 1.0 |
| 🔴 BEARISH | **RIOT** | Vortex — Bearish | 52.8 | 47.8% | 3.4% | 1.42 |
| 🔴 BEARISH | **SMH** | Stochastic RSI Overbought | 52.5 | 60.0% | 0.8% | 0.93 |
| 🔴 BEARISH | **XLE** | TRIX — Bearish Cross | 51.7 | 68.8% | 0.5% | 1.04 |
| 🔴 BEARISH | **AMZN** | Williams %R — Overbought | 51.6 | 58.3% | 0.76% | 1.12 |
| 🔴 BEARISH | **PLTR** | VWAP Deviation — Overbought | 51.2 | 58.4% | 1.39% | 1.0 |
| 🔴 BEARISH | **NVDA** | Stochastic (Full) — Overbought | 50.4 | 57.1% | 0.73% | 0.86 |
| 🔴 BEARISH | **MRVL** | Stochastic RSI Overbought | 50.3 | 54.6% | 1.32% | 0.98 |

---
*Not financial advice. Backtests use historical data.*