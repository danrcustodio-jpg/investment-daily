"""Regenerate trip-data.js from the Cursor canvas trip object (run after editing the canvas)."""
from pathlib import Path

CANVAS = Path(
    r"C:\Users\Owner\.cursor\projects\c-Users-Owner-InvestmentDaily\canvases\hawaii-trip-overview.canvas.tsx"
)
OUT = Path(__file__).resolve().parent / "trip-data.js"


def main() -> None:
    lines = CANVAS.read_text(encoding="utf-8").splitlines()
    # Trip object body: file lines 160-991 (indices 159-990): `  meta:` … `};`
    inner = "\n".join(lines[159:991])
    header = (
        "/** Synced from hawaii-trip-overview.canvas.tsx — re-run extract_trip_from_canvas.py after edits */\n"
        "window.HAWAII_TRIP = {\n"
    )
    OUT.write_text(header + inner + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
