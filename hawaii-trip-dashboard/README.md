# Hawaii trip mobile dashboard

Self-contained **HTML / CSS / JS** mirror of the Cursor canvas trip plan so you can open it on **phones** from **home Wi‑Fi**, **anywhere on the internet** (tunnel), or a **permanent hosted URL**.

## Update data after editing the canvas

The canvas source lives at:

`.cursor/projects/c-Users-Owner-InvestmentDaily/canvases/hawaii-trip-overview.canvas.tsx`

Regenerate `trip-data.js`:

```powershell
cd "C:\Users\Owner\InvestmentDaily\hawaii-trip-dashboard"
python extract_trip_from_canvas.py
```

## View on your phones (same Wi‑Fi)

1. On your PC, start the local server:

```powershell
cd "C:\Users\Owner\InvestmentDaily\hawaii-trip-dashboard"
python -m http.server 8765 --bind 0.0.0.0
```

2. Find your PC’s LAN IP (e.g. `ipconfig` → IPv4 under Wi‑Fi).

3. On each phone, open:

`http://YOUR_PC_IP:8765/`

**Tip:** Use “Add to Home Screen” (Safari / Chrome) for a fullscreen shortcut.

**Firewall:** If the phone cannot connect, allow Python through Windows Firewall for private networks.

---

## Access from anywhere (not on your Wi‑Fi)

Your home router does not expose your PC to the public internet, so phones on cellular or another network need one of these patterns.

### Option 1 — Quick tunnel (good for trips / testing)

Cloudflare **Quick Tunnel** gives a random `*.trycloudflare.com` HTTPS URL while your PC is on and the script is running. No Cloudflare account required for the quick tunnel.

1. Install **cloudflared** (once):

   ```powershell
   winget install --id Cloudflare.cloudflared
   ```

   Restart the terminal so `cloudflared` is on your PATH.

2. From this folder, run:

   ```powershell
   cd "C:\Users\Owner\InvestmentDaily\hawaii-trip-dashboard"
   .\start-public-tunnel.ps1
   ```

3. Copy the **https://….trycloudflare.com** URL from the terminal and open it on the other device (cellular is fine).

4. **Stop** when finished: **Ctrl+C** in that window (stops the tunnel and the local server).

**Security:** Anyone with the link can open the page while the tunnel is active. Treat the URL like a temporary password; do not post it publicly.

**Alternative — ngrok:** If you use [ngrok](https://ngrok.com/), run the local server on `127.0.0.1:8765`, then `ngrok http 8765` and use the URL ngrok prints.

### Option 2 — Permanent public URL (this repo → GitHub Pages)

The **InvestmentDaily** repo includes a workflow that publishes **`hawaii-trip-dashboard/`** to **GitHub Pages** whenever you push changes under that folder (or run the workflow manually).

**One-time setup**

1. On GitHub: open the repo → **Settings** → **Pages**.
2. Under **Build and deployment** → **Source**, choose **GitHub Actions** (not “Deploy from a branch”).
3. Push this repo to GitHub (or merge) so `.github/workflows/deploy-hawaii-dashboard.yml` exists on **`main`**.

After the first successful run, Pages shows your site URL (usually `https://<your-username>.github.io/<repo-name>/`).

**Update the live site after editing the canvas**

1. Regenerate data:

   ```powershell
   cd "C:\Users\Owner\InvestmentDaily\hawaii-trip-dashboard"
   python extract_trip_from_canvas.py
   ```

2. Commit and push `hawaii-trip-dashboard/` (including `trip-data.js`). The workflow redeploys automatically.

**Manual deploy:** GitHub → **Actions** → **Deploy Hawaii trip dashboard** → **Run workflow**.

---

### Option 2b — Other static hosts (optional)

Same folder works anywhere with static hosting: **[Netlify Drop](https://app.netlify.com/drop)**, Cloudflare Pages, etc. No build step.

---

## Optional: same-folder checklist before hosting

- `index.html`, `styles.css`, `app.js`, `trip-data.js` are all present.
- Open the hosted site once on a phone and confirm **Timeline** and a **day** expand correctly.
