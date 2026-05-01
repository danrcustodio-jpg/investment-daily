#!/usr/bin/env python3
"""
Weekly positioning helpers (CFTC COT-first).

This module is intentionally resilient:
- Uses public CFTC Socrata endpoints
- Caches snapshots locally to avoid repeated pulls
- Returns a stable shape even when upstream data is unavailable
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
CACHE_PATH = os.path.join(DATA_DIR, "cot_positioning_cache.json")

logger = logging.getLogger(__name__)

# Public CFTC Socrata datasets (primary first; fallback if schema moves).
CFTC_ENDPOINTS = [
    "https://publicreporting.cftc.gov/resource/kh3c-gbw2.json",
    "https://publicreporting.cftc.gov/resource/6dca-aqww.json",
]

ASSET_TARGETS = [
    {"key": "spx", "label": "S&P 500 Futures", "proxy": "ES", "terms": ["s&p", "500"]},
    {"key": "crude", "label": "WTI Crude Oil Futures", "proxy": "CL", "terms": ["crude", "oil"]},
    {"key": "gold", "label": "Gold Futures", "proxy": "GC", "terms": ["gold"]},
    {"key": "natgas", "label": "Natural Gas Futures", "proxy": "NG", "terms": ["natural", "gas"]},
    {"key": "ust10y", "label": "US 10Y Treasury Note Futures", "proxy": "ZN", "terms": ["10-year", "treasury"]},
]


def _parse_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _pick_first_float(record: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        if key in record:
            parsed = _parse_float(record.get(key))
            if parsed is not None:
                return parsed
    return None


def _read_cache() -> dict[str, Any] | None:
    if not os.path.exists(CACHE_PATH):
        return None
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Failed reading COT cache: %s", exc)
        return None


def _write_cache(payload: dict[str, Any]) -> None:
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception as exc:
        logger.warning("Failed writing COT cache: %s", exc)


def _cache_is_fresh(cache: dict[str, Any]) -> bool:
    fetched_at = cache.get("fetched_at")
    if not fetched_at:
        return False
    try:
        dt = datetime.fromisoformat(fetched_at)
    except ValueError:
        return False
    # COT is weekly; a 36h cache avoids noisy repeat calls while still refreshing.
    return (datetime.utcnow() - dt) < timedelta(hours=36)


def _market_name(record: dict[str, Any]) -> str:
    return str(
        record.get("market_and_exchange_names")
        or record.get("market_and_exchange_name")
        or record.get("contract_market_name")
        or ""
    )


def _report_date(record: dict[str, Any]) -> str:
    raw = (
        record.get("report_date_as_yyyy_mm_dd")
        or record.get("report_date")
        or record.get("as_of_date_in_form_yyyy_mm_dd")
        or ""
    )
    return str(raw)[:10]


def _record_matches(record: dict[str, Any], terms: list[str]) -> bool:
    name = _market_name(record).lower()
    return all(term in name for term in terms)


def _classify_crowding(net_pct_oi: float | None) -> str:
    if net_pct_oi is None:
        return "unknown"
    abs_pct = abs(net_pct_oi)
    if abs_pct >= 20:
        return "extreme"
    if abs_pct >= 10:
        return "crowded"
    return "balanced"


def _build_item(target: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    long_non_comm = _pick_first_float(
        record,
        [
            "noncomm_positions_long_all",
            "noncommercial_positions_long_all",
            "noncommercial_long_all",
            "noncomm_positions_long",
        ],
    )
    short_non_comm = _pick_first_float(
        record,
        [
            "noncomm_positions_short_all",
            "noncommercial_positions_short_all",
            "noncommercial_short_all",
            "noncomm_positions_short",
        ],
    )
    open_interest = _pick_first_float(
        record,
        [
            "open_interest_all",
            "open_interest",
        ],
    )

    net = None
    if long_non_comm is not None and short_non_comm is not None:
        net = long_non_comm - short_non_comm
    net_pct_oi = None
    if net is not None and open_interest:
        net_pct_oi = (net / open_interest) * 100

    crowded_side = "flat"
    if net is not None:
        crowded_side = "long" if net > 0 else ("short" if net < 0 else "flat")

    return {
        "asset_key": target["key"],
        "asset_label": target["label"],
        "proxy": target["proxy"],
        "market_name": _market_name(record),
        "report_date": _report_date(record),
        "non_commercial_long": long_non_comm,
        "non_commercial_short": short_non_comm,
        "open_interest": open_interest,
        "net_contracts": net,
        "net_pct_open_interest": net_pct_oi,
        "crowded_side": crowded_side,
        "crowding": _classify_crowding(net_pct_oi),
    }


def _fetch_latest_records() -> list[dict[str, Any]]:
    params = {
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "$limit": 5000,
    }
    last_err: str | None = None
    for endpoint in CFTC_ENDPOINTS:
        try:
            resp = requests.get(endpoint, params=params, timeout=20)
            resp.raise_for_status()
            rows = resp.json()
            if isinstance(rows, list) and rows:
                return rows
        except Exception as exc:
            last_err = f"{endpoint}: {exc}"
            logger.warning("COT endpoint failed: %s", last_err)
    raise RuntimeError(last_err or "No CFTC endpoint returned usable data")


def _derive_regime(items: list[dict[str, Any]]) -> str:
    crowded = [i for i in items if i.get("crowding") in {"crowded", "extreme"}]
    if not crowded:
        return "Positioning balanced"
    long_count = sum(1 for i in crowded if i.get("crowded_side") == "long")
    short_count = sum(1 for i in crowded if i.get("crowded_side") == "short")
    if long_count > short_count:
        return "Crowded longs building"
    if short_count > long_count:
        return "Crowded shorts building"
    return "Crowding split across markets"


def get_cot_positioning_summary(force_refresh: bool = False) -> dict[str, Any]:
    """
    Return COT-derived positioning snapshot.

    Output keys:
      - source, status, fetched_at, report_as_of, regime, items, note
    """
    cache = _read_cache()
    if not force_refresh and cache and _cache_is_fresh(cache):
        return cache

    try:
        records = _fetch_latest_records()
        items: list[dict[str, Any]] = []
        for target in ASSET_TARGETS:
            match = next((r for r in records if _record_matches(r, target["terms"])), None)
            if not match:
                continue
            items.append(_build_item(target, match))

        if not items:
            raise RuntimeError("No target contracts matched in COT payload")

        report_as_of = max((i.get("report_date") or "" for i in items), default="")
        payload = {
            "source": "CFTC COT (publicreporting.cftc.gov)",
            "status": "ok",
            "fetched_at": datetime.utcnow().isoformat(),
            "report_as_of": report_as_of,
            "regime": _derive_regime(items),
            "items": items,
            "note": "Weekly COT snapshot; use as regime context, not intraday timing.",
        }
        _write_cache(payload)
        return payload
    except Exception as exc:
        logger.warning("COT summary unavailable: %s", exc)
        fallback = cache or {}
        fallback.setdefault("source", "CFTC COT (publicreporting.cftc.gov)")
        fallback["status"] = "unavailable"
        fallback.setdefault("fetched_at", datetime.utcnow().isoformat())
        fallback.setdefault("report_as_of", "")
        fallback.setdefault("regime", "Unknown")
        fallback.setdefault("items", [])
        fallback["note"] = "COT feed unavailable; retry on next run."
        return fallback
