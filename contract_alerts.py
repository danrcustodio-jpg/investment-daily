#!/usr/bin/env python3
"""
Federal Contract Alerts.

Polls USAspending.gov daily for newly-awarded federal contracts to companies
on the resolved watchlist (curated contractors + SCAN_TICKERS overlap),
deduplicates by award ID, and emails a roundup using the existing Gmail
SMTP setup from alert_system.py.

API: https://api.usaspending.gov/api/v2/search/spending_by_award/
Docs: https://api.usaspending.gov/docs/endpoints
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, UTC
from typing import Any
from collections.abc import Iterable

import requests
from dotenv import load_dotenv

from alert_system import send_email as _send_alert_email_via_gmail
from contract_watchlist import match_ticker, resolve_watchlist

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(SCRIPT_DIR, "logs"), exist_ok=True)
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(SCRIPT_DIR, "logs", "contract_alerts.log"),
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────

API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
AWARD_DETAIL_URL = "https://www.usaspending.gov/award/{award_id}/"

# Contract award type codes per USAspending data dictionary:
#   A = BPA Call, B = Purchase Order, C = Delivery Order, D = Definitive Contract
CONTRACT_AWARD_TYPE_CODES = ["A", "B", "C", "D"]

REQUEST_FIELDS = [
    "Award ID",
    "Recipient Name",
    "Award Amount",
    "Description",
    "Start Date",
    "End Date",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Contract Award Type",
    "NAICS",
    "generated_internal_id",
]

STATE_FILE = os.path.join(SCRIPT_DIR, "contract_state.json")
STATE_RETENTION_DAYS = 90
PER_TICKER_DELAY_SEC = 0.2
REQUEST_TIMEOUT_SEC = 30


def _int_env(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid value for %s=%r — using default %s", name, raw, default)
        return default


DEFAULT_MIN_AMOUNT = _int_env("CONTRACT_MIN_AMOUNT", 1_000_000)
DEFAULT_LOOKBACK_DAYS = _int_env("CONTRACT_LOOKBACK_DAYS", 7)


# ─── State (dedup) ───────────────────────────────────────────────────────────

def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {"send_count": 0, "seen": {}}
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        data.setdefault("send_count", 0)
        data.setdefault("seen", {})
        return data
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Failed to read state file (%s) — starting fresh.", e)
        return {"send_count": 0, "seen": {}}


def save_state(state: dict) -> None:
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
    os.replace(tmp, STATE_FILE)


def prune_state(state: dict, retention_days: int = STATE_RETENTION_DAYS) -> dict:
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    kept: dict[str, str] = {}
    for award_id, iso_ts in (state.get("seen") or {}).items():
        try:
            ts = datetime.fromisoformat(iso_ts)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
        except (TypeError, ValueError):
            continue
        if ts >= cutoff:
            kept[award_id] = iso_ts
    pruned = len(state.get("seen") or {}) - len(kept)
    if pruned > 0:
        logger.info("Pruned %d old award(s) from state (>%dd).", pruned, retention_days)
    state["seen"] = kept
    return state


# ─── API client ──────────────────────────────────────────────────────────────

def fetch_contracts_for_ticker(
    ticker: str,
    patterns: list[str],
    *,
    start_date: str,
    end_date: str,
    min_amount: int,
    session: requests.Session | None = None,
) -> list[dict]:
    """Hit USAspending for one ticker. Returns a list of raw award dicts."""
    body: dict[str, Any] = {
        "filters": {
            "time_period": [{"start_date": start_date, "end_date": end_date}],
            "award_type_codes": CONTRACT_AWARD_TYPE_CODES,
            "recipient_search_text": patterns,
            "award_amounts": [{"lower_bound": min_amount}],
        },
        "fields": REQUEST_FIELDS,
        "sort": "Award Amount",
        "order": "desc",
        "limit": 100,
        "page": 1,
    }
    s = session or requests
    resp = s.post(API_URL, json=body, timeout=REQUEST_TIMEOUT_SEC)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("results") or []


# ─── Filtering & normalization ───────────────────────────────────────────────

def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _safe_amount(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _truncate(text: str, n: int = 300) -> str:
    text = (text or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def normalize_award(raw: dict, ticker: str) -> dict:
    """Flatten a raw API row into a stable dict the email builder consumes."""
    return {
        "ticker": ticker,
        "award_id":            _safe_str(raw.get("Award ID")),
        "generated_internal_id": _safe_str(raw.get("generated_internal_id")),
        "recipient":           _safe_str(raw.get("Recipient Name")),
        "amount":              _safe_amount(raw.get("Award Amount")),
        "description":         _safe_str(raw.get("Description")),
        "start_date":          _safe_str(raw.get("Start Date")),
        "end_date":            _safe_str(raw.get("End Date")),
        "agency":              _safe_str(raw.get("Awarding Agency")),
        "sub_agency":          _safe_str(raw.get("Awarding Sub Agency")),
        "award_type":          _safe_str(raw.get("Contract Award Type")),
        "naics":               _safe_str(raw.get("NAICS")),
    }


def filter_new_awards(
    awards: Iterable[dict],
    state: dict,
    *,
    resolved: dict[str, list[str]],
    expected_ticker: str,
) -> list[dict]:
    """Return only awards whose generated_internal_id isn't in state['seen']
    and whose recipient_name still maps to a watched ticker (defensive check
    in case the API returns over-broad matches for short patterns).
    """
    seen: dict[str, str] = state.get("seen") or {}
    new_rows: list[dict] = []
    for raw in awards:
        gid = _safe_str(raw.get("generated_internal_id"))
        if not gid:
            continue
        if gid in seen:
            continue
        matched = match_ticker(_safe_str(raw.get("Recipient Name")), resolved)
        if matched is None:
            continue
        new_rows.append(normalize_award(raw, matched))
    return new_rows


# ─── Email rendering ─────────────────────────────────────────────────────────

def _fmt_amount(amount: float) -> str:
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.2f}B"
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.1f}K"
    return f"${amount:,.0f}"


def _award_url(gid: str) -> str:
    return AWARD_DETAIL_URL.format(award_id=gid)


def build_contract_card(award: dict) -> str:
    amount_str = _fmt_amount(award["amount"])
    desc = _truncate(award["description"], 320) or "(no description provided)"
    period = " → ".join([p for p in (award["start_date"], award["end_date"]) if p])
    agency_full = award["agency"]
    if award["sub_agency"] and award["sub_agency"] != award["agency"]:
        agency_full = f"{award['agency']} · {award['sub_agency']}"
    url = _award_url(award["generated_internal_id"])

    naics_html = (
        f'<div style="font-size:11px;color:#64748b;margin-top:6px">'
        f'NAICS {award["naics"]}</div>'
    ) if award["naics"] else ""

    return f"""
    <div style="background:#0f172a;border-radius:10px;padding:16px 18px;
                margin-bottom:12px;border:1px solid #1e293b">
      <div style="display:flex;justify-content:space-between;align-items:baseline;
                  flex-wrap:wrap;gap:8px;margin-bottom:8px">
        <div style="font-size:15px;font-weight:700;color:#f1f5f9">
          {award['recipient'] or 'Unknown recipient'}
        </div>
        <div style="font-size:18px;font-weight:900;color:#34d399">
          {amount_str}
        </div>
      </div>
      <div style="font-size:12px;color:#94a3b8;margin-bottom:8px">
        {agency_full or 'Agency unknown'}
        {(' &nbsp;·&nbsp; ' + award['award_type']) if award['award_type'] else ''}
      </div>
      <div style="font-size:13px;color:#cbd5e1;line-height:1.5;margin-bottom:10px">
        {desc}
      </div>
      <div style="font-size:11px;color:#64748b;margin-bottom:10px">
        {('Period: ' + period) if period else ''}
      </div>
      {naics_html}
      <div style="margin-top:10px">
        <a href="{url}"
           style="display:inline-block;background:#1e3a8a;color:#dbeafe;
                  padding:7px 14px;border-radius:6px;text-decoration:none;
                  font-size:12px;font-weight:600">
          View on USAspending.gov →
        </a>
      </div>
    </div>
    """


def build_ticker_section(ticker: str, awards: list[dict]) -> str:
    total = sum(a["amount"] for a in awards)
    cards = "\n".join(build_contract_card(a) for a in awards)
    return f"""
    <div style="margin-bottom:24px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;
                  margin-bottom:10px;padding:0 4px">
        <h3 style="margin:0;color:#f1f5f9;font-size:18px;font-weight:800;
                   letter-spacing:0.02em">
          {ticker}
          <span style="color:#64748b;font-weight:500;font-size:13px;
                       margin-left:6px">
            {len(awards)} contract{'s' if len(awards) != 1 else ''}
          </span>
        </h3>
        <div style="color:#34d399;font-size:14px;font-weight:700">
          {_fmt_amount(total)}
        </div>
      </div>
      {cards}
    </div>
    """


def build_contract_email(
    by_ticker: dict[str, list[dict]],
    *,
    send_count: int,
    lookback_days: int,
    min_amount: int,
) -> tuple[str, str]:
    tickers_sorted = sorted(
        by_ticker.keys(),
        key=lambda t: sum(a["amount"] for a in by_ticker[t]),
        reverse=True,
    )
    total_contracts = sum(len(v) for v in by_ticker.values())
    total_amount = sum(a["amount"] for awards in by_ticker.values() for a in awards)

    # Include up to 4 top tickers in the subject so the inbox preview is useful.
    head = tickers_sorted[:4]
    tail_n = len(tickers_sorted) - len(head)
    tickers_label = ", ".join(head) + (f" +{tail_n} more" if tail_n > 0 else "")

    subject = (
        f"Contract Alert #{send_count} — {tickers_label} · "
        f"{_fmt_amount(total_amount)} "
        f"({total_contracts} new contract{'s' if total_contracts != 1 else ''})"
    )

    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p").lstrip("0")

    sections = "\n".join(build_ticker_section(t, by_ticker[t]) for t in tickers_sorted)

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Contract Alert #{send_count} — {time_str}</title>
</head>
<body style="margin:0;padding:0;background:#020617;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif">
<div style="max-width:680px;margin:0 auto;padding:20px 14px">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#064e3b 0%,#0f172a 100%);
              border-radius:14px;padding:24px;margin-bottom:18px;text-align:center">
    <div style="font-size:10px;color:#34d399;letter-spacing:3px;
                text-transform:uppercase;font-weight:700;margin-bottom:10px">
      Federal Contract Alert
    </div>
    <div style="font-size:22px;font-weight:900;color:#f1f5f9;margin-bottom:6px">
      {total_contracts} New Contract{'s' if total_contracts != 1 else ''}
      &nbsp;·&nbsp; {_fmt_amount(total_amount)}
    </div>
    <div style="font-size:12px;color:#64748b">
      {date_str} &nbsp;·&nbsp; {time_str}
      &nbsp;·&nbsp; Lookback {lookback_days}d &nbsp;·&nbsp;
      Min {_fmt_amount(min_amount)}
    </div>
    <div style="font-size:11px;color:#6ee7b7;margin-top:10px;font-weight:600;
                letter-spacing:0.02em">
      Dispatch #{send_count} &nbsp;·&nbsp; deduplicated by award ID
    </div>
  </div>

  <!-- Explanation -->
  <div style="background:#0f172a;border-radius:10px;padding:14px 16px;
              margin-bottom:18px;border:1px solid #1e293b">
    <p style="color:#94a3b8;font-size:12px;margin:0;line-height:1.7">
      <strong style="color:#e2e8f0">How to read these alerts:</strong>
      Each card is a newly-disclosed federal contract awarded to a company on
      your watchlist. Source is
      <a href="https://www.usaspending.gov" style="color:#34d399">usaspending.gov</a>
      via their public API. Use these as a research starting point — large
      multi-year contracts can move equity prices but the announcement is
      often already priced in.
      <strong style="color:#f59e0b">Not financial advice.</strong>
    </p>
  </div>

  {sections}

  <!-- Footer -->
  <div style="text-align:center;padding:16px 0 4px;color:#374151;font-size:11px;
              border-top:1px solid #1e293b">
    <p style="margin:0 0 4px">
      Investment Daily · Federal Contract Alerts &nbsp;·&nbsp;
      Daily roundup, weekdays
    </p>
    <p style="margin:8px 0 0;background:#111827;border-radius:6px;padding:10px;
              color:#6b7280;line-height:1.5">
      Award data is public domain from USAspending.gov. Reporting can lag by
      1-3 business days. Not financial advice — always do your own research
      before trading.
    </p>
  </div>

</div>
</body></html>"""

    return subject, html


