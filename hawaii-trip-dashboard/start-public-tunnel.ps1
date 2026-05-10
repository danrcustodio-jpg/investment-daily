# Serves the dashboard on localhost and opens a public HTTPS URL via Cloudflare Quick Tunnel.
# Install cloudflared once: winget install --id Cloudflare.cloudflared
# Stop: press Ctrl+C (stops tunnel and the local server).

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  Write-Error "Python not found on PATH. Install Python 3 and try again."
}

$cf = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cf) {
  Write-Host "cloudflared not found. Install with:" -ForegroundColor Yellow
  Write-Host "  winget install --id Cloudflare.cloudflared" -ForegroundColor Cyan
  Write-Host "Then re-run this script." -ForegroundColor Yellow
  exit 1
}

Write-Host "Starting local server on http://127.0.0.1:8765 ..." -ForegroundColor Green
$proc = Start-Process -FilePath "python" `
  -ArgumentList @("-m", "http.server", "8765", "--bind", "127.0.0.1") `
  -WorkingDirectory $root `
  -PassThru `
  -WindowStyle Hidden

Start-Sleep -Seconds 1

try {
  Write-Host "Opening Cloudflare Quick Tunnel (public URL will appear below)..." -ForegroundColor Green
  Write-Host "Share that URL only with people you trust. Press Ctrl+C when done.`n" -ForegroundColor Yellow
  & cloudflared tunnel --url http://127.0.0.1:8765
}
finally {
  if ($proc -and -not $proc.HasExited) {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
  }
  Write-Host "`nLocal server stopped." -ForegroundColor Gray
}
