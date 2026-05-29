"""
One-time (or occasional) Schwab OAuth login. Writes schwab_token.json in the project root.

Requires in .env:
  SCHWAB_CLIENT_ID
  SCHWAB_CLIENT_SECRET
Optional:
  SCHWAB_CALLBACK_URL   (default https://127.0.0.1:8182 — must match Developer Portal)
  SCHWAB_TOKEN_PATH     (default schwab_token.json)

Usage (from repo root):
  python scripts/schwab_login.py              # browser + local HTTPS callback
  python scripts/schwab_login.py --manual     # paste redirect URL (if cert page blocks you)
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, ".env"))

from schwab.auth import client_from_manual_flow, easy_client  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Schwab OAuth token for schwab-py")
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Copy the full redirect URL from the browser into the terminal (no local server)",
    )
    args = parser.parse_args()

    cid = os.getenv("SCHWAB_CLIENT_ID", "").strip()
    secret = os.getenv("SCHWAB_CLIENT_SECRET", "").strip()
    if not cid or not secret:
        print(
            "Set SCHWAB_CLIENT_ID and SCHWAB_CLIENT_SECRET in .env",
            file=sys.stderr,
        )
        sys.exit(1)
    cb = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8182").strip()
    token = os.path.join(
        ROOT, os.getenv("SCHWAB_TOKEN_PATH", "schwab_token.json")
    )

    if args.manual:
        client_from_manual_flow(cid, secret, cb, token)
    else:
        print("Opening browser for Schwab login …")
        print(
            "(If the terminal stays quiet: use Advanced → Proceed on the "
            "127.0.0.1 certificate warning, or run with --manual.)"
        )
        easy_client(cid, secret, cb, token, interactive=True)
    print(f"Token written to {token}")


if __name__ == "__main__":
    main()
