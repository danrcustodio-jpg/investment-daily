# GitHub Actions Setup Guide

Follow these steps once to get the newsletter, alerts, and simulation running
in the cloud — no PC required.

**Time to complete:** ~20 minutes  
**Cost:** Free

---

## Step 1: Create a GitHub Account

Go to [github.com](https://github.com) and sign up if you don't have an account.

---

## Step 2: Create a Private Repository

1. Click the **+** button (top right) → **New repository**
2. Name it: `investment-daily` (or anything you like)
3. Set it to **Private**
4. Do **not** initialize with a README (we have our own)
5. Click **Create repository**

GitHub will show you a page with setup commands. Keep this tab open.

---

## Step 3: Push the Code from Your PC

Open PowerShell and run these commands:

```powershell
cd "C:\Users\Owner\InvestmentDaily"

# Initialize git (first time only)
git init
git branch -M main

# Connect to your new GitHub repo
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/investment-daily.git

# Push everything
git add .
git commit -m "Initial deployment"
git push -u origin main
```

If prompted for credentials, use your GitHub username and a
**Personal Access Token** (not your password):
- Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
- Generate new token → check `repo` scope → copy the token
- Paste it as the password when prompted

---

## Step 4: Add Your Email Credentials as Secrets

GitHub Secrets are encrypted — they are never visible to anyone, even in public repos.

1. Go to your repo on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** — add these two:

| Name | Value |
|---|---|
| `EMAIL_SENDER` | your Gmail address (e.g. `yourname@gmail.com`) |
| `EMAIL_PASSWORD` | your Gmail App Password (16 chars, e.g. `xxxx xxxx xxxx xxxx`) |

> **What is a Gmail App Password?**  
> It's a separate password for apps — NOT your regular Gmail password.  
> Generate one at: Google Account → Security → 2-Step Verification → App passwords  
> Select "Mail" + "Windows Computer" → Generate

---

## Step 5: Verify the Workflows Exist

In your repo on GitHub, click the **Actions** tab.
You should see two workflows listed:
- **Daily Newsletter**
- **Strategy Alerts**

If you don't see them, make sure the `.github/workflows/` folder was pushed correctly.

---

## Step 6: Test It (Manual Trigger)

1. Click **Actions** tab → **Daily Newsletter**
2. Click **Run workflow** → **Run workflow**
3. Watch it run (takes ~2-3 minutes)
4. When it finishes, check:
   - Your email for the newsletter
   - Your repo's `reports/` folder for the new markdown files
   - The repo homepage (README.md) should show live status

---

## Step 7: You're Done

From now on, GitHub automatically runs:

| What | When | Result |
|---|---|---|
| Newsletter | Daily at ~7:30 AM ET | Email + `reports/NEWSLETTER.md` updated |
| Alerts | Every 30 min, Mon–Fri market hours | Email (if new signals) + `reports/ALERTS.md` updated |
| Simulation | With every alert run | `reports/SIMULATION.md` updated |

**To check status from your phone:**  
Open `github.com/YOUR_USERNAME/investment-daily` in your mobile browser.
The repo homepage (README.md) shows live simulation performance.
Tap any report link to see the full details — rendered as a clean table.

---

## Troubleshooting

**Workflow fails with email error:**  
Check that `EMAIL_SENDER` and `EMAIL_PASSWORD` secrets are set correctly.
The App Password should have no spaces when stored.

**"Nothing to commit" in the logs:**  
This is normal when no new signals were found or prices didn't change significantly.

**Alerts not running:**  
The alert_system.py exits silently outside NYSE market hours (Mon–Fri 9:30 AM–4:00 PM ET).
This is by design — check the logs to see "Market closed — skipping."

**Want to trigger a run manually:**  
GitHub Actions tab → select workflow → Run workflow button (top right)

**Want to stop the automation:**  
GitHub Actions tab → select workflow → three dots menu → Disable workflow

---

## What Lives Where

| File | Purpose |
|---|---|
| `reports/ALERTS.md` | Latest signal scan — updates every 30 min |
| `reports/SIMULATION.md` | Portfolio simulation status — updates daily |
| `reports/NEWSLETTER.md` | Newsletter summary — updates daily |
| `README.md` | Repo homepage with live simulation P&L |
| `alert_state.json` | Alert deduplication state (auto-managed) |
| `sim_portfolio.json` | Simulation state (auto-managed) |

---

## Keeping Your PC Setup Working Too

The Task Scheduler jobs on your PC still work independently.
Running both PC + GitHub Actions is fine — they share the same email
but each has its own `alert_state.json` (the PC version is local,
GitHub's is in the repo). They won't conflict.

If you want to use GitHub as the primary and turn off the PC jobs:

```powershell
schtasks /delete /tn "InvestmentDailyNewsletter" /f
schtasks /delete /tn "InvestmentDailyAlerts" /f
schtasks /delete /tn "InvestmentDailySimSnapshot" /f
```
