# Register daily portfolio simulation snapshot + email
# Runs every weekday at 4:15 PM (after market close)

$ScriptDir  = "C:\Users\Owner\InvestmentDaily"
$PythonExe  = (Get-Command python).Source
$TaskName   = "InvestmentDailySimSnapshot"

$TR = "cmd /C cd /D `"$ScriptDir`" ^&^& python portfolio_sim.py --snapshot --email"

schtasks.exe /Create /TN $TaskName /F /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 16:15 /TR $TR /RL LIMITED

if ($LASTEXITCODE -eq 0) {
    Write-Host "Registered: $TaskName (weekdays at 4:15 PM)" -ForegroundColor Green
} else {
    Write-Host "Failed to register task. Exit code: $LASTEXITCODE" -ForegroundColor Red
}