# ─── Orchestration ───────────────────────────────────────────────────────────

def _today_window(lookback_days: int) -> tuple[str, str]:
    today = datetime.now(UTC).date()
    start = today - timedelta(days=lookback_days)
    return start.isoformat(), today.isoformat()


def scan(
    *,
    only_ticker: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    min_amount: int = DEFAULT_MIN_AMOUNT,
) -> tuple[dict[str, list[dict]], dict]:
    """Run the full scan. Returns (new_awards_by_ticker, fresh_state).

    State is loaded, pruned, and updated in-memory with the newly-seen IDs
    so callers can decide whether to persist + send.
    """
    resolved = resolve_watchlist()
    if only_ticker:
        if only_ticker not in resolved:
            raise SystemExit(f"Ticker {only_ticker!r} is not in the resolved watchlist.")
        resolved = {only_ticker: resolved[only_ticker]}

    start_date, end_date = _today_window(lookback_days)
    logger.info(
        "Scanning %d ticker(s) for contracts %s..%s, min %s",
        len(resolved), start_date, end_date, _fmt_amount(min_amount),
    )

    state = prune_state(load_state())
    seen: dict[str, str] = state["seen"]
    now_iso = datetime.now(UTC).isoformat()

    by_ticker: dict[str, list[dict]] = {}
    session = requests.Session()
    session.headers.update({"User-Agent": "InvestmentDaily-ContractAlerts/1.0"})

    tickers = list(resolved.keys())
    for idx, ticker in enumerate(tickers):
        patterns = resolved[ticker]
        if not patterns:
            logger.debug("%s: no patterns configured — skipping.", ticker)
            continue
        try:
            raw_rows = fetch_contracts_for_ticker(
                ticker, patterns,
                start_date=start_date, end_date=end_date,
                min_amount=min_amount, session=session,
            )
        except requests.RequestException as e:
            logger.warning("%s: API error (%s) — skipping.", ticker, e)
            continue

        new_rows = filter_new_awards(
            raw_rows, state, resolved=resolved, expected_ticker=ticker,
        )
        if new_rows:
            logger.info(
                "%s: %d new contract(s) (out of %d returned).",
                ticker, len(new_rows), len(raw_rows),
            )
            for row in new_rows:
                gid = row["generated_internal_id"]
                if gid:
                    seen[gid] = now_iso
                by_ticker.setdefault(row["ticker"], []).append(row)
        else:
            logger.debug(
                "%s: 0 new (returned %d).", ticker, len(raw_rows),
            )

        if idx < len(tickers) - 1:
            time.sleep(PER_TICKER_DELAY_SEC)

    state["seen"] = seen
    return by_ticker, state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Federal contract alerts via USAspending.gov.",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results, don't send email or persist state.")
    parser.add_argument("--days", type=int, default=DEFAULT_LOOKBACK_DAYS,
                        help=f"Lookback window in days (default {DEFAULT_LOOKBACK_DAYS}).")
    parser.add_argument("--min-amount", type=int, default=DEFAULT_MIN_AMOUNT,
                        help=f"Minimum contract amount USD (default {DEFAULT_MIN_AMOUNT}).")
    parser.add_argument("--ticker", type=str, default=None,
                        help="Limit scan to a single ticker for testing.")
    args = parser.parse_args(argv)

    logger.info("=== Federal Contract Alerts starting ===")
    by_ticker, state = scan(
        only_ticker=args.ticker,
        lookback_days=args.days,
        min_amount=args.min_amount,
    )
    total_new = sum(len(v) for v in by_ticker.values())

    if total_new == 0:
        logger.info("No new contracts above $%s threshold — no email sent.",
                    f"{args.min_amount:,}")
        if not args.dry_run:
            save_state(state)
        return 0

    state["send_count"] = int(state.get("send_count", 0)) + 1
    subject, html = build_contract_email(
        by_ticker,
        send_count=state["send_count"],
        lookback_days=args.days,
        min_amount=args.min_amount,
    )

    logger.info(
        "Found %d new contract(s) across %d ticker(s): %s",
        total_new, len(by_ticker),
        ", ".join(f"{t}({len(v)})" for t, v in by_ticker.items()),
    )

    if args.dry_run:
        logger.info("[DRY RUN] Subject: %s", subject)
        logger.info("[DRY RUN] HTML length: %d chars", len(html))
        for ticker, awards in by_ticker.items():
            for a in awards:
                logger.info(
                    "  %s  %s  %s  %s",
                    ticker, _fmt_amount(a["amount"]),
                    (a["recipient"] or "?")[:48],
                    (a["description"] or "")[:80],
                )
        return 0

    try:
        _send_alert_email_via_gmail(subject, html)
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return 1

    save_state(state)
    logger.info("=== Federal Contract Alerts finished ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
