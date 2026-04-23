"""Quick smoke-test — fetches live data and prints a summary (no email sent)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from investment_daily import (
    get_market_data, get_news, get_polymarket_data,
    analyze_sentiment, fact_check_articles, build_email,
)

print("=== Market Data ===")
md = get_market_data()
for cat, items in md.items():
    print(f"  {cat}:")
    for name, d in list(items.items())[:3]:
        print(f"    {name}: {d['price']:.4f}  ({d['pct_change']:+.2f}%)")

print("\n=== News ===")
arts = get_news()
print(f"  {len(arts)} articles collected")
for a in arts[:5]:
    print(f"  [{a['source']}] {a['title'][:90]}")

print("\n=== Polymarket ===")
poly = get_polymarket_data()
print(f"  {len(poly)} markets found")
for p in poly[:5]:
    print(f"  YES {p['probability']}% | {p['question'][:70]}")

print("\n=== Sentiment ===")
sent = analyze_sentiment(md)
print(f"  {sent['overall'].upper()}  (avg index change {sent['score']:+.2f}%)")
for d in sent["details"]:
    print(f"    {d}")

print("\n=== Fact-Check ===")
checked = fact_check_articles(arts, md, sent)
from collections import Counter
import sys
c = Counter(a["verdict"] if a["verdict"] else "N/A" for a in checked)
for verdict, count in sorted(c.items()):
    safe = verdict.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8")
    print(f"  {count:3d}x  {safe}")

print("\n=== Email HTML Build ===")
html = build_email(md, checked, poly, sent)
print(f"  HTML generated — {len(html):,} characters")

print("\nAll checks passed. Configure .env then run: python investment_daily.py")
