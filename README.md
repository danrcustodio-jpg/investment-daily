# Investment Daily

Automated investment newsletter, intraday strategy alerts, and portfolio simulation.
Powered by GitHub Actions — runs 24/7 with no PC required.

**Last updated:** August 12, 2026 at 01:59 PM

---

## Live Reports

| Report | Description | Link |
|---|---|---|
| Strategy Alerts | Latest signal scan with confidence scores | [View →](reports/ALERTS.md) |
| Newsletter Summary | Daily market overview and top movers | [View →](reports/NEWSLETTER.md) |
| Portfolio Simulation | $194k paper portfolio vs SPY | [View →](reports/SIMULATION.md) |

## Portfolio Simulation

Day 96 &nbsp;·&nbsp; Portfolio **+1.94%** vs SPY +9.16% &nbsp;·&nbsp; Alpha ❌ **-7.23%**

[Full details with equity curve →](reports/SIMULATION.md)

---

## System

| Component | Schedule |
|---|---|
| Daily Newsletter | 7:30 AM ET every day |
| Strategy Alerts | Every 30 min, Mon–Fri, 9:30 AM – 4:00 PM ET |
| Alert cooldown | Same ticker+strategy: at most once per 6 hours |
| Signals tracked | 28 tickers × 30 strategy detectors |

## Docs

- [Architecture & Data Flow](ARCHITECTURE.md)
- [Agent Guide — Change Recipes](AGENT_GUIDE.md)

---
*This repo is auto-updated by GitHub Actions. Reports commit after every run.*
*Not financial advice.*
