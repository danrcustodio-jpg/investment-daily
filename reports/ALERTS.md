# Strategy Alerts
**Last scan:** Wednesday July 08, 2026 at 03:10 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 93 |
| 🟢 Bullish | 74 |
| 🔴 Bearish | 40 |
| ✅ Fired this run (SMS + email) | 93 |
| ⏭ Skipped — same ticker notified in last 6h | 0 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 8 |

## 📲 SMS sent (3)

- One text per ticker: **UPRO, IWM, XLE**
- Skipped — over per-scan cap: **PLTR, SPY, MRVL, SMH, META, QQQ, XLK, GC=F, TSLA, AVGO, XBI, GOOGL, AMD, TQQQ, SOXL, RKLB, RIOT, NVDA, DOGE-USD, ARM, APP, CRWD, IONQ, ARKK, SMCI** (visible on dashboard)
- ⚠ **Headline ticker was contested** — opposing-side top score **65.1** (1 BULL signals).

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **XLE** | Vortex — Bullish | 65.1 | 1 | Aroon — Strong Downtrend | 88.2 | 1 |
| **PLTR** | PPO — Bullish Cross | 87.5 | 2 | Vortex — Bearish | 81.8 | 1 |
| **SMH** | VWAP Deviation — Oversold | 83.1 | 4 | Ulcer Index — Elevated | 81.7 | 2 |
| **QQQ** | Stochastic RSI Oversold | 72.1 | 2 | Awesome Oscillator — Bearish Zero Line | 81.3 | 1 |
| **GC=F** | PPO — Bullish Cross | 79.5 | 2 | ADX Strong Trend — Bearish | 73.2 | 1 |
| **XBI** | ADX Strong Trend — Bullish | 65.3 | 1 | MFI — Overbought | 75.2 | 1 |
| **GOOGL** | Chaikin Money Flow — Bullish | 65.4 | 1 | SMA 30 — Bearish Loss | 71.4 | 1 |
| **RKLB** | CCI — Extreme Oversold | 68.1 | 1 | Chaikin Money Flow — Bearish | 66.8 | 1 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **PLTR** | PPO — Bullish Cross | 87.5 | 81.2% | 5.43% | 4.05 |
| 🟢 BULLISH | **SMH** | VWAP Deviation — Oversold | 83.1 | 78.9% | 3.71% | 4.0 |
| 🟢 BULLISH | **XLK** | Stochastic RSI Oversold | 80.8 | 68.9% | 1.85% | 3.15 |
| 🟢 BULLISH | **XLK** | Williams %R — Oversold | 80.4 | 71.7% | 1.9% | 2.82 |
| 🟢 BULLISH | **GC=F** | PPO — Bullish Cross | 79.5 | 72.2% | 1.4% | 4.45 |
| 🟢 BULLISH | **SMH** | Williams %R — Oversold | 78.7 | 70.5% | 2.43% | 2.7 |
| 🟢 BULLISH | **XLK** | Stochastic (Full) — Oversold | 77.9 | 69.2% | 2.11% | 2.99 |
| 🟢 BULLISH | **PLTR** | TRIX — Bullish Cross | 76.8 | 66.7% | 3.16% | 2.18 |
| 🟢 BULLISH | **SMH** | Stochastic (Full) — Oversold | 75.6 | 69.2% | 2.4% | 2.69 |
| 🟢 BULLISH | **SMH** | Stochastic RSI Oversold | 74.1 | 66.7% | 1.97% | 2.46 |
| 🟢 BULLISH | **QQQ** | Stochastic RSI Oversold | 72.1 | 62.7% | 1.17% | 2.16 |
| 🟢 BULLISH | **AMD** | Aroon — Strong Uptrend | 71.2 | 61.9% | 3.4% | 2.35 |
| 🟢 BULLISH | **TQQQ** | Williams %R — Oversold | 70.8 | 66.7% | 3.3% | 2.04 |
| 🟢 BULLISH | **SOXL** | Stochastic RSI Oversold | 70.6 | 66.0% | 5.58% | 2.26 |
| 🟢 BULLISH | **TQQQ** | Stochastic RSI Oversold | 70.3 | 63.8% | 3.21% | 2.16 |
| 🟢 BULLISH | **SOXL** | VWAP Deviation — Oversold | 70.1 | 67.6% | 5.05% | 2.12 |
| 🟢 BULLISH | **QQQ** | Williams %R — Oversold | 69.2 | 65.6% | 1.06% | 1.82 |
| 🟢 BULLISH | **TQQQ** | VWAP Deviation — Oversold | 68.7 | 66.0% | 3.42% | 1.96 |
| 🟢 BULLISH | **SOXL** | Williams %R — Oversold | 68.7 | 66.7% | 4.98% | 2.01 |
| 🟢 BULLISH | **AMD** | Williams %R — Oversold | 68.7 | 60.2% | 2.08% | 2.35 |
| 🟢 BULLISH | **GC=F** | TRIX — Bullish Cross | 68.4 | 66.7% | 0.86% | 1.98 |
| 🟢 BULLISH | **RKLB** | CCI — Extreme Oversold | 68.1 | 54.6% | 4.01% | 2.03 |
| 🟢 BULLISH | **RIOT** | Williams %R — Oversold | 67.7 | 60.8% | 4.05% | 2.03 |
| 🟢 BULLISH | **AMD** | Stochastic RSI Oversold | 66.6 | 59.3% | 2.42% | 2.24 |
| 🟢 BULLISH | **AMD** | Chaikin Money Flow — Bullish | 65.8 | 59.3% | 3.15% | 1.95 |
| 🟢 BULLISH | **GOOGL** | Chaikin Money Flow — Bullish | 65.4 | 59.0% | 1.31% | 1.77 |
| 🟢 BULLISH | **XBI** | ADX Strong Trend — Bullish | 65.3 | 62.2% | 0.81% | 1.52 |
| 🟢 BULLISH | **XLE** | Vortex — Bullish | 65.1 | 63.2% | 0.72% | 1.73 |
| 🟢 BULLISH | **RIOT** | Fisher Transform — Low Extreme | 63.2 | 59.5% | 3.56% | 2.24 |
| 🟢 BULLISH | **XBI** | Aroon — Strong Uptrend | 62.9 | 60.3% | 0.8% | 1.53 |
| 🟢 BULLISH | **SMH** | CCI — Extreme Oversold | 62.8 | 61.3% | 1.19% | 1.59 |
| 🟢 BULLISH | **DOGE-USD** | RSI Oversold | 62.2 | 60.8% | 2.23% | 2.1 |
| 🟢 BULLISH | **ARM** | Stochastic RSI Oversold | 60.6 | 55.9% | 2.86% | 1.75 |
| 🟢 BULLISH | **PLTR** | CCI — Extreme Oversold | 59.8 | 57.5% | 2.11% | 1.52 |
| 🟢 BULLISH | **SOXL** | Stochastic (Full) — Oversold | 59.8 | 63.9% | 4.45% | 1.57 |
| 🟢 BULLISH | **RIOT** | Stochastic RSI Oversold | 59.8 | 54.4% | 3.68% | 1.68 |
| 🟢 BULLISH | **APP** | CCI — Extreme Oversold | 58.8 | 59.7% | 2.72% | 1.39 |
| 🟢 BULLISH | **CRWD** | CCI — Extreme Oversold | 58.7 | 57.9% | 1.51% | 1.48 |
| 🟢 BULLISH | **RIOT** | Stochastic (Full) — Oversold | 58.7 | 58.9% | 2.84% | 1.69 |
| 🟢 BULLISH | **CRWD** | Chaikin Money Flow — Bullish | 57.7 | 57.6% | 1.48% | 1.4 |
| 🟢 BULLISH | **GOOGL** | CCI — Extreme Oversold | 57.5 | 59.0% | 0.96% | 1.38 |
| 🟢 BULLISH | **MRVL** | CCI — Extreme Oversold | 57.4 | 59.2% | 1.9% | 1.34 |
| 🟢 BULLISH | **SOXL** | CCI — Extreme Oversold | 56.7 | 59.4% | 3.25% | 1.4 |
| 🟢 BULLISH | **SPY** | CCI — Extreme Oversold | 56.5 | 61.9% | 0.42% | 1.06 |
| 🟢 BULLISH | **QQQ** | CCI — Extreme Oversold | 56.4 | 60.3% | 0.56% | 1.15 |
| 🟢 BULLISH | **AMD** | CCI — Extreme Oversold | 55.5 | 57.8% | 1.79% | 1.4 |
| 🟢 BULLISH | **XLK** | CCI — Extreme Oversold | 55.1 | 59.6% | 0.7% | 1.18 |
| 🟢 BULLISH | **IONQ** | CCI — Extreme Oversold | 53.9 | 52.9% | 3.21% | 1.37 |
| 🟢 BULLISH | **RIOT** | VWAP Deviation — Oversold | 53.4 | 55.0% | 2.47% | 1.33 |
| 🟢 BULLISH | **UPRO** | CCI — Extreme Oversold | 53.0 | 60.3% | 1.01% | 1.01 |
| 🟢 BULLISH | **TQQQ** | CCI — Extreme Oversold | 52.8 | 59.6% | 1.41% | 1.09 |
| 🟢 BULLISH | **XBI** | CCI — Extreme Oversold | 51.9 | 57.7% | 0.63% | 1.04 |
| 🟢 BULLISH | **ARKK** | CCI — Extreme Oversold | 51.8 | 58.4% | 0.89% | 1.01 |
| 🟢 BULLISH | **RIOT** | Keltner — Lower Channel Touch | 51.6 | 53.8% | 2.31% | 1.44 |
| 🟢 BULLISH | **SMCI** | Fisher Transform — Low Extreme | 51.5 | 50.0% | 4.35% | 1.41 |
| 🟢 BULLISH | **CRWD** | Aroon — Strong Uptrend | 51.5 | 55.8% | 1.13% | 1.09 |
| 🟢 BULLISH | **ARM** | Fisher Transform — Low Extreme | 51.4 | 55.6% | 1.78% | 1.46 |
| 🟢 BULLISH | **AVGO** | CCI — Extreme Oversold | 50.9 | 54.0% | 1.3% | 1.14 |
| 🟢 BULLISH | **MRVL** | Williams %R — Oversold | 50.8 | 63.9% | 1.57% | 1.08 |
| 🟢 BULLISH | **ARKK** | Aroon — Strong Uptrend | 50.5 | 56.8% | 0.92% | 1.03 |
| 🟢 BULLISH | **IWM** | CCI — Extreme Oversold | 50.3 | 56.5% | 0.45% | 0.88 |
| 🔴 BEARISH | **UPRO** | Chaikin Money Flow — Bearish | 92.0 | 81.6% | 7.93% | 7.96 |
| 🔴 BEARISH | **IWM** | TRIX — Bearish Cross | 88.6 | 78.6% | 1.53% | 3.75 |
| 🔴 BEARISH | **XLE** | Aroon — Strong Downtrend | 88.2 | 78.1% | 1.62% | 4.36 |
| 🔴 BEARISH | **SPY** | SMA 30 — Bearish Loss | 85.3 | 78.9% | 1.23% | 4.08 |
| 🔴 BEARISH | **MRVL** | Awesome Oscillator — Bearish Zero Line | 83.3 | 83.3% | 3.55% | 4.88 |
| 🔴 BEARISH | **META** | Chaikin Money Flow — Bearish | 82.2 | 64.8% | 2.71% | 3.65 |
| 🔴 BEARISH | **PLTR** | Vortex — Bearish | 81.8 | 68.4% | 3.44% | 2.51 |
| 🔴 BEARISH | **SMH** | Ulcer Index — Elevated | 81.7 | 74.1% | 2.2% | 3.96 |
| 🔴 BEARISH | **UPRO** | SMA 30 — Bearish Loss | 81.7 | 66.7% | 3.04% | 3.42 |
| 🔴 BEARISH | **QQQ** | Awesome Oscillator — Bearish Zero Line | 81.3 | 70.0% | 1.25% | 3.03 |
| 🔴 BEARISH | **UPRO** | Elder Force — Bearish | 81.3 | 70.0% | 1.8% | 2.91 |
| 🔴 BEARISH | **TSLA** | EMA 9/21 — Bearish Cross | 78.2 | 72.7% | 2.19% | 4.47 |
| 🔴 BEARISH | **SMH** | Awesome Oscillator — Bearish Zero Line | 76.9 | 72.7% | 1.07% | 2.33 |
| 🔴 BEARISH | **AVGO** | Aroon — Strong Downtrend | 76.2 | 62.8% | 3.43% | 3.0 |
| 🔴 BEARISH | **XBI** | MFI — Overbought | 75.2 | 84.6% | 1.0% | 1.65 |
| 🔴 BEARISH | **IWM** | SMA 30 — Bearish Loss | 73.7 | 73.9% | 1.1% | 1.98 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 73.2 | 67.3% | 1.08% | 1.99 |
| 🔴 BEARISH | **GOOGL** | SMA 30 — Bearish Loss | 71.4 | 63.6% | 2.18% | 2.57 |
| 🔴 BEARISH | **IWM** | Parabolic SAR — Bearish | 70.8 | 69.6% | 1.04% | 1.81 |
| 🔴 BEARISH | **RKLB** | Chaikin Money Flow — Bearish | 66.8 | 56.2% | 4.17% | 1.97 |
| 🔴 BEARISH | **IWM** | Vortex — Bearish | 65.0 | 62.5% | 0.89% | 1.76 |
| 🔴 BEARISH | **NVDA** | Aroon — Strong Downtrend | 64.1 | 60.0% | 1.68% | 1.8 |
| 🔴 BEARISH | **DOGE-USD** | Parabolic SAR — Bearish | 63.5 | 48.1% | 3.15% | 1.94 |
| 🔴 BEARISH | **GOOGL** | Stochastic RSI Overbought | 62.6 | 61.6% | 1.01% | 1.58 |
| 🔴 BEARISH | **SOXL** | Aroon — Strong Downtrend | 62.2 | 64.2% | 4.05% | 1.62 |
| 🔴 BEARISH | **RIOT** | Aroon — Strong Downtrend | 59.8 | 58.3% | 2.86% | 1.67 |
| 🔴 BEARISH | **PLTR** | Stochastic (Full) — Overbought | 57.5 | 59.3% | 1.91% | 1.31 |
| 🔴 BEARISH | **PLTR** | Stochastic RSI Overbought | 55.6 | 58.9% | 1.82% | 1.26 |
| 🔴 BEARISH | **CRWD** | VWAP Deviation — Overbought | 55.3 | 56.8% | 1.28% | 1.23 |
| 🔴 BEARISH | **IWM** | Elder Force — Bearish | 54.0 | 58.8% | 0.59% | 1.12 |
| 🔴 BEARISH | **TSLA** | Vortex — Bearish | 51.4 | 46.4% | 1.92% | 1.24 |
| 🔴 BEARISH | **SMCI** | Aroon — Strong Downtrend | 50.2 | 52.3% | 2.39% | 1.06 |

---
*Not financial advice. Backtests use historical data.*