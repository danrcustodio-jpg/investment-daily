"""Synthetic-snapshot smoke test for generate_reports.generate_alerts_report().

Builds a tiny last_scan.json that mirrors today's MRVL 17:14 UTC run shape,
calls generate_alerts_report(), then prints the rendered ALERTS.md to stdout.
Restores any pre-existing last_scan.json and reports/ALERTS.md afterwards.
"""
import json
import os
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from alert_system import LAST_SCAN_FILE  # noqa: E402
import generate_reports  # noqa: E402

REPORTS_DIR = os.path.join(ROOT, "reports")
ALERTS_PATH = os.path.join(REPORTS_DIR, "ALERTS.md")


def _slim(direction: str, ticker: str, strategy: str, conf: float) -> dict:
    return {
        "direction": direction,
        "ticker": ticker,
        "strategy": strategy,
        "confidence": conf,
        "win_rate": 80.0,
        "avg_return": 1.0,
        "sharpe": 1.2,
        "max_drawdown": -5.0,
    }


def main() -> int:
    backup_snap = LAST_SCAN_FILE + ".bak"
    backup_report = ALERTS_PATH + ".bak"
    had_snap = os.path.exists(LAST_SCAN_FILE)
    had_report = os.path.exists(ALERTS_PATH)
    if had_snap:
        shutil.copy2(LAST_SCAN_FILE, backup_snap)
    if had_report:
        shutil.copy2(ALERTS_PATH, backup_report)

    fired = [
        _slim("BULLISH", "MRVL", "52-Week Breakout", 95),
        _slim("BULLISH", "ARM",  "52-Week Breakout", 90),
        _slim("BULLISH", "ARKK", "TRIX — Bullish Cross", 88),
    ]
    sup_ticker = [
        _slim("BULLISH", "MRVL", "ADX Strong Trend — Bullish", 84),
        _slim("BEARISH", "QQQ",  "Keltner — Upper Channel Touch", 49),
    ]
    sup_signal: list = []
    snoozed: list = []
    bullish_n = 4
    bearish_n = 1
    above_thresh = bullish_n + bearish_n

    snap = {
        "scan_at_iso": datetime.now().astimezone().isoformat(),
        "scan_human": "Smoke Test — synthetic snapshot",
        "crypto_only": False,
        "market_status": "test",
        "early_exit_reason": None,
        "thresholds": {
            "min_confidence": 50.0,
            "alert_cooldown_hours": 6,
            "sms_cooldown_hours": 1,
            "high_confidence_15m_threshold": 68.0,
            "cooldown_bypass_move_pct": 2.0,
        },
        "totals": {
            "scanned": above_thresh,
            "above_threshold": above_thresh,
            "bullish": bullish_n,
            "bearish": bearish_n,
            "fired_this_run": len(fired),
            "suppressed_signal_cooldown": len(sup_signal),
            "suppressed_ticker_cooldown": len(sup_ticker),
            "bypassed_signal_cooldown": 0,
            "snoozed": len(snoozed),
            "below_threshold": 0,
        },
        "buckets": {
            "fired_this_run": fired,
            "suppressed_signal_cooldown": sup_signal,
            "suppressed_ticker_cooldown": sup_ticker,
            "bypassed_signal_cooldown": [],
            "snoozed": snoozed,
        },
        "sms": {
            "sent": True,
            "reason": None,
            "top_ticker": "MRVL",
            "more_count": len(fired) - 1,
        },
    }

    try:
        with open(LAST_SCAN_FILE, "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)

        generate_reports.generate_alerts_report()

        with open(ALERTS_PATH, encoding="utf-8") as f:
            rendered = f.read()
        # Echo to a sibling file the user can inspect (avoids Windows console codec issues).
        echo_path = os.path.join(os.path.dirname(__file__), "_smoke_alerts_report.out.md")
        with open(echo_path, "w", encoding="utf-8") as f:
            f.write(rendered)
        print(f"Wrote rendered report copy: {echo_path}  ({len(rendered):,} chars)")

        expected_phrases = [
            "Fired this run (SMS + email)",
            "Skipped — same ticker notified",
            "Suppressed — same signal already fired",
            "📲 SMS sent",
            "**MRVL**",
        ]
        missing = [p for p in expected_phrases if p not in rendered]
        if missing:
            print(f"FAIL: missing expected phrases: {missing}")
            return 1
        print("OK: all expected phrases present.")

        # Bonus: exercise write_last_scan_snapshot's early-exit shapes
        from alert_system import write_last_scan_snapshot
        write_last_scan_snapshot(
            crypto_only=False,
            market_status="test",
            all_signals=[],
            eligibility={},
            sms_status={"sent": False, "reason": "no_signals", "top_ticker": None, "more_count": 0},
            early_exit_reason="no_signals_above_threshold",
        )
        with open(LAST_SCAN_FILE, encoding="utf-8") as f:
            empty_snap = json.load(f)
        assert empty_snap["totals"]["scanned"] == 0
        assert empty_snap["early_exit_reason"] == "no_signals_above_threshold"
        print("OK: write_last_scan_snapshot handles empty / early-exit shape.")

        # Render the empty snapshot through the report to confirm it still produces output.
        generate_reports.generate_alerts_report()
        with open(ALERTS_PATH, encoding="utf-8") as f:
            empty_rendered = f.read()
        if "Run ended early" not in empty_rendered or "no_signals_above_threshold" not in empty_rendered:
            print("FAIL: empty snapshot did not render early-exit banner")
            return 1
        print("OK: empty snapshot renders with early-exit banner.")

        # Conflict detection: rebuild a snapshot with MRVL conflicted (BULL 95 vs BEAR 85).
        from alert_system import compute_ticker_conflicts, select_sms_top_signal, send_sms

        def _full(direction, ticker, strategy, conf, indicator="ind"):
            return {
                "direction": direction,
                "ticker": ticker,
                "strategy": strategy,
                "confidence": conf,
                "indicator": indicator,
                "backtest": {"5d": {"win_rate": 80, "avg_return": 1.0, "sharpe": 1.2, "max_drawdown": -5.0}},
            }

        active = [
            _full("BULLISH", "MRVL", "52-Week Breakout", 95, "Price 284.77 broke 52-week high 219.43"),
            _full("BEARISH", "MRVL", "Fisher Transform — High Extreme", 85),
            _full("BEARISH", "MRVL", "RSI Overbought", 83),
            _full("BULLISH", "ARM",  "52-Week Breakout", 90),  # uncontested
        ]
        new_sigs = active  # treat all as new for the test
        conflicts_dict = compute_ticker_conflicts(active, min_score=65)
        assert "MRVL" in conflicts_dict and conflicts_dict["MRVL"]["bull_max"] == 95 and conflicts_dict["MRVL"]["bear_max"] == 85
        assert "ARM" not in conflicts_dict
        top, is_conflicted = select_sms_top_signal(new_sigs, conflicts_dict)
        assert top["ticker"] == "MRVL" and is_conflicted, f"unexpected top: {top}"
        print("OK: compute_ticker_conflicts + select_sms_top_signal flag MRVL contested.")

        # Build the SMS body locally without actually sending — we monkeypatch smtplib.
        import smtplib
        captured: dict[str, str] = {}

        class _FakeSMTP:
            def __init__(self, *a, **k):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def login(self, *a, **k):
                pass

            def sendmail(self, _from, _to, msg_str):
                captured["raw"] = msg_str

        real_smtp_ssl = smtplib.SMTP_SSL
        smtplib.SMTP_SSL = _FakeSMTP  # type: ignore[assignment]
        os.environ.setdefault("EMAIL_SENDER", "test@example.com")
        os.environ.setdefault("EMAIL_PASSWORD", "x")
        os.environ.setdefault("SMS_GATEWAY", "5551234567@vtext.com")
        # Reload module-level env-derived constants for the patched env
        import importlib
        import alert_system as _als
        importlib.reload(_als)
        try:
            ok = _als.send_sms(new_sigs, conflicts=conflicts_dict, top_signal=top)
            assert ok and "raw" in captured, "send_sms returned False or no body captured"
            from email import message_from_string
            msg_obj = message_from_string(captured["raw"])
            payload_bytes = msg_obj.get_payload(decode=True)
            assert payload_bytes is not None, "MIME payload could not be decoded"
            body = payload_bytes.decode("utf-8")
            assert "MIXED BUY: MRVL" in body, f"missing MIXED prefix; decoded body=\n{body}"
            assert "vs BEAR top 85" in body, f"missing opposing-side info; decoded body=\n{body}"
            assert "n=2" in body, f"missing opposing-side count; decoded body=\n{body}"
            body_path = os.path.join(os.path.dirname(__file__), "_smoke_sms_body.out.txt")
            with open(body_path, "w", encoding="utf-8") as f:
                f.write(body)
            print(
                f"OK: send_sms emits MIXED prefix with opposing-side score. "
                f"Body ({len(body)} chars) -> {body_path}"
            )
        finally:
            smtplib.SMTP_SSL = real_smtp_ssl  # type: ignore[assignment]
        return 0
    finally:
        if had_snap:
            shutil.move(backup_snap, LAST_SCAN_FILE)
        else:
            try:
                os.remove(LAST_SCAN_FILE)
            except FileNotFoundError:
                pass
        if had_report:
            shutil.move(backup_report, ALERTS_PATH)
        else:
            try:
                os.remove(ALERTS_PATH)
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    sys.exit(main())
