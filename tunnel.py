"""
Starts an ngrok tunnel on port 5050 and prints the public URL.
Uses pyngrok which manages the ngrok binary automatically.
"""
import sys
from pyngrok import ngrok, conf

TOKEN_FILE = r"C:\Users\Owner\InvestmentDaily\.ngrok_token"

try:
    with open(TOKEN_FILE, "r") as f:
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

print(f"\n{'='*55}")
print(f"  PHONE URL (works from anywhere):")
print(f"  {public_url}")
print(f"\n  Local URL (same WiFi only):")
print(f"  http://192.168.4.43:5050")
print(f"{'='*55}")
print("\nTunnel is open. Close this window to stop it.")

# Keep alive
try:
    ngrok.get_ngrok_process().proc.wait()
except KeyboardInterrupt:
    ngrok.kill()
    print("Tunnel closed.")
