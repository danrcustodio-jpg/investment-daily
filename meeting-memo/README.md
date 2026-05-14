# Meeting Memo — self-hosted Fireflies-style capture

Record or upload audio from your phone, transcribe with **OpenAI Whisper**, then get **structured notes** (summary, decisions, action items) via **Chat Completions**. Runs as a small Flask app you control.

## Why this vs Fireflies

- **Transcription model**: Uses your OpenAI key (`whisper-1` API). No vendor lock-in on minutes if you bring your own billing.
- **File types**: Upload **webm, mp3, m4a, wav, mp4, mpeg, mpga** (whatever Whisper accepts; API limit **25 MB** per file).
- **Summaries**: Prompts are plain text in `app.py` — change tone, language, or add “sales call / interview” modes yourself.

## Setup

1. Copy env:

   ```bash
   cd meeting-memo
   cp .env.example .env
   ```

2. Add your **OpenAI API key** in `.env`.

3. Install and run:

   ```bash
   pip install -r requirements.txt
   python app.py
   ```

4. Open **http://127.0.0.1:8766** on your computer, or expose it to your phone:

   - Same WiFi: use your PC’s LAN IP (e.g. `http://192.168.1.5:8766`).
   - **Microphone in the browser** needs **HTTPS** on real phones (except localhost). Use Cloudflare Tunnel, ngrok, or deploy to Render/Fly with TLS.

## Security (important)

This MVP has **no login**. Only run on a trusted network or behind a VPN/tunnel with a secret URL. Add HTTP auth or OAuth before exposing to the internet.

## Limits

- OpenAI **Whisper** file size **25 MB** (enforced in app).
- Recording length depends on browser; very long meetings → upload a file instead.
