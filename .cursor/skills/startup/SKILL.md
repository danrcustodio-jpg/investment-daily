---
name: startup
description: Ensure Investment Daily is ready locally with one startup routine. Use when the user asks to start the dashboard, check local/cloud readiness, verify no local scheduled tasks are active, or run a quick health check.
disable-model-invocation: true
---

# Startup

## Purpose

Run a single readiness routine for this project:
- Ensure `dashboard.py` is running on port `5050`
- Verify cloud workflow files exist
- Check for local scheduled task drift
- Validate `/api/status` returns healthy data

## Execution Steps

1. Confirm workspace is `C:\Users\Owner\InvestmentDaily`.
2. Dashboard process check:
   - Check whether `http://127.0.0.1:5050/api/status` is reachable.
   - If unreachable, start `python dashboard.py` in background.
   - Wait briefly, then confirm `/api/status` responds.
3. Cloud workflow presence check:
   - Confirm both files exist:
     - `.github/workflows/alerts.yml`
     - `.github/workflows/newsletter.yml`
4. Local scheduler drift check:
   - Query for tasks named `InvestmentDailyAlerts` and `InvestmentDailyNewsletter`.
   - If present, report that local automation exists and may conflict with cloud-only intent.
5. Return a concise report:
   - Dashboard: running/not running
   - Health endpoint: pass/fail (+ key status fields if available)
   - Workflow files: found/missing
   - Scheduled tasks: found/not found
   - Next action if any check fails

## PowerShell Commands (Preferred)

```powershell
# 1) Health probe
try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5050/api/status -TimeoutSec 5 } catch {}

# 2) Start dashboard only if needed
python dashboard.py

# 3) Workflow presence
Test-Path ".github/workflows/alerts.yml"
Test-Path ".github/workflows/newsletter.yml"

# 4) Scheduler drift
schtasks /Query /TN "InvestmentDailyAlerts" /FO LIST
schtasks /Query /TN "InvestmentDailyNewsletter" /FO LIST
```

## Notes

- Keep output brief and operational.
- Do not create/update scheduled tasks in this routine; only detect and report.
- If dashboard is started, include the URL: `http://127.0.0.1:5050/hub`.
