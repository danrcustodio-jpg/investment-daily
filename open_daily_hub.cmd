@echo off
setlocal

set "SCRIPT_PATH=C:\Users\Owner\InvestmentDaily\scripts\open_daily_hub.ps1"

if not exist "%SCRIPT_PATH%" (
  echo Hub launcher script not found:
  echo %SCRIPT_PATH%
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_PATH%"
exit /b %errorlevel%
