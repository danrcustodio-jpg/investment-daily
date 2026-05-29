# Investment Daily

Automated investment newsletter, intraday strategy alerts, and portfolio simulation.
Powered by GitHub Actions — runs 24/7 with no PC required.

**Last updated:** May 28, 2026 at 09:50 PM

---

## Live Reports

| Report | Description | Link |
|---|---|---|
| Strategy Alerts | Latest signal scan with confidence scores | [View →](reports/ALERTS.md) |
| Newsletter Summary | Daily market overview and top movers | [View →](reports/NEWSLETTER.md) |
| Portfolio Simulation | $194k paper portfolio vs SPY | [View →](reports/SIMULATION.md) |

## Portfolio Simulation

Day 20 &nbsp;·&nbsp; Portfolio **+1.19%** vs SPY +6.61% &nbsp;·&nbsp; Alpha ❌ **-5.42%**

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

## Cloud Hosting (Render)

You can host the dashboard for free on [Render](https://render.com/) using the included `render.yaml`.

1. Push this repo to GitHub.
2. In Render, choose **New +** -> **Blueprint**.
3. Select this repository; Render auto-detects `render.yaml`.
4. Deploy and open the generated URL.

Notes:
- Free tier web services may sleep when idle (first request can be slow).
- The service runs with **Gunicorn** and a **`/health`** probe so deploy health checks do not hit `/` (the home page can run a heavy first-time strategy scan).
- Render picks a **supported Python** automatically unless you set `PYTHON_VERSION` in the service **Environment** tab (only pin if you need to match local).
- Add environment variables in Render dashboard as needed (`EMAIL_SENDER`, `EMAIL_PASSWORD`, etc.).
- Use `https://<your-render-url>/hub` for the hub page and `https://<your-render-url>/asset-opportunities` for the opportunity page.

If a deploy still fails, open the **Render deploy log**: build errors usually mean a dependency or Python version mismatch; runtime crashes often mean **out of memory** on the free tier during the first full `run_full_scan` (wait for wake or upgrade plan).

---
*This repo is auto-updated by GitHub Actions. Reports commit after every run.*
*Not financial advice.*
