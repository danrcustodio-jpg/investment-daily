# Investment Daily - Dashboard + Phone Tunnel Launcher
# Uses localhost.run (free, SSH-based, zero install) to expose the
# dashboard to your phone from anywhere.  SSH is built into Windows 10+.

$ScriptDir = "C:\Users\Owner\InvestmentDaily"
$PythonExe = (Get-Command python).Source
$Port      = 5050

# Kill any stale Flask on port 5050
Get-Process -Name python -ErrorAction SilentlyContinue |
    Where-Object { (& netstat -ano | Select-String ":$Port") -match $_.Id } |
    Stop-Process -Force -ErrorAction SilentlyContinue

# Start Flask dashboard
Write-Host "Starting Investment Daily dashboard..." -ForegroundColor Cyan
$flask = Start-Process `
    -FilePath         $PythonExe `
    -ArgumentList     "dashboard.py" `
    -WorkingDirectory $ScriptDir `
    -PassThru -WindowStyle Minimized

Write-Host "Waiting for dashboard to load..." -ForegroundColor Gray
Start-Sleep -Seconds 6

# Verify Flask
try {
    $s = Invoke-RestMethod "http://127.0.0.1:$Port/api/status" -TimeoutSec 5
    Write-Host "  Dashboard OK - $($s.signal_count) signals, market: $($s.sentiment)" -ForegroundColor Green
} catch {
    Write-Host "  Dashboard loading (strategy scan takes ~15s on first run)..." -ForegroundColor Yellow
}

# Open SSH tunnel via localhost.run (no account, no install needed)
Write-Host ""
Write-Host "Opening phone tunnel via localhost.run..." -ForegroundColor Cyan
Write-Host "(Watch for your URL to appear below - takes ~5 seconds)" -ForegroundColor Gray
Write-Host ""

# Run SSH tunnel - the URL appears in the output
# localhost.run gives a free HTTPS URL like: https://abc123.lhr.life
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 `
    -R "80:localhost:$Port" nokey@localhost.run 2>&1 | ForEach-Object {
    $line = $_
    Write-Host $line
    # Highlight the URL when it appears
    if ($line -match "https://[^\s]+\.lhr\.life") {
        $url = $Matches[0]
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  Open this on your phone:" -ForegroundColor Green
        Write-Host "  $url" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Start-Process $url
    }
}

# Cleanup Flask when tunnel closes
Stop-Process -Id $flask.Id -Force -ErrorAction SilentlyContinue
Write-Host "Tunnel closed. Dashboard stopped."
