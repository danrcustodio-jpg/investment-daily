# Investment Daily - Alert Scheduler
# Registers two scheduled tasks:
#   1. InvestmentDailyAlerts       - equities + crypto, Mon-Fri market hours
#   2. InvestmentDailyCryptoAlerts - crypto only (24/7, including weekends)
#
# Uses schtasks.exe (no Administrator required - runs as the current user).

$ScriptDir  = "C:\Users\Owner\InvestmentDaily"
$PythonExe  = (Get-Command python).Source
$ScriptPath = Join-Path $ScriptDir "alert_system.py"

function Register-AlertTask {
    param(
        [string]$TaskName,
        [string]$Cmd,
        [string]$Schedule,
        [string]$Days,
        [string]$StartTime,
        [string]$Duration
    )

    schtasks /delete /tn $TaskName /f 2>$null | Out-Null

    $createArgs = @(
        "/create", "/tn", $TaskName, "/tr", $Cmd,
        "/sc", $Schedule, "/st", $StartTime,
        "/ri", "30", "/du", $Duration,
        "/sd", (Get-Date -Format "MM/dd/yyyy"), "/f"
    )
    if ($Days) { $createArgs += @("/d", $Days) }

    schtasks @createArgs

    if ($LASTEXITCODE -eq 0) {
        $xml = schtasks /query /tn $TaskName /xml ONE 2>$null
        if ($xml) {
            $xml = $xml -replace "<WorkingDirectory>.*?</WorkingDirectory>", ""
            $xml = $xml -replace "</Exec>", "<WorkingDirectory>$ScriptDir</WorkingDirectory></Exec>"
            $tmpXml = Join-Path $env:TEMP "$TaskName.xml"
            $xml | Out-File -FilePath $tmpXml -Encoding UTF8
            schtasks /create /tn $TaskName /xml $tmpXml /f | Out-Null
            Remove-Item $tmpXml -ErrorAction SilentlyContinue
        }
        Write-Host "  '$TaskName' registered." -ForegroundColor Green
    } else {
        Write-Host "  '$TaskName' FAILED - check the error above." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Registering Investment Daily alert tasks..." -ForegroundColor Cyan

# Task 1: Equities + crypto - weekdays, market hours (9:30 AM to 4:00 PM ET)
Register-AlertTask `
    -TaskName  "InvestmentDailyAlerts" `
    -Cmd       "`"$PythonExe`" `"$ScriptPath`"" `
    -Schedule  "weekly" `
    -Days      "MON,TUE,WED,THU,FRI" `
    -StartTime "09:30" `
    -Duration  "0006:30"

# Task 2: Crypto only - every day 24/7 (30-min interval, --crypto flag)
Register-AlertTask `
    -TaskName  "InvestmentDailyCryptoAlerts" `
    -Cmd       "`"$PythonExe`" `"$ScriptPath`" --crypto" `
    -Schedule  "daily" `
    -Days      "" `
    -StartTime "00:00" `
    -Duration  "0023:50"

Write-Host ""
Write-Host "Done. Both tasks registered:" -ForegroundColor Cyan
Write-Host "  InvestmentDailyAlerts       - Mon-Fri, every 30 min, 9:30 AM - 4:00 PM ET"
Write-Host "  InvestmentDailyCryptoAlerts - Daily (incl. weekends), every 30 min, 24/7"
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  Run now   : schtasks /run /tn InvestmentDailyAlerts"
Write-Host "  Run crypto: schtasks /run /tn InvestmentDailyCryptoAlerts"
Write-Host "  Status    : schtasks /query /tn InvestmentDailyAlerts /fo list"
Write-Host "  Remove    : schtasks /delete /tn InvestmentDailyAlerts /f"
Write-Host "              schtasks /delete /tn InvestmentDailyCryptoAlerts /f"