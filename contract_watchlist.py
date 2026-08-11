"""
Federal contract watchlist for contract_alerts.py.

Maps ticker -> list of lowercase substring patterns that match against the
USAspending.gov "Recipient Name" field. Patterns are intentionally generous
(subsidiary names, common legal-entity suffixes omitted) because federal
contracts are usually awarded to a subsidiary, not the parent holding co.

To add a new contractor, see docs/AGENT_GUIDE.md Recipe 11.
"""

from __future__ import annotations


from strategy_engine import SCAN_TICKERS

WATCHLIST: dict[str, list[str]] = {
    # ── Prime defense contractors ───────────────────────────────────────────
    "LMT":  ["lockheed martin", "sikorsky aircraft"],
    "RTX":  ["raytheon", "rtx corporation", "collins aerospace", "pratt & whitney"],
    "NOC":  ["northrop grumman"],
    "GD":   ["general dynamics", "gulfstream aerospace", "bath iron works",
             "electric boat"],
    "BA":   ["boeing"],
    "HII":  ["huntington ingalls", "newport news shipbuilding", "ingalls shipbuilding"],
    "TXT":  ["textron", "bell textron", "bell helicopter"],
    "TDG":  ["transdigm"],
    "HEI":  ["heico"],
    "CW":   ["curtiss-wright", "curtiss wright"],
    "AJRD": ["aerojet rocketdyne"],
    "AVAV": ["aerovironment"],
    "KTOS": ["kratos defense", "kratos unmanned"],
    "MRCY": ["mercury systems"],
    "BWXT": ["bwx technologies", "bwxt"],

    # ── Federal IT / services / systems integrators ─────────────────────────
    "LDOS": ["leidos"],
    "BAH":  ["booz allen"],
    "CACI": ["caci"],
    "SAIC": ["science applications international", "saic, inc",
             "saic incorporated"],
    "KBR":  ["kbr, inc", "kbr inc", "kellogg brown"],
    "MAXR": ["maxar"],
    "GDIT": ["general dynamics information technology", "gdit"],
    "ACN":  ["accenture federal", "accenture llp"],
    "HPE":  ["hewlett packard enterprise"],
    "DXC":  ["dxc technology"],
    "PLTR": ["palantir"],
    "ANET": ["arista networks"],
    "CSCO": ["cisco systems"],

    # ── Big tech with material government books ─────────────────────────────
    "MSFT": ["microsoft corporation"],
    "ORCL": ["oracle america", "oracle corporation"],
    "IBM":  ["international business machines"],
    "GOOGL": ["google llc", "alphabet inc"],
    "AMZN": ["amazon web services", "amazon.com services"],
    "NVDA": ["nvidia corporation"],
    "AMD":  ["advanced micro devices"],
    "CRWD": ["crowdstrike"],

    # ── Engineering / construction / energy services ────────────────────────
    "FLR":  ["fluor corporation", "fluor federal"],
    "J":    ["jacobs engineering", "jacobs solutions"],
    "PWR":  ["quanta services"],
    "EME":  ["emcor"],
    "EXP":  ["eagle materials"],

    # ── Healthcare with federal exposure (VA, HHS, DoD) ─────────────────────
    "HUM":  ["humana government business", "humana federal"],
    "UNH":  ["unitedhealth military", "optum public sector", "optumserve"],
    "MOH":  ["molina healthcare"],
    "DHR":  ["danaher", "beckman coulter", "cepheid"],
    "TMO":  ["thermo fisher"],
}

# Tickers that obviously cannot receive USD federal contracts. Excluded from
# the SCAN_TICKERS fallback so we don't waste API calls on them.
_NON_RECIPIENT_TICKERS: set[str] = {
    # Indices / commodities / crypto / 3x leveraged ETFs
    "SPY", "VOO", "QQQ", "IWM", "SMH", "ARKK", "XBI", "XLE", "XLK",
    "TQQQ", "UPRO", "SOXL",
    "GC=F", "CL=F",
}


def _is_crypto_or_future(symbol: str) -> bool:
    return symbol.endswith("-USD") or "=" in symbol


def _company_name_pattern(name: str) -> str:
    """Convert a SCAN_TICKERS display name into a USAspending search pattern."""
    base = name.lower()
    # Strip parenthetical disambiguation, e.g. "Tech (XLK)" -> "tech"
    if "(" in base:
        base = base.split("(", 1)[0]
    return base.strip()


def resolve_watchlist() -> dict[str, list[str]]:
    """Return the effective watchlist: curated WATCHLIST + SCAN_TICKERS fallback.

    Tickers present in WATCHLIST keep their curated patterns. Tickers in
    SCAN_TICKERS but not in WATCHLIST get their company name as the sole
    fallback pattern. Crypto / futures / ETFs / indices are skipped.
    """
    resolved: dict[str, list[str]] = {}

    for ticker, patterns in WATCHLIST.items():
        resolved[ticker] = list(patterns)

    for ticker, name in SCAN_TICKERS.items():
        if ticker in resolved:
            continue
        if ticker in _NON_RECIPIENT_TICKERS:
            continue
        if _is_crypto_or_future(ticker):
            continue
        pattern = _company_name_pattern(name)
        if not pattern:
            continue
        resolved[ticker] = [pattern]

    return resolved


def match_ticker(recipient_name: str, resolved: dict[str, list[str]]) -> str | None:
    """Return the ticker whose patterns match the recipient name, or None.

    Case-insensitive substring match. If a recipient matches multiple tickers
    (rare in practice), the first one with the longest matching pattern wins.
    """
    if not recipient_name:
        return None
    lowered = recipient_name.lower()
    best_ticker: str | None = None
    best_len = 0
    for ticker, patterns in resolved.items():
        for pat in patterns:
            if pat and pat in lowered and len(pat) > best_len:
                best_ticker = ticker
                best_len = len(pat)
    return best_ticker
