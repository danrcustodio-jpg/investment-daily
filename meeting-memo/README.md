# Meeting Memo — local meeting capture

Run on **your machine only**: open **http://127.0.0.1:8766**, **tap “Start recording”**, tap **“Stop recording”** when done (or upload an audio file). Audio is sent to this same computer’s Flask app, transcribed with **OpenAI Whisper**, then summarized with **Chat Completions** using your API key in `.env`.

## Setup

```bash
cd meeting-memo
cp .env.example .env
# add OPENAI_API_KEY=sk-...
pip install -r requirements.txt
python app.py
```

Then visit **http://127.0.0.1:8766**.

## Behavior

- **Transcription**: `whisper-1` (25 MB max per file).
- **Summary**: editable prompts in `app.py` (default `gpt-4o-mini`).
- **No login** — meant for localhost; don’t expose to the internet without adding auth.

## Limits

- Very long meetings: stay under Whisper’s size limit, or use **Upload** with a compressed file.
