#!/usr/bin/env python3
"""
Investment Daily Newsletter
Fetches investment news, real market data, and Polymarket predictions,
fact-checks claims against live data, then emails a formatted report.
"""

import os
import json
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import yfinance as yf
import feedparser
import requests
from dotenv import load_dotenv

from strategy_engine import methodology_newsletter_html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIR, "logs", "investment_daily.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────

EMAIL_SENDER    = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")   # Gmail App Password
EMAIL_RECIPIENT = "dan.r.custodio@gmail.com"

RSS_FEEDS = [
    ("Reuters Business",   "https://feeds.reuters.com/reuters/businessNews"),
    ("CNBC Markets",       "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("MarketWatch",        "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ("Yahoo Finance",      "https://finance.yahoo.com/news/rssindex"),
    ("Seeking Alpha",      "https://seekingalpha.com/market_currents.xml"),
    ("Investing.com",      "https://www.investing.com/rss/news.rss"),
    ("Barron's",           "https://www.barrons.com/xml/rss/3_7515.xml"),
    ("Financial Times",    "https://www.ft.com/rss/home"),
    ("WSJ Markets",        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
]

MARKET_TICKERS: dict[str, dict[str, str]] = {
    "Major Indices": {
        "^GSPC":    "S&P 500",
        "^IXIC":    "NASDAQ",
        "^DJI":     "Dow Jones",
        "^RUT":     "Russell 2000",
        "^VIX":     "VIX (Fear Index)",
    },
    "Sector ETFs": {
        "XLK": "Tech (XLK)",
        "XLF": "Financials (XLF)",
        "XLE": "Energy (XLE)",
        "XLV": "Healthcare (XLV)",
        "XLI": "Industrials (XLI)",
        "XLY": "Consumer Disc. (XLY)",
    },
    "Commodities": {
        "GC=F":  "Gold",
        "CL=F":  "Crude Oil",
        "SI=F":  "Silver",
        "NG=F":  "Natural Gas",
    },
    "Crypto": {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana",
    },
    "Bonds & Rates": {
        "^TNX": "10-Year Treasury Yield",
        "^TYX": "30-Year Treasury Yield",
        "^IRX": "3-Month T-Bill",
    },
    "Currency": {
        "DX-Y.NYB": "US Dollar Index",
        "EURUSD=X": "EUR/USD",
        "JPYUSD=X": "JPY/USD",
        "GBPUSD=X": "GBP/USD",
    },
}

# Maps keywords in headlines → yfinance symbol for fact-checking
KEYWORD_TO_SYMBOL: dict[str, str] = {
    "nasdaq":       "^IXIC",
    "s&p":          "^GSPC",
    "s&p 500":      "^GSPC",
    "dow":          "^DJI",
    "dow jones":    "^DJI",
    "russell":      "^RUT",
    "vix":          "^VIX",
    "tech":         "XLK",
    "technology":   "XLK",
    "financials":   "XLF",
    "banks":        "XLF",
    "energy":       "XLE",
    "healthcare":   "XLV",
    "gold":         "GC=F",
    "oil":          "CL=F",
    "crude":        "CL=F",
    "bitcoin":      "BTC-USD",
    "btc":          "BTC-USD",
    "ethereum":     "ETH-USD",
    "eth":          "ETH-USD",
    "solana":       "SOL-USD",
    "treasury":     "^TNX",
    "bonds":        "^TNX",
    "dollar":       "DX-Y.NYB",
    "eur":          "EURUSD=X",
    "euro":         "EURUSD=X",
    "yen":          "JPYUSD=X",
}

BULLISH_WORDS = [
    "rally", "surge", "soar", "jump", "rise", "gain", "boom", "record high",
    "bullish", "optimism", "upbeat", "boost", "uptick", "climb", "rebound",
    "recover", "green", "up ", "higher", "strong",
]
BEARISH_WORDS = [
    "fall", "drop", "plunge", "decline", "slump", "crash", "sell-off",
    "bearish", "recession", "fear", "worry", "concern", "downturn", "tumble",
    "sink", "red ", "lower", "weak", "loss", "correction",
]

# ─── Market Data ─────────────────────────────────────────────────────────────

def get_market_data() -> dict[str, dict[str, Any]]:
    """Pull daily OHLCV for all tracked tickers and compute day-over-day change."""
    result: dict[str, dict[str, Any]] = {}

    # Try Schwab batch quotes first for supported symbols
    schwab_quotes: dict[str, dict[str, Any]] = {}
    try:
        import schwab_client
        all_symbols = [s for tickers in MARKET_TICKERS.values() for s in tickers]
        sq = schwab_client.get_quotes(all_symbols)
        if sq:
            schwab_quotes = sq
            logger.info(f"Schwab: pre-fetched {len(schwab_quotes)} quotes for market snapshot")
    except Exception as exc:
        logger.debug(f"Schwab quotes unavailable: {exc}")

    for category, tickers in MARKET_TICKERS.items():
        result[category] = {}
        for symbol, name in tickers.items():
            # Use Schwab data if available for this symbol
            if symbol in schwab_quotes:
                sq = schwab_quotes[symbol]
                result[category][name] = {
                    "symbol":     symbol,
                    "price":      sq["price"],
                    "change":     sq["change"],
                    "pct_change": sq["pct_change"],
                }
                continue

            # Fall back to yfinance
            try:
                hist = yf.Ticker(symbol).history(period="5d")
                if hist.empty:
                    continue
                closes = hist["Close"].dropna()
                if len(closes) >= 2:
                    prev  = float(closes.iloc[-2])
                    curr  = float(closes.iloc[-1])
                    delta = curr - prev
                    pct   = (delta / prev) * 100
                else:
                    curr  = float(closes.iloc[-1])
                    delta = 0.0
                    pct   = 0.0

                result[category][name] = {
                    "symbol":     symbol,
                    "price":      curr,
                    "change":     delta,
                    "pct_change": pct,
                }
            except Exception as exc:
                logger.warning(f"Could not fetch {symbol}: {exc}")

    return result


def flat_symbol_lookup(market_data: dict) -> dict[str, dict]:
    """Build a flat {symbol: data} dict for quick fact-check lookups."""
    lookup: dict[str, dict] = {}
    for cat_data in market_data.values():
        for _name, data in cat_data.items():
            sym = data.get("symbol", "")
            lookup[sym] = data
    return lookup

# ─── News ─────────────────────────────────────────────────────────────────────

def get_news(hours: int = 24) -> list[dict]:
    """Fetch and deduplicate articles from all RSS feeds published within `hours`."""
    cutoff   = datetime.utcnow() - timedelta(hours=hours)
    articles: list[dict] = []
    seen     = set()

    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title = getattr(entry, "title", "").strip()
                if not title or title in seen:
                    continue
                seen.add(title)

                pub: datetime | None = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        pub = datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass

                if pub and pub < cutoff:
                    continue

                summary = getattr(entry, "summary", "") or ""
                # Strip basic HTML tags from summary
                import re
                summary = re.sub(r"<[^>]+>", "", summary).strip()[:400]

                articles.append({
                    "source":  source,
                    "title":   title,
                    "summary": summary,
                    "link":    getattr(entry, "link", "#"),
                    "date":    pub,
                })
        except Exception as exc:
            logger.warning(f"RSS error ({source}): {exc}")

    articles.sort(key=lambda x: x["date"] or datetime.min, reverse=True)
    return articles[:35]

# ─── Polymarket ───────────────────────────────────────────────────────────────

def get_polymarket_data() -> list[dict]:
    """
    Pull active financial/economic prediction markets from the Polymarket Gamma API.
    Fetches a broad set and filters client-side for finance-relevant topics.
    """
    FINANCE_KEYWORDS = [
        "fed", "federal reserve", "interest rate", "inflation", "cpi", "gdp",
        "recession", "unemployment", "tariff", "trade", "treasury", "debt",
        "bitcoin", "btc", "ethereum", "crypto", "stock", "s&p", "nasdaq", "dow",
        "oil", "gold", "dollar", "euro", "yen", "economy", "economic", "market",
        "bank", "fiscal", "deficit", "bond", "yield", "rate cut", "rate hike",
        "powell", "trump", "congress", "budget", "tax", "ipo",
    ]

    markets: list[dict] = []
    seen_ids: set = set()
    headers = {"User-Agent": "InvestmentDaily/1.0"}

    # Pull a large batch sorted by volume, then filter for financial topics
    endpoints = [
        "https://gamma-api.polymarket.com/markets?limit=100&active=true&order=volume&ascending=false",
        "https://gamma-api.polymarket.com/markets?limit=100&active=true&tag=crypto&order=volume&ascending=false",
        "https://gamma-api.polymarket.com/markets?limit=100&active=true&tag=economics&order=volume&ascending=false",
    ]

    for url in endpoints:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue
            data = resp.json()
            if not isinstance(data, list):
                continue

            for m in data:
                mid = m.get("id", "")
                if not mid or mid in seen_ids:
                    continue

                question = (m.get("question", "") or "").lower()
                # Only include finance/economy-relevant markets
                if not any(kw in question for kw in FINANCE_KEYWORDS):
                    continue

                seen_ids.add(mid)

                prob: float | None = None
                try:
                    prices = json.loads(m.get("outcomePrices", "[]") or "[]")
                    if prices:
                        prob = round(float(prices[0]) * 100, 1)
                except Exception:
                    pass

                try:
                    vol = float(m.get("volume", 0) or 0)
                except Exception:
                    vol = 0.0

                end_raw = m.get("endDate", "") or ""
                end_str = ""
                if end_raw:
                    try:
                        end_str = datetime.fromisoformat(end_raw[:10]).strftime("%b %d, %Y")
                    except Exception:
                        end_str = end_raw[:10]

                markets.append({
                    "question":    m.get("question", ""),
                    "probability": prob,
                    "volume":      vol,
                    "end_date":    end_str,
                    "url": f"https://polymarket.com/event/{m.get('slug', '')}",
                })
        except Exception as exc:
            logger.warning(f"Polymarket endpoint error: {exc}")

    markets.sort(key=lambda x: x["volume"], reverse=True)
    return markets[:15]

# ─── Sentiment & Fact-Checking ────────────────────────────────────────────────

def analyze_sentiment(market_data: dict) -> dict:
    """Derive overall market sentiment from index performance."""
    scores: list[float] = []
    details: list[str]  = []

    indices = market_data.get("Major Indices", {})
    for name, data in indices.items():
        if name == "VIX (Fear Index)":
            continue
        pct = data.get("pct_change", 0.0)
        scores.append(pct)
        if pct >= 0.5:
            details.append(f"{name} +{pct:.2f}%")
        elif pct <= -0.5:
            details.append(f"{name} {pct:.2f}%")
        else:
            details.append(f"{name} flat ({pct:+.2f}%)")

    avg = sum(scores) / len(scores) if scores else 0.0
    overall = "bullish" if avg > 0.25 else ("bearish" if avg < -0.25 else "neutral")

    return {"overall": overall, "score": avg, "details": details}


def fact_check_articles(
    articles: list[dict],
    market_data: dict,
    sentiment: dict,
) -> list[dict]:
    """
    For each article, determine if its directional claim (bullish/bearish) is
    consistent with same-day market data for the referenced asset.
    """
    sym_lookup = flat_symbol_lookup(market_data)

    checked: list[dict] = []
    for art in articles:
        title_lc = art["title"].lower()

        is_bullish = any(w in title_lc for w in BULLISH_WORDS)
        is_bearish = any(w in title_lc for w in BEARISH_WORDS)

        # Try to find a related market ticker
        matched_sym: str | None   = None
        matched_pct: float | None = None
        for kw, sym in KEYWORD_TO_SYMBOL.items():
            if kw in title_lc and sym in sym_lookup:
                matched_sym = sym
                matched_pct = sym_lookup[sym].get("pct_change")
                break

        # Fact-check result
        verdict = detail = ""

        if matched_pct is not None:
            if is_bullish:
                if matched_pct > 0.1:
                    verdict = "✅ CONFIRMED"
                    detail  = f"{matched_sym} is up {matched_pct:+.2f}% today — supports bullish headline."
                elif matched_pct < -0.5:
                    verdict = "❌ CONTRADICTED"
                    detail  = f"{matched_sym} is down {matched_pct:.2f}% today — contradicts bullish claim."
                else:
                    verdict = "⚠️ MIXED"
                    detail  = f"{matched_sym} moved only {matched_pct:+.2f}% — claim is overstated."
            elif is_bearish:
                if matched_pct < -0.1:
                    verdict = "✅ CONFIRMED"
                    detail  = f"{matched_sym} is down {matched_pct:.2f}% today — supports bearish headline."
                elif matched_pct > 0.5:
                    verdict = "❌ CONTRADICTED"
                    detail  = f"{matched_sym} is up {matched_pct:+.2f}% today — contradicts bearish claim."
                else:
                    verdict = "⚠️ MIXED"
                    detail  = f"{matched_sym} moved only {matched_pct:+.2f}% — claim may be overstated."
            else:
                verdict = "➡️ NEUTRAL"
                detail  = f"No directional claim; {matched_sym} at {matched_pct:+.2f}% for context."
        elif is_bullish or is_bearish:
            direction = "bullish" if is_bullish else "bearish"
            if (direction == "bullish") == (sentiment["overall"] == "bearish"):
                verdict = "⚠️ MIXED SIGNALS"
                detail  = f"Overall market is {sentiment['overall']} today, but no direct data for this asset."
            else:
                verdict = "➡️ UNVERIFIED"
                detail  = "Directional claim found but no matching market data available."
        else:
            verdict = "ℹ️ N/A"
            detail  = "No directional market claim to check."

        checked.append({**art, "verdict": verdict, "verdict_detail": detail})

    return checked

# ─── Email Builder ────────────────────────────────────────────────────────────

def _pct_color(pct: float) -> str:
    return "#22c55e" if pct >= 0 else "#ef4444"

def _price_fmt(price: float, symbol: str) -> str:
    if "=X" in symbol or symbol in ("DX-Y.NYB",):
        return f"{price:.4f}"
    if price > 1000:
        return f"${price:,.2f}"
    if price > 1:
        return f"${price:.2f}"
    return f"${price:.6f}"


def build_market_rows(market_data: dict) -> str:
    rows = ""
    for category, tickers in market_data.items():
        if not tickers:
            continue
        rows += (
            f'<tr><td colspan="4" style="background:#1e293b;color:#94a3b8;'
            f'font-size:11px;font-weight:700;letter-spacing:1px;padding:6px 14px;'
            f'text-transform:uppercase">{category}</td></tr>'
        )
        for name, data in tickers.items():
            pct    = data.get("pct_change", 0.0)
            price  = data.get("price", 0.0)
            change = data.get("change", 0.0)
            symbol = data.get("symbol", "")
            color  = _pct_color(pct)
            arrow  = "▲" if pct >= 0 else "▼"
            chg_s  = f"+{change:.2f}" if change >= 0 else f"{change:.2f}"
            rows += (
                f'<tr style="border-bottom:1px solid #0f172a">'
                f'<td style="padding:8px 14px;color:#e2e8f0;font-weight:500">{name}</td>'
                f'<td style="padding:8px 14px;color:#e2e8f0;text-align:right">{_price_fmt(price, symbol)}</td>'
                f'<td style="padding:8px 14px;color:{color};text-align:right">{chg_s}</td>'
                f'<td style="padding:8px 14px;color:{color};text-align:right;font-weight:700">'
                f'{arrow} {abs(pct):.2f}%</td></tr>'
            )
    return rows


def build_news_html(articles: list[dict]) -> str:
    html = ""
    for art in articles[:22]:
        verdict = art.get("verdict", "")
        detail  = art.get("verdict_detail", "")

        if "CONFIRMED" in verdict:
            vbg, vc = "#0f2d1f", "#4ade80"
        elif "CONTRADICTED" in verdict:
            vbg, vc = "#2d0f0f", "#f87171"
        elif "MIXED" in verdict:
            vbg, vc = "#2d1a0f", "#fb923c"
        else:
            vbg, vc = "#1e293b", "#94a3b8"

        date_s = art["date"].strftime("%I:%M %p UTC") if art.get("date") else ""
        link   = art.get("link") or "#"

        summary_block = (
            f'<p style="color:#94a3b8;font-size:13px;margin:8px 0 10px;line-height:1.6">'
            f'{art["summary"]}</p>'
        ) if art.get("summary") else '<div style="margin-bottom:10px"></div>'

        verdict_block = (
            f'<div style="background:{vbg};padding:7px 14px;border-top:1px solid #0f172a">'
            f'<span style="font-size:11px;color:{vc};font-weight:700">{verdict}</span>'
            f'<span style="font-size:11px;color:#64748b;margin-left:8px">{detail}</span></div>'
        ) if verdict else ""

        read_more = (
            f'<a href="{link}" target="_blank" rel="noopener"'
            f' style="display:inline-block;background:#1e293b;color:#818cf8;'
            f'font-size:11px;font-weight:700;padding:5px 12px;border-radius:20px;'
            f'text-decoration:none;letter-spacing:0.5px;border:1px solid #334155;'
            f'transition:background 0.2s">'
            f'Read Full Article &#8594;</a>'
        ) if link and link != "#" else ""

        html += f"""
        <div style="margin-bottom:14px;background:#0f172a;border-radius:8px;
                    overflow:hidden;border:1px solid #1e293b">
          <div style="padding:14px 16px">
            <div style="margin-bottom:6px;display:flex;justify-content:space-between">
              <span style="font-size:11px;color:#818cf8;font-weight:700;
                           text-transform:uppercase">{art.get('source','')}</span>
              <span style="font-size:11px;color:#475569">{date_s}</span>
            </div>
            <a href="{link}" target="_blank" rel="noopener"
               style="color:#e2e8f0;font-size:15px;font-weight:600;
                      text-decoration:none;line-height:1.4;display:block;margin-bottom:4px">
              {art.get('title','')}
            </a>
            {summary_block}
            {read_more}
          </div>
          {verdict_block}
        </div>"""
    return html


def build_polymarket_html(markets: list[dict]) -> str:
    html = ""
    for m in markets:
        prob = m.get("probability")
        if prob is not None:
            pc = "#22c55e" if prob > 60 else ("#ef4444" if prob < 40 else "#f59e0b")
            ps = f"{prob:.1f}%"
        else:
            pc, ps = "#94a3b8", "N/A"

        try:
            vol_s = f"${float(m.get('volume', 0)):,.0f}"
        except Exception:
            vol_s = "N/A"

        end_s = f" · Resolves {m['end_date']}" if m.get("end_date") else ""

        html += f"""
        <div style="margin-bottom:12px;background:#0f172a;border-radius:8px;
                    padding:13px 16px;border:1px solid #1e293b">
          <a href="{m.get('url','#')}"
             style="color:#e2e8f0;font-size:14px;font-weight:500;
                    text-decoration:none;line-height:1.4">{m.get('question','')}</a>
          <div style="margin-top:9px;display:flex;
                      justify-content:space-between;align-items:center">
            <span style="font-size:12px;color:#64748b">
              Volume: {vol_s}{end_s}
            </span>
            <span style="font-size:18px;font-weight:800;color:{pc}">
              YES {ps}
            </span>
          </div>
        </div>"""
    return html


def build_strategy_section(signals: list[dict]) -> str:
    """Compact strategy signals table for the daily newsletter."""
    from strategy_engine import (
        confidence_breakdown,
        group_signals_primary_secondary,
        holdout_backtest_score,
        strategy_learn_link,
    )
    if not signals:
        return ""

    groups = group_signals_primary_secondary(signals)[:24]

    rows = ""
    for g in groups:
        s         = g["primary"]
        sec       = g.get("secondary")
        direction = s["direction"]
        is_bull   = direction == "BULLISH"
        dc        = "#22c55e" if is_bull else "#ef4444"
        arrow     = "&#9650;" if is_bull else "&#9660;"
        conf      = s.get("confidence", 0)
        cc        = "#22c55e" if conf >= 65 else ("#f59e0b" if conf >= 52 else "#94a3b8")
        bt        = s.get("backtest", {})
        d5        = bt.get("5d", {})
        wr_s      = f"{d5['win_rate']}% ({d5['avg_return']:+.1f}%)" if d5 else "N/A"
        wr_c      = "#22c55e" if d5 and d5["avg_return"] > 0 else "#ef4444"
        learn     = strategy_learn_link(s["strategy"], style="badge")
        n_line    = ""
        if d5 and d5.get("count") is not None:
            n_line = (
                f'<div style="font-size:10px;color:#64748b;margin-top:4px">'
                f'n={d5["count"]} fills (5d fwd)</div>'
            )

        bd          = confidence_breakdown(bt)
        bd_line     = ""
        if bd:
            wr20_bit = f'{bd["wr20_pts"]}' if bd["has_20d"] else "0"
            bd_line = (
                f'<div style="font-size:9px;color:#64748b;line-height:1.45;margin-top:5px;'
                f'max-width:178px;margin-left:auto;text-align:right">'
                f'Pts: 5dWR {bd["wr5_pts"]} + Sh {bd["sharpe_pts"]} + '
                f'20dWR {wr20_bit} + PF {bd["pf_pts"]}'
                f'</div>'
            )

        ho_sc, ho_n = holdout_backtest_score(bt)
        ho_line       = ""
        if ho_sc is not None and ho_n:
            hcc = "#22c55e" if ho_sc >= 65 else ("#f59e0b" if ho_sc >= 52 else "#94a3b8")
            ho_line = (
                f'<div style="font-size:10px;color:#475569;margin-top:6px;line-height:1.35">'
                f'Recent slice: <span style="color:{hcc};font-weight:800">{ho_sc:.0f}</span> '
                f'(n={ho_n})</div>'
            )

        agree_html = ""
        if g.get("agreement_count", 1) > 1:
            agree_html = (
                f'<div style="font-size:10px;color:#a78bfa;margin-top:4px;font-weight:600">'
                f'{g["agreement_count"]} rules · same direction</div>'
            )
        reg_html = (
            f'<div style="font-size:10px;color:#475569;margin-top:3px">{s.get("regime", "—")}</div>'
        )

        runner_html = ""
        if sec:
            s_conf = sec.get("confidence", 0)
            s_cc   = "#22c55e" if s_conf >= 65 else ("#f59e0b" if s_conf >= 52 else "#94a3b8")
            run_ln = strategy_learn_link(sec["strategy"], style="badge")
            runner_html = (
                f'<div style="margin-top:8px;padding-top:8px;border-top:1px solid #1e293b">'
                f'<div style="color:#64748b;font-size:10px;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px">'
                f'Runner-up (same direction)</div>'
                f'<div style="color:#94a3b8;font-size:11px;margin-bottom:4px">{sec["strategy"]}</div>'
                f'<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap">'
                f'<span style="font-size:13px;font-weight:800;color:{s_cc}">{s_conf:.0f}</span>'
                f'<span style="font-size:10px;color:#475569">score</span>'
                f'{run_ln}</div></div>'
            )

        rows += (
            f'<tr style="border-bottom:1px solid #0f172a">'
            f'<td style="padding:8px 12px;color:{dc};font-size:15px;font-weight:900;vertical-align:top">{arrow}</td>'
            f'<td style="padding:8px 12px;vertical-align:top">'
            f'  <div style="color:#e2e8f0;font-size:13px;font-weight:700">{s["ticker"]}</div>'
            f'  <div style="color:#64748b;font-size:11px">{s["name"]}</div>'
            f'  {reg_html}'
            f'  {agree_html}'
            f'</td>'
            f'<td style="padding:8px 12px;vertical-align:top">'
            f'  <div style="color:#cbd5e1;font-size:11px;font-weight:700;margin-bottom:4px">Top rule</div>'
            f'  <div style="color:#94a3b8;font-size:12px;margin-bottom:4px">{s["strategy"]}</div>'
            f'  {learn}'
            f'  {runner_html}'
            f'</td>'
            f'<td style="padding:8px 12px;text-align:right;vertical-align:top">'
            f'  <div style="font-size:13px;color:{wr_c};font-weight:700">{wr_s}</div>'
            f'  <div style="font-size:10px;color:#475569">5-day win | avg</div>'
            f'  {n_line}'
            f'</td>'
            f'<td style="padding:8px 12px;text-align:right;vertical-align:top">'
            f'  <div style="font-size:16px;font-weight:900;color:{cc}">{conf:.0f}</div>'
            f'  <div style="font-size:10px;color:#475569">backtest score</div>'
            f'  {bd_line}'
            f'  {ho_line}'
            f'</td>'
            f'</tr>'
        )

    bullish_n  = sum(1 for s in signals if s["direction"] == "BULLISH")
    bearish_n  = sum(1 for s in signals if s["direction"] == "BEARISH")

    return f"""
    <div style="background:#0f172a;border-radius:10px;overflow:hidden;
                margin-bottom:20px;border:1px solid #1e293b">
      <div style="background:linear-gradient(90deg,#1e1b4b,#0f172a);padding:14px 16px;
                  border-bottom:1px solid #1e293b">
        <h2 style="color:#f1f5f9;margin:0 0 2px;font-size:16px;font-weight:700">
          Strategy Signals Today
        </h2>
        <div style="font-size:12px;color:#64748b">
          {bullish_n} bullish &nbsp;·&nbsp; {bearish_n} bearish rule hits &nbsp;·&nbsp;
          Rows group by asset &amp; direction (top rule + runner-up) &nbsp;·&nbsp;
          <span style="color:#818cf8">Intraday alerts sent automatically when these fire</span>
        </div>
      </div>
      <table style="width:100%;border-collapse:collapse">
        <tr style="background:#0a0f1e">
          <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:left;
                     font-weight:600;text-transform:uppercase"></th>
          <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:left;
                     font-weight:600;text-transform:uppercase">Asset</th>
          <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:left;
                     font-weight:600;text-transform:uppercase">Strategy</th>
          <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:right;
                     font-weight:600;text-transform:uppercase">5-Day History</th>
          <th style="padding:6px 12px;color:#475569;font-size:10px;text-align:right;
                     font-weight:600;text-transform:uppercase">Score</th>
        </tr>
        {rows}
      </table>
      <div style="padding:10px 14px;border-top:1px solid #1e293b">
        <p style="color:#475569;font-size:11px;margin:0;line-height:1.55">
          <strong style="color:#64748b">Backtest score</strong> measures how this <em>rule</em> behaved
          in history (weighted 5d/20d win rates, Sharpe, profit factor)—not tomorrow&apos;s probability.
          <strong>Pts</strong> show how those pieces add up; <strong>n</strong> is trade count in the 5d stats.
          <strong>Recent slice</strong> recomputes the same score on only the latest 20% of signal dates (time-ordered)
          as a rough out-of-sample check. <strong>Regime</strong> is price vs a long MA for context.
          Runner-up = next-best rule when several align. Not financial advice.
        </p>
      </div>
    </div>"""


def build_email(
    market_data: dict,
    articles: list[dict],
    polymarket: list[dict],
    sentiment: dict,
    strategy_signals: list[dict] | None = None,
) -> str:
    today  = datetime.now().strftime("%A, %B %d, %Y")
    sc_map = {"bullish": "#22c55e", "bearish": "#ef4444", "neutral": "#f59e0b"}
    sb_map = {"bullish": "#f0fdf4", "bearish": "#fef2f2", "neutral": "#fffbeb"}
    sc     = sc_map.get(sentiment["overall"], "#f59e0b")
    sb     = sb_map.get(sentiment["overall"], "#fffbeb")

    confirmed    = sum(1 for a in articles if "CONFIRMED"    in a.get("verdict", ""))
    contradicted = sum(1 for a in articles if "CONTRADICTED" in a.get("verdict", ""))
    mixed        = sum(1 for a in articles if "MIXED"        in a.get("verdict", ""))
    unverified   = len(articles) - confirmed - contradicted - mixed

    market_rows  = build_market_rows(market_data)
    news_html    = build_news_html(articles)
    poly_html    = build_polymarket_html(polymarket)
    detail_str   = " &nbsp;·&nbsp; ".join(sentiment["details"][:4])
    method_html    = methodology_newsletter_html()

    poly_section = f"""
    <div style="margin-bottom:24px">
      <h2 style="color:#f1f5f9;margin:0 0 6px;font-size:18px;font-weight:700">
        🎯 Polymarket — Prediction Markets
      </h2>
      <p style="color:#64748b;font-size:12px;margin:0 0 14px">
        Real-money prediction markets. Probability = crowd's best estimate.
        High volume = stronger signal.
      </p>
      {poly_html}
    </div>""" if poly_html else ""

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Investment Daily — {today}</title>
</head>
<body style="margin:0;padding:0;background:#020617;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif">
<div style="max-width:700px;margin:0 auto;padding:24px 16px">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#1e3a5f 0%,#1e1b4b 100%);
              border-radius:14px;padding:30px 28px;margin-bottom:20px;text-align:center">
    <div style="font-size:11px;color:#818cf8;letter-spacing:3px;
                text-transform:uppercase;font-weight:700;margin-bottom:10px">
      ⚡ Investment Daily
    </div>
    <h1 style="color:#f1f5f9;margin:0 0 10px;font-size:26px;font-weight:800">
      {today}
    </h1>
    <p style="color:#94a3b8;font-size:13px;margin:0">
      Live market data · RSS news from 9 sources · Polymarket predictions · Fact-checked
    </p>
  </div>

  <!-- Sentiment Banner -->
  <div style="background:{sb};border:2px solid {sc}40;border-radius:10px;
              padding:16px;margin-bottom:20px;text-align:center">
    <div style="font-size:11px;color:{sc};font-weight:700;
                letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">
      Overall Market Sentiment
    </div>
    <div style="font-size:28px;font-weight:900;color:{sc};text-transform:uppercase;
                letter-spacing:1px">
      {sentiment['overall']}
    </div>
    <div style="font-size:12px;color:#64748b;margin-top:8px">{detail_str}</div>
  </div>

  <!-- Market Data Table -->
  <div style="background:#0f172a;border-radius:10px;overflow:hidden;
              margin-bottom:20px;border:1px solid #1e293b">
    <div style="background:#1e293b;padding:14px 16px">
      <h2 style="color:#f1f5f9;margin:0;font-size:16px;font-weight:700">
        📊 Live Market Snapshot
      </h2>
    </div>
    <table style="width:100%;border-collapse:collapse">
      <tr style="background:#0a0f1e">
        <th style="padding:8px 14px;color:#475569;font-size:11px;text-align:left;
                   font-weight:600;text-transform:uppercase">Asset</th>
        <th style="padding:8px 14px;color:#475569;font-size:11px;text-align:right;
                   font-weight:600;text-transform:uppercase">Price</th>
        <th style="padding:8px 14px;color:#475569;font-size:11px;text-align:right;
                   font-weight:600;text-transform:uppercase">Chg</th>
        <th style="padding:8px 14px;color:#475569;font-size:11px;text-align:right;
                   font-weight:600;text-transform:uppercase">%</th>
      </tr>
      {market_rows}
    </table>
  </div>

  <!-- Fact-Check Summary -->
  <div style="background:#0f172a;border-radius:10px;padding:18px;
              margin-bottom:20px;border:1px solid #1e293b">
    <h2 style="color:#f1f5f9;margin:0 0 14px;font-size:16px;font-weight:700">
      🔍 Today's Fact-Check Results
    </h2>
    <table style="width:100%;border-collapse:collapse">
      <tr>
        <td style="padding:4px 8px 4px 0;width:25%">
          <div style="background:#0f2d1f;border-radius:8px;padding:12px;text-align:center">
            <div style="font-size:26px;font-weight:900;color:#22c55e">{confirmed}</div>
            <div style="font-size:10px;color:#4ade80;font-weight:700;letter-spacing:1px">
              CONFIRMED
            </div>
          </div>
        </td>
        <td style="padding:4px 4px;width:25%">
          <div style="background:#2d0f0f;border-radius:8px;padding:12px;text-align:center">
            <div style="font-size:26px;font-weight:900;color:#f87171">{contradicted}</div>
            <div style="font-size:10px;color:#fca5a5;font-weight:700;letter-spacing:1px">
              CONTRADICTED
            </div>
          </div>
        </td>
        <td style="padding:4px 4px;width:25%">
          <div style="background:#2d1a0f;border-radius:8px;padding:12px;text-align:center">
            <div style="font-size:26px;font-weight:900;color:#fb923c">{mixed}</div>
            <div style="font-size:10px;color:#fdba74;font-weight:700;letter-spacing:1px">
              MIXED/OVERSTATED
            </div>
          </div>
        </td>
        <td style="padding:4px 0 4px 4px;width:25%">
          <div style="background:#1e293b;border-radius:8px;padding:12px;text-align:center">
            <div style="font-size:26px;font-weight:900;color:#94a3b8">{unverified}</div>
            <div style="font-size:10px;color:#64748b;font-weight:700;letter-spacing:1px">
              UNVERIFIED
            </div>
          </div>
        </td>
      </tr>
    </table>
    <p style="font-size:11px;color:#475569;margin:12px 0 0;line-height:1.5">
      Each news headline is cross-referenced against same-day price movement
      of the referenced asset. "Contradicted" means the headline's direction
      claim is opposite to what the market actually did today.
    </p>
  </div>

  {method_html}

  <!-- Strategy Signals -->
  {build_strategy_section(strategy_signals or [])}

  <!-- News -->
  <div style="margin-bottom:24px">
    <h2 style="color:#f1f5f9;margin:0 0 14px;font-size:18px;font-weight:700">
      📰 Top Investment News
    </h2>
    {news_html}
  </div>

  {poly_section}

  <!-- Footer -->
  <div style="text-align:center;padding:20px 0 8px;color:#475569;font-size:11px;
              border-top:1px solid #1e293b">
    <p style="margin:0 0 4px;font-weight:600;color:#64748b">Investment Daily</p>
    <p style="margin:0 0 4px">
      Market data: Yahoo Finance · News: Reuters, CNBC, MarketWatch, WSJ & more
      · Predictions: Polymarket
    </p>
    <p style="margin:10px 0 0;color:#374151;font-size:12px;
              background:#111827;border-radius:6px;padding:10px">
      ⚠️ <strong style="color:#6b7280">Disclaimer:</strong>
      This newsletter is for informational purposes only and is
      <strong>not financial advice</strong>. Always do your own research.
    </p>
  </div>

</div>
</body></html>"""

# ─── Email Sender ─────────────────────────────────────────────────────────────

def send_email(html: str, subject: str) -> None:
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        raise ValueError(
            "EMAIL_SENDER and EMAIL_PASSWORD must be set in the .env file."
        )

    msg              = MIMEMultipart("alternative")
    msg["Subject"]   = subject
    msg["From"]      = EMAIL_SENDER
    msg["To"]        = EMAIL_RECIPIENT
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

    logger.info(f"Email delivered → {EMAIL_RECIPIENT}")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    from strategy_engine import run_full_scan

    logger.info("=== Investment Daily starting ===")

    logger.info("Fetching market data ...")
    market_data = get_market_data()

    logger.info("Fetching news ...")
    articles = get_news()
    logger.info(f"  {len(articles)} articles collected")

    logger.info("Fetching Polymarket data ...")
    polymarket = get_polymarket_data()
    logger.info(f"  {len(polymarket)} markets found")

    logger.info("Running strategy scan (this may take ~2 min) ...")
    try:
        strategy_signals = run_full_scan()
        logger.info(f"  {len(strategy_signals)} strategy signals found")
    except Exception as exc:
        logger.warning(f"  Strategy scan failed: {exc} — continuing without signals")
        strategy_signals = []

    sentiment = analyze_sentiment(market_data)
    logger.info(f"  Sentiment: {sentiment['overall']} ({sentiment['score']:+.2f}%)")

    articles = fact_check_articles(articles, market_data, sentiment)

    html    = build_email(market_data, articles, polymarket, sentiment, strategy_signals)
    emoji   = {"bullish": "UP", "bearish": "DOWN", "neutral": "FLAT"}.get(sentiment["overall"], "")
    today   = datetime.now().strftime("%b %d, %Y")
    subject = (
        f"Investment Daily -- {today} | Market {emoji} "
        f"| {len(strategy_signals)} Strategy Signals"
    )

    logger.info("Sending email ...")
    send_email(html, subject)

    logger.info("=== Done ===")


if __name__ == "__main__":
    main()
