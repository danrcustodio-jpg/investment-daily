# Strategy Alerts
**Last scan:** Thursday July 02, 2026 at 04:00 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 102 |
| 🟢 Bullish | 68 |
| 🔴 Bearish | 48 |
| ✅ Fired this run (SMS + email) | 4 |
| ⏭ Skipped — same ticker notified in last 6h | 98 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 8 |

## 📲 SMS sent (3)

- One text per ticker: **TSLA, MARA, DOGE-USD**

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **XLE** | Stochastic (Full) — Oversold | 65.8 | 1 | Aroon — Strong Downtrend | 88.0 | 1 |
| **AVGO** | Fisher Transform — Low Extreme | 87.5 | 4 | Aroon — Strong Downtrend | 76.6 | 1 |
| **SMH** | Williams %R — Oversold | 79.4 | 1 | SMA 30 — Bearish Loss | 85.9 | 1 |
| **NVDA** | Williams %R — Oversold | 85.6 | 2 | Aroon — Strong Downtrend | 69.1 | 2 |
| **AAPL** | SMA 30 — Bullish Reclaim | 77.9 | 1 | Chaikin Money Flow — Bearish | 84.5 | 2 |
| **RIOT** | Williams %R — Oversold | 67.7 | 1 | Supertrend — Bearish Flip | 78.3 | 1 |
| **MRVL** | ADX Strong Trend — Bullish | 75.8 | 1 | SMA 30 — Bearish Loss | 77.8 | 2 |
| **RKLB** | CCI — Extreme Oversold | 68.3 | 1 | Aroon — Strong Downtrend | 70.7 | 1 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **DOGE-USD** | RSI Oversold | 63.7 | 62.3% | 2.25% | 1.99 |
| 🔴 BEARISH | **TSLA** | EMA 9/21 — Bearish Cross | 80.9 | 75.0% | 2.78% | 5.05 |
| 🔴 BEARISH | **TSLA** | SMA 30 — Bearish Loss | 73.6 | 70.8% | 1.86% | 2.27 |
| 🔴 BEARISH | **MARA** | EMA 9/21 — Bearish Cross | 67.6 | 44.4% | 6.38% | 2.01 |

## ⏭ Skipped — same ticker already notified

