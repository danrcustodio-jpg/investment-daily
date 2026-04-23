# ─── Investment Daily — Intraday Alert Scheduler ─────────────────────────────
# Uses schtasks.exe for reliable repeating trigger support.
# No Administrator required — runs as the current user.
# ─────────────────────────────────────────────────────────────────────────────

$ScriptDir  = "C:\Users\Owner\InvestmentDaily"
$PythonExe  = (Get-Command python).Source
$ScriptPath = Join-Path $ScriptDir "alert_system.py"
$TaskName   = "InvestmentDailyAlerts"

# Delete existing task if it exists (ignore error if it doesn't)
schtasks /delete /tn $TaskName /f 2>$null | Out-Null

# Create the task:
#   /sc weekly        — weekly schedule base
#   /d MON,TUE,...    — only weekdays
#   /st 09:30         — first run at 9:30 AM
#   /ri 30            — repeat every 30 minutes
#   /du 0006:30       — for a duration of 6 hours 30 minutes (until ~4:00 PM)
#   /tr               — the command to run
#   /f                — force create (overwrite if exists)

$cmd = "`"$PythonExe`" `"$ScriptPath`""

schtasks /create `
    /tn  $TaskName `
    /tr  $cmd `
    /sc  weekly `
    /d   "MON,TUE,WED,THU,FRI" `
    /st  "09:30" `
    /ri  30 `
    /du  "0006:30" `
    /sd  (Get-Date -Format "MM/dd/yyyy") `
    /f

if ($LASTEXITCODE -eq 0) {
    # Set the working directory via XML patch (schtasks doesn't support it directly)
    $xml = schtasks /query /tn $TaskName /xml ONE 2>$null
    if ($xml) {
        $xml = $xml -replace "<WorkingDirectory>.*?</WorkingDirectory>", ""
        $xml = $xml -replace "</Exec>", "<WorkingDirectory>$ScriptDir</WorkingDirectory></Exec>"
        $tmpXml = Join-Path $env:TEMP "alert_task.xml"
        $xml | Out-File -FilePath $tmpXml -Encoding UTF8
        schtasks /create /tn $TaskName /xml $tmpXml /f | Out-Null
        Remove-Item $tmpXml -ErrorAction SilentlyContinue
    }

    Write-Host ""
    Write-Host "Alert task '$TaskName' registered successfully!" -ForegroundColor Green
    Write-Host "  Schedule: Mon-Fri, every 30 min from 9:30 AM for 6.5 hrs (~4:00 PM ET)"
    Write-Host "  Python  : $PythonExe"
    Write-Host "  Script  : $ScriptPath"
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Cyan
    Write-Host "  Run now  : schtasks /run /tn '$TaskName'"
    Write-Host "  Status   : schtasks /query /tn '$TaskName' /fo list"
    Write-Host "  Remove   : schtasks /delete /tn '$TaskName' /f"
} else {
    Write-Host "Failed to register task. Check the error above." -ForegroundColor Red
}
