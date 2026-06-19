# Strategy Alerts
**Last scan:** Friday June 19, 2026 at 06:34 PM

## Scan Summary

| | Count |
|---|---|
| Total signals scanned (confidence ≥ 50) | 18 |
| 🟢 Bullish | 16 |
| 🔴 Bearish | 9 |
| ✅ Fired this run (SMS + email) | 3 |
| ⏭ Skipped — same ticker notified in last 6h | 15 |
| ⏸ Suppressed — same signal already fired in last 6h | 0 |
| 🚀 Bypassed cooldown (large price move) | 0 |
| 😴 Snoozed by strategy/ticker | 0 |
| ⚠ Tickers with conflicting BULL+BEAR signals | 1 |

## 📲 SMS sent (3)

- One text per ticker: **DOGE-USD, BCH-USD, AVAX-USD**

## ⚠ Conflicting tickers (both directions ≥ 65)

Tickers where bullish *and* bearish strategies are firing above the conflict threshold at the same time. Treat the headline as one input only.

| Ticker | 🟢 Bull top | Score | n | 🔴 Bear top | Score | n |
|---|---|---:|---:|---|---:|---:|
| **GC=F** | Keltner — Lower Channel Touch | 70.5 | 2 | MACD Bearish Crossover | 85.0 | 2 |

## ✅ Fired this run (SMS + email)

Signals that **actually triggered** an SMS / email on this run.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🔴 BEARISH | **DOGE-USD** | Parabolic SAR — Bearish | 67.7 | 51.9% | 3.35% | 2.06 |
| 🔴 BEARISH | **BCH-USD** | Parabolic SAR — Bearish | 56.7 | 46.9% | 1.75% | 1.65 |
| 🔴 BEARISH | **AVAX-USD** | Parabolic SAR — Bearish | 54.8 | 58.1% | 2.08% | 1.51 |

## ⏭ Skipped — same ticker already notified

Above-threshold signals dropped because another strategy on the same ticker fired within the last 6h ticker-cooldown window.

| Direction | Ticker | Strategy | Confidence | Win Rate | Avg Return (5d) | Sharpe |
|---|---|---|---|---|---|---|
| 🟢 BULLISH | **CL=F** | Stochastic RSI Oversold | 78.1 | 67.3% | 2.05% | 2.81 |
| 🟢 BULLISH | **CL=F** | Keltner — Lower Channel Touch | 74.2 | 61.3% | 1.61% | 2.49 |
| 🟢 BULLISH | **CL=F** | Fisher Transform — Low Extreme | 72.7 | 64.5% | 1.24% | 2.37 |
| 🟢 BULLISH | **GC=F** | Keltner — Lower Channel Touch | 70.5 | 55.9% | 1.1% | 2.22 |
| 🟢 BULLISH | **GC=F** | Chaikin Money Flow — Bullish | 66.4 | 68.8% | 0.77% | 1.4 |
| 🟢 BULLISH | **MRVL** | ADX Strong Trend — Bullish | 59.9 | 62.2% | nan% | 0.0 |
| 🟢 BULLISH | **AVGO** | Stochastic RSI Oversold | 59.0 | 65.2% | nan% | 0.0 |
| 🟢 BULLISH | **CL=F** | VWAP Deviation — Oversold | 57.6 | 63.5% | 0.97% | 1.18 |
| 🟢 BULLISH | **AMD** | ADX Strong Trend — Bullish | 56.8 | 57.5% | 2.29% | 1.49 |
| 🟢 BULLISH | **ADA-USD** | RSI Oversold | 53.8 | 62.3% | 2.26% | 1.34 |
| 🔴 BEARISH | **GC=F** | MACD Bearish Crossover | 85.0 | 75.0% | 1.19% | 2.73 |
| 🔴 BEARISH | **GC=F** | ADX Strong Trend — Bearish | 83.8 | 72.7% | 1.81% | 4.03 |
| 🔴 BEARISH | **ADA-USD** | Parabolic SAR — Bearish | 74.2 | 61.3% | 6.2% | 2.65 |
| 🔴 BEARISH | **AERO-USD** | MFI — Overbought | 70.2 | 50.8% | 8.98% | 2.09 |
| 🔴 BEARISH | **BTC-USD** | Chaikin Money Flow — Bearish | 56.7 | 65.2% | 1.1% | 1.15 |

---
*Not financial advice. Backtests use historical data.*