Above-threshold signals dropped because another strategy on the same ticker fired within the last 6h ticker-cooldown window.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **AVGO** | Fisher Transform — Low Extreme | 87.5 | 84.0% | 5.75% | 5.18 |
| 🟢 BULLISH | **NVDA** | Williams %R — Oversold | 85.6 | 79.0% | 4.24% | 4.86 |
| 🟢 BULLISH | **GOOGL** | MACD Bullish Crossover | 85.2 | 78.9% | 2.74% | 3.86 |
| 🟢 BULLISH | **PLTR** | MACD Bullish Crossover | 84.5 | 77.8% | 3.8% | 4.54 |
| 🟢 BULLISH | **NVDA** | VWAP Deviation — Oversold | 84.4 | 74.7% | 4.19% | 4.24 |
| 🟢 BULLISH | **XBI** | ADX Strong Trend — Bullish | 82.3 | 67.9% | 1.24% | 2.57 |
| 🟢 BULLISH | **SMH** | Williams %R — Oversold | 79.4 | 71.1% | 2.43% | 2.74 |
| 🟢 BULLISH | **AVGO** | VWAP Deviation — Oversold | 79.0 | 64.8% | 3.34% | 3.13 |
| 🟢 BULLISH | **ATOM-USD** | Keltner — Lower Channel Touch | 78.9 | 71.4% | 4.52% | 3.67 |
| 🟢 BULLISH | **AAPL** | SMA 30 — Bullish Reclaim | 77.9 | 68.4% | 1.53% | 2.57 |
| 🟢 BULLISH | **XBI** | 52-Week Breakout | 77.3 | 63.9% | 1.37% | 2.41 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 75.8 | 59.7% | 3.48% | 2.21 |
| 🟢 BULLISH | **CRWD** | 52-Week Breakout | 72.2 | 68.8% | 3.52% | 2.54 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 72.0 | 62.3% | 3.5% | 2.43 |
| 🟢 BULLISH | **AVGO** | Stochastic (Full) — Oversold | 71.5 | 60.9% | 2.22% | 2.07 |
| 🟢 BULLISH | **AVGO** | Williams %R — Oversold | 69.5 | 59.8% | 1.92% | 1.92 |
| 🟢 BULLISH | **PLTR** | OBV — Accumulation | 68.8 | 57.6% | 2.23% | 1.84 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 68.3 | 54.4% | 4.0% | 2.03 |
| 🟢 BULLISH | **RIOT** | Williams %R — Oversold | 67.7 | 60.8% | 4.05% | 2.03 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 67.3 | 60.0% | 3.33% | 2.06 |
| 🟢 BULLISH | **SOXL** | VWAP Deviation — Oversold | 66.0 | 66.7% | 4.52% | 1.84 |
| 🟢 BULLISH | **XLE** | Stochastic (Full) — Oversold | 65.8 | 65.7% | 0.69% | 1.44 |
| 🟢 BULLISH | **GOOGL** | Chaikin Money Flow — Bullish | 65.4 | 59.0% | 1.31% | 1.77 |
| 🟢 BULLISH | **SOXL** | Williams %R — Oversold | 64.7 | 66.2% | 4.52% | 1.81 |
| 🟢 BULLISH | **GC=F** | Elder Force — Bullish | 64.1 | 53.3% | 0.59% | 1.67 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 62.8 | 61.3% | 1.19% | 1.58 |
| 🟢 BULLISH | **ATOM-USD** | Fisher Transform — Low Extreme | 62.7 | 60.8% | 2.27% | 1.82 |
| 🟢 BULLISH | **GOOGL** | Vortex — Bullish | 62.6 | 60.0% | 1.09% | 1.59 |
| 🟢 BULLISH | **XBI** | Aroon — Strong Uptrend | 61.3 | 59.7% | 0.76% | 1.46 |
| 🟢 BULLISH | **CL=F** | Stochastic RSI Oversold | 60.5 | 59.7% | 1.32% | 1.68 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 60.3 | 67.3% | 0.64% | 1.1 |
| 🟢 BULLISH | **AMZN** | Vortex — Bullish | 60.1 | 65.2% | 1.16% | 1.43 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 59.2 | 57.3% | 2.04% | 1.48 |
| 🟢 BULLISH | **CRWD** | CCI — Extreme Oversold | 58.4 | 57.7% | 1.49% | 1.47 |
| 🟢 BULLISH | **MRVL** | CCI — Extreme Oversold | 58.3 | 59.2% | 1.95% | 1.39 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 58.1 | 59.5% | 2.64% | 1.34 |
| 🟢 BULLISH | **AAPL** | MACD Bullish Crossover | 57.8 | 52.9% | 0.83% | 1.5 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 56.9 | 59.4% | 3.27% | 1.4 |
| 🟢 BULLISH | **CRWD** | Chaikin Money Flow — Bullish | 56.4 | 57.4% | 1.41% | 1.33 |
| 🟢 BULLISH | **ARM** | Stochastic RSI Oversold | 56.3 | 56.6% | 2.58% | 1.51 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 55.5 | 57.8% | 1.78% | 1.4 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 55.4 | 60.0% | 0.54% | 1.09 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 55.2 | 58.4% | 0.89% | 1.26 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 54.5 | 61.5% | 0.39% | 0.94 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 54.4 | 59.4% | 0.68% | 1.14 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 54.1 | 52.9% | 3.22% | 1.38 |
| 🟢 BULLISH | **CEG** | Williams %R — Oversold | 52.3 | 59.6% | 1.19% | 0.98 |
| 🟢 BULLISH | **CEG** | Keltner — Lower Channel Touch | 52.2 | 60.8% | 1.5% | 1.06 |
| 🟢 BULLISH | **CEG** | VWAP Deviation — Oversold | 52.1 | 58.3% | 1.28% | 1.04 |
| 🟢 BULLISH | **TQQQ** | CCI — Extreme Oversold | 51.8 | 59.4% | 1.35% | 1.03 |
| 🟢 BULLISH | **MRVL** | Williams %R — Oversold | 51.8 | 64.4% | 1.6% | 1.12 |
| 🟢 BULLISH | **CRWD** | Aroon — Strong Uptrend | 51.4 | 55.8% | 1.13% | 1.09 |
| 🟢 BULLISH | **UPRO** | CCI — Extreme Oversold | 51.0 | 59.8% | 0.92% | 0.9 |
| 🟢 BULLISH | **ARKK** | Aroon — Strong Uptrend | 50.4 | 56.8% | 0.92% | 1.03 |
| 🟢 BULLISH | **AVGO** | CCI — Extreme Oversold | 50.3 | 53.8% | 1.26% | 1.1 |
| 🟢 BULLISH | **ARKK** | CCI — Extreme Oversold | 50.0 | 57.9% | 0.82% | 0.92 |
| 🟢 BULLISH | **XBI** | CCI — Extreme Oversold | 50.0 | 57.1% | 0.58% | 0.93 |
| 🔴 BEARISH | **UPRO** | Chaikin Money Flow — Bearish | 89.9 | 76.3% | 6.74% | 5.37 |
| 🔴 BEARISH | **XLE** | Aroon — Strong Downtrend | 88.0 | 79.2% | 1.62% | 4.4 |
| 🔴 BEARISH | **QQQ** | Chaikin Money Flow — Bearish | 87.0 | 85.0% | 2.81% | 5.28 |
| 🔴 BEARISH | **SMH** | SMA 30 — Bearish Loss | 85.9 | 76.5% | 2.44% | 3.72 |
| 🔴 BEARISH | **AAPL** | Chaikin Money Flow — Bearish | 84.5 | 73.7% | 3.6% | 4.87 |
| 🔴 BEARISH | **GC=F** | MFI — Overbought | 84.4 | 70.3% | 1.27% | 2.87 |
| 🔴 BEARISH | **TQQQ** | Chaikin Money Flow — Bearish | 82.6 | 74.4% | 7.52% | 4.67 |
| 🔴 BEARISH | **META** | Chaikin Money Flow — Bearish | 82.3 | 64.8% | 2.59% | 3.53 |
| 🔴 BEARISH | **QQQ** | SMA 30 — Bearish Loss | 81.7 | 70.8% | 1.19% | 3.35 |
| 🔴 BEARISH | **UPRO** | SMA 30 — Bearish Loss | 81.3 | 66.7% | 3.04% | 3.42 |
| 🔴 BEARISH | **XLK** | Awesome Oscillator — Bearish Zero Line | 78.6 | 66.7% | 1.4% | 2.95 |
| 🔴 BEARISH | **RIOT** | Supertrend — Bearish Flip | 78.3 | 66.7% | 9.46% | 2.17 |
| 🔴 BEARISH | **SPY** | PPO — Bearish Cross | 77.8 | 66.7% | 0.9% | 2.14 |
| 🔴 BEARISH | **MRVL** | SMA 30 — Bearish Loss | 77.8 | 66.7% | 3.63% | 3.09 |
| 🔴 BEARISH | **AVGO** | Aroon — Strong Downtrend | 76.6 | 63.6% | 3.74% | 3.21 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 71.1 | 65.4% | 1.05% | 1.88 |
| 🔴 BEARISH | **RKLB** | Aroon — Strong Downtrend | 70.7 | 61.7% | 4.0% | 2.09 |
| 🔴 BEARISH | **APP** | VWAP Deviation — Overbought | 70.3 | 65.4% | 3.66% | 1.92 |
| 🔴 BEARISH | **NVDA** | Aroon — Strong Downtrend | 69.1 | 60.8% | 2.13% | 2.13 |
| 🔴 BEARISH | **NVDA** | PPO — Bearish Cross | 69.0 | 68.8% | 2.27% | 1.88 |
| 🔴 BEARISH | **AAPL** | Aroon — Strong Downtrend | 68.4 | 58.4% | 1.17% | 1.8 |
| 🔴 BEARISH | **MRVL** | Vortex — Bearish | 67.7 | 50.0% | 3.34% | 2.14 |
| 🔴 BEARISH | **SMH** | Parabolic SAR — Bearish | 63.4 | 68.0% | 1.14% | 1.38 |
| 🔴 BEARISH | **ARM** | Elder Force — Bearish | 63.2 | 56.0% | 2.26% | 1.84 |
| 🔴 BEARISH | **AVGO** | Chaikin Money Flow — Bearish | 62.5 | 60.0% | 1.97% | 1.64 |
| 🔴 BEARISH | **APP** | Williams %R — Overbought | 61.8 | 62.9% | 2.42% | 1.58 |
| 🔴 BEARISH | **APP** | Stochastic RSI Overbought | 60.8 | 62.0% | 2.33% | 1.56 |
| 🔴 BEARISH | **APP** | Aroon — Strong Downtrend | 60.6 | 64.2% | 2.71% | 1.47 |
| 🔴 BEARISH | **META** | SMA 30 — Bearish Loss | 60.2 | 60.0% | 1.03% | 1.52 |
| 🔴 BEARISH | **XLK** | SMA 30 — Bearish Loss | 59.9 | 63.6% | 0.65% | 1.34 |
| 🔴 BEARISH | **RIOT** | Aroon — Strong Downtrend | 58.4 | 57.8% | 2.73% | 1.61 |
| 🔴 BEARISH | **CRWD** | Williams %R — Overbought | 57.6 | 58.9% | 1.5% | 1.4 |
| 🔴 BEARISH | **PLTR** | Aroon — Strong Downtrend | 56.2 | 54.1% | 1.88% | 1.4 |
| 🔴 BEARISH | **CRWD** | Stochastic RSI Overbought | 55.9 | 55.6% | 1.37% | 1.31 |
| 🔴 BEARISH | **CRWD** | Stochastic (Full) — Overbought | 55.8 | 57.8% | 1.38% | 1.3 |
| 🔴 BEARISH | **CRWD** | VWAP Deviation — Overbought | 55.3 | 56.9% | 1.28% | 1.23 |
| 🔴 BEARISH | **SMCI** | Aroon — Strong Downtrend | 53.9 | 53.7% | 2.84% | 1.26 |
| 🔴 BEARISH | **XBI** | MFI — Overbought | 53.8 | 80.0% | 0.33% | 0.39 |
| 🔴 BEARISH | **XBI** | RSI Overbought | 52.7 | 57.5% | 0.46% | 0.79 |
| 🔴 BEARISH | **RIOT** | Vortex — Bearish | 51.8 | 47.6% | 3.53% | 1.39 |
| 🔴 BEARISH | **AMZN** | Williams %R — Overbought | 51.1 | 57.1% | 0.77% | 1.13 |

---
*Not financial advice. Backtests use historical data.*