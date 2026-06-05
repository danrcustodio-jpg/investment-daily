"""
Starts an ngrok tunnel on port 5050 and prints the public URL.
Uses pyngrok which manages the ngrok binary automatically.

Side effect: persists the live public URL to `.ngrok_url` in this directory so
`alert_system.py` can include it as a dashboard link in outgoing SMS alerts.
The file is removed on clean shutdown to avoid leaving a stale URL that would
point to a dead tunnel.
"""
import os
import sys
from pyngrok import ngrok, conf

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, ".ngrok_token")
URL_FILE   = os.path.join(SCRIPT_DIR, ".ngrok_url")

try:
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    conf.get_default().auth_token = token
except FileNotFoundError:
    print("ERROR: .ngrok_token not found. Run save_ngrok_token.ps1 first.")
    sys.exit(1)

print("Opening ngrok tunnel on port 5050...")
tunnel = ngrok.connect(5050, "http")
public_url = tunnel.public_url

# Prefer https
if not public_url.startswith("https"):
    public_url = public_url.replace("http://", "https://")

try:
    with open(URL_FILE, "w", encoding="utf-8") as f:
        f.write(public_url.rstrip("/") + "\n")
    print(f"  (wrote URL to {URL_FILE} for SMS dashboard link)")
except OSError as exc:
    print(f"  WARN: could not write {URL_FILE}: {exc}")

print(f"\n{'='*55}")
print("  PHONE URL (works from anywhere):")
print(f"  {public_url}")
print("\n  Local URL (same WiFi only):")
print("  http://192.168.4.43:5050")
print(f"{'='*55}")
print("\nTunnel is open. Close this window to stop it.")

# Keep alive
try:
    ngrok.get_ngrok_process().proc.wait()
except KeyboardInterrupt:
    ngrok.kill()
    print("Tunnel closed.")
finally:
    try:
        os.remove(URL_FILE)
    except OSError:
        pass
