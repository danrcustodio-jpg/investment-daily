#!/usr/bin/env python3
"""
Standalone SMS deliverability test.

Sends ONE plain-text message via the same SMTP path the alert system uses
(Gmail SMTP_SSL -> SMS_GATEWAY email-to-SMS address) so you can verify
end-to-end deliverability without touching alert state, cooldowns, or scans.

Reads EMAIL_SENDER, EMAIL_PASSWORD, SMS_GATEWAY from the project .env.
"""

import os
import smtplib
import sys
import time
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    if not env_path.exists():
        print(f"[FAIL] .env not found at {env_path}")
        return 2
    load_dotenv(env_path)

    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    gateway = os.getenv("SMS_GATEWAY")

    missing = [n for n, v in
               (("EMAIL_SENDER", sender), ("EMAIL_PASSWORD", password), ("SMS_GATEWAY", gateway))
               if not v]
    if missing:
        print(f"[FAIL] Missing env vars: {', '.join(missing)}")
        return 2

    domain = gateway.split("@", 1)[1] if "@" in gateway else "?"
    print(f"Sender: {sender}")
    print(f"Recipient gateway domain: {domain}")
    print(f"Recipient length: {len(gateway)} chars")

    body = f"Investment Daily SMS test {int(time.time())}"
    msg = MIMEText(body, _charset="utf-8")
    msg["From"] = sender
    msg["To"] = gateway

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(sender, password)
            refused = server.sendmail(sender, [gateway], msg.as_string())
        if refused:
            print(f"[FAIL] SMTP partially refused recipients: {refused}")
            return 1
        print(f"[OK] SMTP accepted message at {time.strftime('%H:%M:%S')}.")
        print("    Watch your phone for ~30-90s. If nothing arrives, the carrier")
        print("    silently dropped it (e.g. Verizon vtext/vzwpix EOL) — switch to Twilio.")
        return 0
    except smtplib.SMTPRecipientsRefused as exc:
        print(f"[FAIL] SMTP recipient refused: {exc.recipients}")
        return 1
    except smtplib.SMTPAuthenticationError as exc:
        print(f"[FAIL] SMTP auth failed: {exc}")
        return 1
    except Exception as exc:
        print(f"[FAIL] SMTP error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
