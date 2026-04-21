# ─── Investment Daily — Windows Task Scheduler Setup ─────────────────────────
# Run this script ONCE in PowerShell (as Administrator) to register the task.
# After that, Windows will run the newsletter automatically every morning.
# ─────────────────────────────────────────────────────────────────────────────

$ScriptDir  = "C:\Users\Owner\InvestmentDaily"
$PythonExe  = (Get-Command python).Source   # auto-detects your Python install
$ScriptPath = Join-Path $ScriptDir "investment_daily.py"
$TaskName   = "InvestmentDailyNewsletter"

# ── Customize the send time here (24-hour format) ────────────────────────────
$SendHour   = 7     # 7 = 7:00 AM
$SendMinute = 30    # 30 = :30
# ─────────────────────────────────────────────────────────────────────────────

$Action  = New-ScheduledTaskAction `
    -Execute  $PythonExe `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $ScriptDir

$Trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "$($SendHour):$($SendMinute.ToString('D2'))"

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -StartWhenAvailable `          # runs at next opportunity if PC was off
    -RunOnlyIfNetworkAvailable

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action   $Action `
    -Trigger  $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Force

Write-Host ""
Write-Host "✅  Task '$TaskName' registered successfully!" -ForegroundColor Green
Write-Host "    Runs daily at $($SendHour):$($SendMinute.ToString('D2')) AM"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View task   : Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Run now     : Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Remove task : Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
