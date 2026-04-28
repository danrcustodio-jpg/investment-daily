"""
GitHub Actions usage checker for Investment Daily.

Reads GITHUB_TOKEN from .env and calls the GitHub billing API to show
how many Actions minutes you've used this billing cycle and warns when
you're approaching the free-tier cap (2,000 min/month for private repos).

Usage:
    python check_github_usage.py
"""

import os
import sys
import math
from pathlib import Path
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    sys.exit("requests is not installed. Run: pip install requests")

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

FREE_TIER_MINUTES = 2_000
WARN_PCT = 0.75   # warn at 75 %
CRITICAL_PCT = 0.90  # critical at 90 %


def estimate_monthly_minutes() -> dict:
    """Rough estimate of minutes consumed by both workflows each month."""
    # newsletter.yml: 1 run/day × 30 days, ~4 min/run
    newsletter_runs = 30
    newsletter_min_per_run = 4

    # alerts.yml: every 30 min, 13:00-21:30 UTC = 17 slots/day, weekdays only
    # ~22 weekdays/month; each run ≈ 3 min (pip cache usually warm)
    alert_runs = 17 * 22
    alert_min_per_run = 3

    newsletter_total = newsletter_runs * newsletter_min_per_run
    alert_total = alert_runs * alert_min_per_run
    grand_total = newsletter_total + alert_total

    return {
        "newsletter": {"runs": newsletter_runs, "minutes": newsletter_total},
        "alerts": {"runs": alert_runs, "minutes": alert_total},
        "total_minutes": grand_total,
        "pct_of_free_tier": grand_total / FREE_TIER_MINUTES * 100,
    }


def check_github_billing(token: str, username: str) -> dict | None:
    """Call the GitHub billing API and return the actions usage data."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/users/{username}/settings/billing/actions"
    resp = requests.get(url, headers=headers, timeout=10)

    if resp.status_code == 401:
        print("  ERROR: Token is invalid or expired.")
        return None
    if resp.status_code == 403:
        print("  ERROR: Token lacks the required 'user' scope.")
        print("  Re-generate your PAT at https://github.com/settings/tokens")
        print("  and make sure the 'user' scope is checked.")
        return None
    if resp.status_code == 404:
        print(f"  ERROR: User '{username}' not found, or this is an org account.")
        print("  For org accounts change the URL to /orgs/{org}/settings/billing/actions")
        return None
    if not resp.ok:
        print(f"  ERROR: GitHub API returned {resp.status_code}: {resp.text[:200]}")
        return None

    return resp.json()


def get_repo_visibility(token: str, username: str, repo: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.get(
        f"https://api.github.com/repos/{username}/{repo}",
        headers=headers,
        timeout=10,
    )
    if resp.ok:
        return "public" if not resp.json().get("private") else "private"
    return None


def bar(used: int, total: int, width: int = 30) -> str:
    filled = math.ceil(used / total * width) if total else 0
    filled = min(filled, width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def main():
    token = os.getenv("GITHUB_TOKEN", "").strip()
    username = os.getenv("GITHUB_USERNAME", "").strip()

    print("=" * 60)
    print("  GitHub Actions Usage — Investment Daily")
    print("=" * 60)

    # ── Local estimate (always available) ───────────────────────
    est = estimate_monthly_minutes()
    print("\n  ESTIMATED monthly usage (based on your two workflows):")
    print(f"    newsletter.yml  : {est['newsletter']['runs']:>3} runs × ~4 min = {est['newsletter']['minutes']:>4} min")
    print(f"    alerts.yml      : {est['alerts']['runs']:>3} runs × ~3 min = {est['alerts']['minutes']:>4} min")
    print(f"    Total estimate  : {est['total_minutes']:>4} min  ({est['pct_of_free_tier']:.0f}% of {FREE_TIER_MINUTES:,} free-tier cap)")

    if est["pct_of_free_tier"] >= 90:
        print("\n  WARNING: Estimated usage EXCEEDS 90% of the free tier!")
    elif est["pct_of_free_tier"] >= 75:
        print("\n  NOTE: Estimated usage is above 75% — monitor closely.")

    # ── Live check via API (requires token) ─────────────────────
    if not token:
        print("\n" + "-" * 60)
        print("  LIVE CHECK: No GITHUB_TOKEN found in .env")
        print("  Add one to get live billing data:")
        print("    1. https://github.com/settings/tokens")
        print("       -> Generate new token (classic)")
        print("    2. Select the 'user' scope (read:user is sufficient)")
        print("    3. Add  GITHUB_TOKEN=ghp_...  to your .env")
        print("    4. Add  GITHUB_USERNAME=<your_github_username>  to your .env")
        print("-" * 60)
        return

    if not username:
        print("\n  LIVE CHECK: GITHUB_TOKEN found but GITHUB_USERNAME is missing.")
        print("  Add  GITHUB_USERNAME=<your_github_username>  to your .env")
        return

    print("\n" + "-" * 60)
    print(f"  LIVE CHECK: querying GitHub API as '{username}' …")

    # Check repo visibility
    repo_name = SCRIPT_DIR.name  # folder name is usually the repo name
    visibility = get_repo_visibility(token, username, repo_name)
    if visibility:
        print(f"  Repo '{repo_name}': {visibility}")
        if visibility == "public":
            print("  Public repos have UNLIMITED free Actions minutes — you're all good!")

    data = check_github_billing(token, username)
    if not data:
        return

    used = data.get("total_minutes_used", 0)
    paid = data.get("total_paid_minutes_used", 0)
    free_remaining = data.get("included_minutes", FREE_TIER_MINUTES) - used
    cap = data.get("included_minutes", FREE_TIER_MINUTES)
    pct = used / cap * 100 if cap else 0

    print("\n  This billing cycle:")
    print(f"    Minutes used    : {used:>6,} / {cap:,}")
    print(f"    Minutes remaining: {max(free_remaining, 0):>5,}")
    print(f"    Paid overage    : {paid:>6,} min")
    print(f"\n  {bar(used, cap)} {pct:.1f}%")

    if pct >= CRITICAL_PCT * 100:
        print("\n  !! CRITICAL: You've used over 90% of your free Actions minutes!")
        print("     Consider making the repo public, or reducing alert frequency.")
    elif pct >= WARN_PCT * 100:
        print(f"\n  WARNING: You've used {pct:.0f}% of your free Actions minutes.")
        print("     You have roughly", max(free_remaining, 0), "minutes left this cycle.")
    else:
        print(f"\n  OK: Usage is at {pct:.1f}% — well within the free tier.")

    print("=" * 60)


if __name__ == "__main__":
    main()
