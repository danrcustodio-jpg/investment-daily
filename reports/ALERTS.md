# Strategy Alerts
**Last scan:** Monday June 22, 2026 at 02:53 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 95 |
| 🟢 Bullish | 73 |
| 🔴 Bearish | 44 |
| ✅ Fired this run (SMS + email) | 95 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 9 |

## 📲 SMS sent (3)

- One text per ticker: **PLTR, XLE, AAPL**
- Skipped — over per-scan cap: **GC=F, UPRO, MSFT, SOXL, MRVL, AVGO, MARA, TQQQ, RKLB, CL=F, SMH, GOOGL, AMD, COIN, RIOT, XLK, QQQ, CEG, IONQ, SPY, ARM, AMZN, APP, CRWD, NVDA, XBI, META** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **69.8** (2 BEAR signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **PLTR** | MFI — Oversold | 100.0 | 2 | Aroon — Strong Downtrend | 69.8 | 2 |
| **XLE** | VWAP Deviation — Oversold | 77.4 | 3 | Aroon — Strong Downtrend | 90.8 | 2 |
| **GC=F** | Chaikin Money Flow — Bullish | 66.6 | 1 | ADX Strong Trend — Bearish | 84.9 | 1 |
| **MSFT** | MFI — Oversold | 83.3 | 1 | Donchian — 20D Low Breakdown | 75.5 | 1 |
| **MRVL** | ADX Strong Trend — Bullish | 80.3 | 2 | Ulcer Index — Elevated | 82.1 | 2 |
| **SOXL** | Aroon — Strong Uptrend | 70.0 | 2 | Ulcer Index — Elevated | 82.1 | 1 |
| **AVGO** | VWAP Deviation — Oversold | 80.3 | 2 | Ulcer Index — Elevated | 81.2 | 1 |
| **RKLB** | CCI — Extreme Oversold | 68.9 | 1 | Aroon — Strong Downtrend | 78.2 | 1 |
| **AMD** | Aroon — Strong Uptrend | 72.1 | 3 | VWAP Deviation — Overbought | 76.9 | 2 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **PLTR** | MFI — Oversold | 100.0 | 100.0% | 7.17% | 29.41 |
| 🟢 BULLISH | **MSFT** | MFI — Oversold | 83.3 | 83.3% | 1.73% | 5.56 |
| 🟢 BULLISH | **AVGO** | VWAP Deviation — Oversold | 80.3 | 67.1% | 3.61% | 3.37 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 80.3 | 62.6% | 4.0% | 2.57 |
| 🟢 BULLISH | **MARA** | MACD Bullish Crossover | 79.7 | 66.7% | 4.98% | 3.6 |
| 🟢 BULLISH | **MRVL** | Aroon — Strong Uptrend | 79.2 | 64.2% | 3.54% | 2.41 |
| 🟢 BULLISH | **CL=F** | Stochastic RSI Oversold | 77.9 | 66.7% | 2.01% | 2.75 |
| 🟢 BULLISH | **XLE** | VWAP Deviation — Oversold | 77.4 | 75.8% | 0.95% | 1.84 |
| 🟢 BULLISH | **SMH** | Aroon — Strong Uptrend | 76.9 | 66.1% | 1.64% | 2.39 |
| 🟢 BULLISH | **COIN** | PPO — Bullish Cross | 76.7 | 66.7% | 3.17% | 2.92 |
| 🟢 BULLISH | **RIOT** | Aroon — Strong Uptrend | 76.5 | 63.0% | 4.43% | 2.45 |
| 🟢 BULLISH | **XLE** | Fisher Transform — Low Extreme | 76.2 | 76.3% | 0.9% | 1.77 |
| 🟢 BULLISH | **CEG** | TRIX — Bullish Cross | 74.5 | 63.6% | 3.26% | 2.47 |
| 🟢 BULLISH | **CL=F** | Keltner — Lower Channel Touch | 74.2 | 61.3% | 1.61% | 2.49 |
| 🟢 BULLISH | **XLE** | Stochastic (Full) — Oversold | 73.9 | 70.3% | 0.85% | 1.79 |
| 🟢 BULLISH | **PLTR** | VWAP Deviation — Oversold | 72.9 | 57.0% | 2.73% | 2.24 |
| 🟢 BULLISH | **CL=F** | Fisher Transform — Low Extreme | 72.7 | 64.5% | 1.24% | 2.37 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 72.1 | 62.8% | 3.59% | 2.46 |
| 🟢 BULLISH | **AVGO** | Williams %R — Oversold | 71.9 | 60.8% | 2.05% | 2.03 |
| 🟢 BULLISH | **SOXL** | Aroon — Strong Uptrend | 70.0 | 61.1% | 4.42% | 2.08 |
| 🟢 BULLISH | **AMD** | ADX Strong Trend — Bullish | 70.0 | 61.9% | 3.26% | 2.23 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 68.9 | 54.2% | 4.01% | 2.06 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 67.2 | 60.7% | 3.47% | 2.1 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 66.6 | 68.8% | 0.78% | 1.41 |
| 🟢 BULLISH | **SOXL** | 52-Week Breakout | 65.3 | 62.5% | 4.43% | 1.7 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 61.2 | 60.9% | 1.14% | 1.5 |
| 🟢 BULLISH | **ARM** | Aroon — Strong Uptrend | 60.9 | 54.4% | 2.4% | 1.55 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 59.9 | 57.4% | 2.05% | 1.5 |
| 🟢 BULLISH | **SMH** | 52-Week Breakout | 59.4 | 61.2% | 0.9% | 1.22 |
| 🟢 BULLISH | **MARA** | OBV — Accumulation | 59.4 | 54.5% | 2.73% | 1.59 |
| 🟢 BULLISH | **MRVL** | CCI — Extreme Oversold | 58.4 | 59.2% | 1.95% | 1.39 |
| 🟢 BULLISH | **PLTR** | Williams %R — Oversold | 57.4 | 51.5% | 1.62% | 1.41 |
| 🟢 BULLISH | **AMZN** | Williams %R — Oversold | 57.2 | 61.2% | 0.89% | 1.32 |
| 🟢 BULLISH | **CL=F** | VWAP Deviation — Oversold | 56.5 | 63.5% | 0.93% | 1.11 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 56.5 | 58.6% | 2.47% | 1.25 |
| 🟢 BULLISH | **GOOGL** | Keltner — Lower Channel Touch | 55.9 | 57.8% | 1.07% | 1.49 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 55.8 | 59.2% | 3.16% | 1.35 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 55.1 | 60.3% | 0.52% | 1.05 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 55.0 | 58.0% | 0.88% | 1.25 |
| 🟢 BULLISH | **CRWD** | Chaikin Money Flow — Bullish | 54.7 | 57.8% | 1.3% | 1.23 |
| 🟢 BULLISH | **AMZN** | VWAP Deviation — Oversold | 54.5 | 60.3% | 0.96% | 1.28 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 54.5 | 53.2% | 3.25% | 1.39 |
| 🟢 BULLISH | **IONQ** | Stochastic RSI Oversold | 54.3 | 51.9% | 3.85% | 1.38 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 54.1 | 61.6% | 0.38% | 0.9 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 53.9 | 57.2% | 1.7% | 1.32 |
| 🟢 BULLISH | **CRWD** | CCI — Extreme Oversold | 53.8 | 56.9% | 1.23% | 1.21 |
| 🟢 BULLISH | **ARM** | Chaikin Money Flow — Bullish | 53.8 | 50.4% | 2.45% | 1.3 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 53.5 | 59.5% | 0.65% | 1.07 |
| 🟢 BULLISH | **RKLB** | VWAP Deviation — Oversold | 53.0 | 51.8% | 2.42% | 1.29 |
| 🟢 BULLISH | **RKLB** | Stochastic RSI Oversold | 52.4 | 44.1% | 3.18% | 1.37 |
| 🟢 BULLISH | **XBI** | Aroon — Strong Uptrend | 51.9 | 57.8% | 0.5% | 0.92 |
| 🟢 BULLISH | **TQQQ** | CCI — Extreme Oversold | 51.7 | 59.7% | 1.31% | 1.0 |
| 🟢 BULLISH | **RIOT** | 52-Week Breakout | 51.4 | 66.7% | 0.92% | 0.81 |
| 🟢 BULLISH | **CRWD** | OBV — Accumulation | 51.2 | 61.5% | 0.76% | 0.99 |
| 🟢 BULLISH | **XLE** | Keltner — Lower Channel Touch | 51.1 | 67.6% | 0.32% | 0.41 |
| 🟢 BULLISH | **AVGO** | CCI — Extreme Oversold | 50.8 | 54.0% | 1.27% | 1.11 |
| 🟢 BULLISH | **UPRO** | CCI — Extreme Oversold | 50.8 | 59.9% | 0.89% | 0.86 |
| 🟢 BULLISH | **XLE** | Williams %R — Oversold | 50.1 | 61.6% | 0.35% | 0.54 |
| 🔴 BEARISH | **XLE** | Aroon — Strong Downtrend | 90.8 | 85.7% | 1.89% | 5.44 |
| 🔴 BEARISH | **AAPL** | Chaikin Money Flow — Bearish | 86.5 | 78.8% | 4.18% | 6.14 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 84.9 | 74.5% | 1.85% | 4.27 |
| 🔴 BEARISH | **UPRO** | SMA 30 — Bearish Loss | 84.7 | 75.0% | 3.69% | 4.13 |
| 🔴 BEARISH | **SOXL** | Ulcer Index — Elevated | 82.1 | 77.0% | 8.77% | 4.52 |
| 🔴 BEARISH | **MRVL** | Ulcer Index — Elevated | 82.1 | 75.3% | 3.92% | 4.44 |
| 🔴 BEARISH | **AVGO** | Ulcer Index — Elevated | 81.2 | 73.7% | 3.9% | 4.58 |
| 🔴 BEARISH | **XLE** | Chaikin Money Flow — Bearish | 80.1 | 72.0% | 1.22% | 2.34 |
| 🔴 BEARISH | **TQQQ** | Ulcer Index — Elevated | 79.2 | 72.3% | 3.28% | 2.89 |
| 🔴 BEARISH | **RKLB** | Aroon — Strong Downtrend | 78.2 | 64.5% | 4.85% | 2.72 |
| 🔴 BEARISH | **GOOGL** | Elder Force — Bearish | 76.9 | 65.5% | 2.09% | 2.72 |
| 🔴 BEARISH | **AMD** | VWAP Deviation — Overbought | 76.9 | 64.4% | 3.72% | 2.69 |
| 🔴 BEARISH | **AMD** | Williams %R — Overbought | 76.7 | 62.7% | 3.89% | 2.64 |
| 🔴 BEARISH | **XLK** | Ulcer Index — Elevated | 76.5 | 67.3% | 1.35% | 2.77 |
| 🔴 BEARISH | **AAPL** | Aroon — Strong Downtrend | 76.3 | 61.9% | 1.42% | 2.33 |
| 🔴 BEARISH | **QQQ** | Ulcer Index — Elevated | 76.0 | 69.0% | 1.0% | 2.42 |
| 🔴 BEARISH | **MSFT** | Donchian — 20D Low Breakdown | 75.5 | 75.0% | 1.42% | 2.15 |
| 🔴 BEARISH | **MRVL** | VWAP Deviation — Overbought | 74.8 | 60.4% | 3.09% | 2.1 |
| 🔴 BEARISH | **PLTR** | Aroon — Strong Downtrend | 69.8 | 57.5% | 2.82% | 2.19 |
| 🔴 BEARISH | **IONQ** | Ulcer Index — Elevated | 68.2 | 52.7% | 5.21% | 2.1 |
| 🔴 BEARISH | **PLTR** | Ulcer Index — Elevated | 65.7 | 53.7% | 2.51% | 1.79 |
| 🔴 BEARISH | **UPRO** | Ulcer Index — Elevated | 64.8 | 63.7% | 1.7% | 1.64 |
| 🔴 BEARISH | **SPY** | Ulcer Index — Elevated | 63.2 | 65.2% | 0.53% | 1.42 |
| 🔴 BEARISH | **SMH** | Keltner — Upper Channel Touch | 62.4 | 60.3% | 0.98% | 1.42 |
| 🔴 BEARISH | **SMH** | VWAP Deviation — Overbought | 59.0 | 58.8% | 0.97% | 1.27 |
| 🔴 BEARISH | **AAPL** | Ulcer Index — Elevated | 58.2 | 60.4% | 0.95% | 1.41 |
| 🔴 BEARISH | **MRVL** | PPO — Bearish Cross | 57.8 | 66.7% | 1.36% | 1.03 |
| 🔴 BEARISH | **APP** | Aroon — Strong Downtrend | 57.2 | 63.1% | 2.31% | 1.26 |
| 🔴 BEARISH | **CEG** | Stochastic RSI Overbought | 57.2 | 58.5% | 1.93% | 1.46 |
| 🔴 BEARISH | **SOXL** | Williams %R — Overbought | 56.8 | 56.7% | 3.26% | 1.36 |
| 🔴 BEARISH | **SMH** | Williams %R — Overbought | 55.9 | 56.7% | 0.92% | 1.2 |
| 🔴 BEARISH | **SOXL** | VWAP Deviation — Overbought | 55.8 | 56.0% | 3.16% | 1.35 |
| 🔴 BEARISH | **NVDA** | Chaikin Money Flow — Bearish | 53.8 | 56.7% | 1.08% | 1.24 |
| 🔴 BEARISH | **ARM** | VWAP Deviation — Overbought | 53.4 | 53.2% | 1.85% | 1.14 |
| 🔴 BEARISH | **CEG** | Aroon — Strong Downtrend | 52.8 | 61.0% | 1.24% | 1.01 |
| 🔴 BEARISH | **META** | Aroon — Strong Downtrend | 51.8 | 57.1% | 1.02% | 1.09 |
| 🔴 BEARISH | **AMZN** | Elder Force — Bearish | 51.3 | 64.1% | 0.83% | 0.86 |

---
*Not financial advice. Backtests use historical data.*