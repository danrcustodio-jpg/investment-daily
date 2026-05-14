#!/usr/bin/env python3
"""
Meeting Memo — record or upload audio, Whisper transcription, structured GPT summary.
Mobile-first single page. Self-hosted; bring your own OpenAI API key.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI
from werkzeug.utils import secure_filename

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 26 * 1024 * 1024  # 26 MiB cap (Whisper limit 25 MiB)

ALLOWED_EXTENSIONS = {"webm", "wav", "mp3", "m4a", "mp4", "mpeg", "mpga"}
TRANSCRIBE_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1")
SUMMARY_MODEL = os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4o-mini")


def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=key)


def _allowed(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS


SUMMARY_SYSTEM = """You are an expert meeting analyst. Given a raw transcript (may contain errors), produce:
1) **Title** — one line, specific.
2) **Executive summary** — 3–6 bullet points.
3) **Key decisions** — bullet list, or "None noted".
4) **Action items** — bullet list with owner if mentioned, or "None noted".
5) **Open questions / risks** — short bullet list, or "None noted".
6) **Chronology** — optional 4–8 short time-ordered beats if timestamps exist; else skip.

Use clear Markdown headings (##). Be concise; do not invent facts not supported by the transcript."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def api_process():
    if "audio" not in request.files:
        return jsonify({"ok": False, "error": "Missing file field `audio`"}), 400
    f = request.files["audio"]
    if not f or not f.filename:
        return jsonify({"ok": False, "error": "Empty upload"}), 400
    if not _allowed(f.filename):
        return jsonify(
            {
                "ok": False,
                "error": f"Unsupported type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            }
        ), 400

    raw_name = secure_filename(f.filename)
    suffix = Path(raw_name).suffix or ".webm"

    try:
        client = _client()
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_fp:
            tr = client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=audio_fp,
                response_format="verbose_json",
            )
    except Exception as e:
        return jsonify({"ok": False, "error": f"Transcription failed: {e}"}), 502
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    text = getattr(tr, "text", None) or ""
    if not text.strip():
        return jsonify({"ok": False, "error": "Transcription returned empty text"}), 502

    lang = getattr(tr, "language", None) or ""

    try:
        chat = client.chat.completions.create(
            model=SUMMARY_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM},
                {
                    "role": "user",
                    "content": f"Detected language hint: {lang or 'unknown'}\n\n---\n\n{text}",
                },
            ],
        )
        summary = (chat.choices[0].message.content or "").strip()
    except Exception as e:
        return jsonify(
            {
                "ok": True,
                "transcript": text,
                "language": lang,
                "summary": "",
                "summary_error": str(e),
            }
        )

    return jsonify(
        {
            "ok": True,
            "transcript": text,
            "language": lang,
            "summary": summary,
            "transcribe_model": TRANSCRIBE_MODEL,
            "summary_model": SUMMARY_MODEL,
        }
    )


@app.route("/api/health")
def health():
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    return jsonify({"ok": True, "openai_configured": has_key})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8766"))
    print(f"\n  Meeting Memo → http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
