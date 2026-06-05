"""Test federal contract alert logic — no email sent.

Three checks:
  1. Recipient-name pattern matching maps known subsidiaries to the right ticker.
  2. State-based deduplication: an award already in state is filtered out.
  3. (Optional) Live API smoke test against USAspending — skipped if
     SKIP_NETWORK_TESTS=1 is in the environment, or if requests fails.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contract_watchlist import WATCHLIST, match_ticker, resolve_watchlist
import contract_alerts


# ─── Test 1: pattern matching ────────────────────────────────────────────────

print("[1/3] Pattern matching...")
resolved = resolve_watchlist()

cases = [
    ("LOCKHEED MARTIN CORPORATION",            "LMT"),
    ("Sikorsky Aircraft Corporation",          "LMT"),
    ("RAYTHEON COMPANY",                       "RTX"),
    ("Collins Aerospace Systems",              "RTX"),
    ("Pratt & Whitney",                        "RTX"),
    ("Northrop Grumman Systems Corporation",   "NOC"),
    ("General Dynamics Land Systems, Inc.",    "GD"),
    ("Bath Iron Works Corporation",            "GD"),
    ("The Boeing Company",                     "BA"),
    ("PALANTIR USG, INC.",                     "PLTR"),
    ("Leidos, Inc.",                           "LDOS"),
    ("Booz Allen Hamilton Inc.",               "BAH"),
    ("Microsoft Corporation",                  "MSFT"),
    ("Amazon Web Services, Inc.",              "AMZN"),
    ("Some Random Plumbing Company",           None),
]
failures = []
for recipient, want in cases:
    got = match_ticker(recipient, resolved)
    ok = (got == want)
    marker = "OK " if ok else "FAIL"
    print(f"  [{marker}] {recipient!r:<48} -> {got!r:<8} want {want!r}")
    if not ok:
        failures.append((recipient, want, got))

assert not failures, f"{len(failures)} pattern-match failure(s): {failures}"
print(f"  Resolved watchlist size: {len(resolved)} ticker(s)")

# Sanity-check that every curated entry survived the merge.
for ticker in WATCHLIST:
    assert ticker in resolved, f"{ticker} dropped from resolved watchlist"


# ─── Test 2: dedup via state ─────────────────────────────────────────────────

print("\n[2/3] Dedup state...")

with tempfile.TemporaryDirectory() as tmpdir:
    contract_alerts.STATE_FILE = os.path.join(tmpdir, "contract_state.json")

    sample_award = {
        "Award ID": "FA8730-26-C-0001",
        "Recipient Name": "LOCKHEED MARTIN CORPORATION",
        "Award Amount": 12_345_678,
        "Description": "Test contract for unit testing.",
        "Start Date": "2026-06-01",
        "End Date": "2027-06-01",
        "Awarding Agency": "Department of Defense",
        "Awarding Sub Agency": "Department of the Air Force",
        "Contract Award Type": "DEFINITIVE CONTRACT",
        "NAICS": "541330",
        "generated_internal_id": "CONT_AWD_TEST_LMT_001",
    }

    state = contract_alerts.load_state()
    assert state == {"send_count": 0, "seen": {}}, "fresh state should be empty"

    first_pass = contract_alerts.filter_new_awards(
        [sample_award], state, resolved=resolved, expected_ticker="LMT",
    )
    assert len(first_pass) == 1, "first pass should surface the new award"
    assert first_pass[0]["ticker"] == "LMT"
    assert first_pass[0]["amount"] == 12_345_678.0

    state["seen"][sample_award["generated_internal_id"]] = "2026-06-04T12:00:00+00:00"
    contract_alerts.save_state(state)

    reloaded = contract_alerts.load_state()
    second_pass = contract_alerts.filter_new_awards(
        [sample_award], reloaded, resolved=resolved, expected_ticker="LMT",
    )
    assert second_pass == [], "second pass should dedupe the already-seen award"
    print("  OK  fresh award surfaced once, then deduped on repeat")

    # Email rendering smoke test
    state["send_count"] = 1
    subject, html = contract_alerts.build_contract_email(
        {"LMT": [contract_alerts.normalize_award(sample_award, "LMT")]},
        send_count=state["send_count"],
        lookback_days=7,
        min_amount=1_000_000,
    )
    assert "LMT" in subject and "$12.35M" in subject, f"unexpected subject: {subject}"
    assert "Lockheed Martin".upper() in html.upper()
    assert "usaspending.gov/award/CONT_AWD_TEST_LMT_001" in html
    print(f"  OK  email rendered (subject={subject!r}, html={len(html):,} chars)")


# ─── Test 3: live API smoke (skippable) ──────────────────────────────────────

print("\n[3/3] Live API smoke test...")
if os.getenv("SKIP_NETWORK_TESTS") == "1":
    print("  SKIPPED (SKIP_NETWORK_TESTS=1)")
else:
    try:
        import requests
        body = {
            "filters": {
                "time_period": [{"start_date": "2026-01-01", "end_date": "2026-12-31"}],
                "award_type_codes": contract_alerts.CONTRACT_AWARD_TYPE_CODES,
                "recipient_search_text": ["lockheed martin"],
                "award_amounts": [{"lower_bound": 100_000_000}],
            },
            "fields": contract_alerts.REQUEST_FIELDS,
            "sort": "Award Amount", "order": "desc", "limit": 5, "page": 1,
        }
        resp = requests.post(contract_alerts.API_URL, json=body, timeout=20)
        resp.raise_for_status()
        rows = resp.json().get("results") or []
        print(f"  OK  USAspending API reachable, returned {len(rows)} sample row(s)")
        if rows:
            r0 = rows[0]
            print(f"      sample: {r0.get('Recipient Name')!r} "
                  f"${float(r0.get('Award Amount') or 0):,.0f}")
    except Exception as e:
        print(f"  WARN  live API call failed ({e!r}) — non-fatal, network may be down")


print("\nContract alert tests passed.")
