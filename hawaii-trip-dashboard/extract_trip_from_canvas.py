"""Regenerate trip-data.js from the Cursor canvas trip object (run after editing the canvas)."""
from pathlib import Path

CANVAS = Path(
    r"C:\Users\Owner\.cursor\projects\c-Users-Owner-InvestmentDaily\canvases\hawaii-trip-overview.canvas.tsx"
)
OUT = Path(__file__).resolve().parent / "trip-data.js"


START_MARKER = "const trip: TripModel = {"


def main() -> None:
    lines = CANVAS.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith(START_MARKER))
    except StopIteration as exc:
        raise SystemExit(f"Could not find '{START_MARKER}' in {CANVAS}") from exc
    closing = "};"
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].rstrip() == closing),
        None,
    )
    if end is None:
        raise SystemExit(f"Could not find closing {closing!r} for trip object in {CANVAS}")
    # Inner body: everything between `const trip: TripModel = {` and the matching `};` (inclusive).
    inner = "\n".join(lines[start + 1 : end + 1])
    header = (
        "/** Synced from hawaii-trip-overview.canvas.tsx — re-run extract_trip_from_canvas.py after edits */\n"
        "window.HAWAII_TRIP = {\n"
    )
    OUT.write_text(header + inner + "\n", encoding="utf-8")
    print(f"Wrote {OUT} (canvas lines {start + 2}..{end + 1})")


if __name__ == "__main__":
    main()
