# Run this ONCE to save your ngrok auth token.
# Get your free token at: https://dashboard.ngrok.com/get-started/your-authtoken
param([Parameter(Mandatory)][string]$Token)
$Token.Trim() | Out-File "C:\Users\Owner\InvestmentDaily\.ngrok_token" -Encoding utf8 -NoNewline
Write-Host "Token saved. Now run: powershell -ExecutionPolicy Bypass -File start_dashboard.ps1" -ForegroundColor Green
