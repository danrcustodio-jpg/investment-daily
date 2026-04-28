$ScriptDir = Split-Path -Parent $PSScriptRoot
$HubPath = Join-Path $ScriptDir "hub\index.html"
$HubUrl = "http://127.0.0.1:5050/hub"
$DashboardUrl = "http://127.0.0.1:5050"
$AutoStartDashboard = $true
$AutoStartMealPlanner = $true
$DashboardScript = Join-Path $ScriptDir "dashboard.py"
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
$MealPlannerDir = "C:\Users\Owner\meal-planner"
$MealPlannerFrontendDir = Join-Path $MealPlannerDir "frontend"
$MealPlannerBackendUrl = "http://127.0.0.1:8000/docs"
$MealPlannerFrontendUrl = "http://localhost:5173"

if ($AutoStartDashboard) {
    try {
        $health = Invoke-RestMethod "$DashboardUrl/api/status" -TimeoutSec 2
        if ($health) {
            Write-Host "Dashboard already running." -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Starting dashboard..." -ForegroundColor Cyan
        if (-not $PythonExe) {
            Write-Error "Python is not available on PATH."
            exit 1
        }
        if (-not (Test-Path $DashboardScript)) {
            Write-Error "Dashboard script not found: $DashboardScript"
            exit 1
        }

        Start-Process -FilePath $PythonExe -ArgumentList $DashboardScript -WorkingDirectory $ScriptDir -WindowStyle Minimized
        Start-Sleep -Seconds 4

        try {
            $check = Invoke-RestMethod "$DashboardUrl/api/status" -TimeoutSec 3
            if ($check) {
                Write-Host "Dashboard started successfully." -ForegroundColor Green
            }
        }
        catch {
            Write-Warning "Dashboard may still be starting. Try again in a few seconds."
        }
    }
}

if (-not (Test-Path $HubPath)) {
    Write-Error "Hub file not found: $HubPath"
    exit 1
}

if ($AutoStartMealPlanner) {
    if (-not (Test-Path $MealPlannerDir)) {
        Write-Warning "Meal planner directory not found: $MealPlannerDir"
    }
    else {
        try {
            $mpBackend = Invoke-WebRequest $MealPlannerBackendUrl -UseBasicParsing -TimeoutSec 2
            if ($mpBackend.StatusCode -eq 200) {
                Write-Host "Meal planner backend already running." -ForegroundColor Green
            }
        }
        catch {
            if (-not $PythonExe) {
                Write-Warning "Python is not available, cannot auto-start meal planner backend."
            }
            else {
                Write-Host "Starting meal planner backend..." -ForegroundColor Cyan
                Start-Process -FilePath $PythonExe `
                    -ArgumentList @("-m", "uvicorn", "backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000") `
                    -WorkingDirectory $MealPlannerDir `
                    -WindowStyle Minimized
                Start-Sleep -Seconds 2
            }
        }

        try {
            $mpFrontend = Invoke-WebRequest $MealPlannerFrontendUrl -UseBasicParsing -TimeoutSec 2
            if ($mpFrontend.StatusCode -eq 200) {
                Write-Host "Meal planner frontend already running." -ForegroundColor Green
            }
        }
        catch {
            if (-not (Test-Path $MealPlannerFrontendDir)) {
                Write-Warning "Meal planner frontend directory not found: $MealPlannerFrontendDir"
            }
            else {
                Write-Host "Starting meal planner frontend..." -ForegroundColor Cyan
                Start-Process -FilePath "cmd.exe" `
                    -ArgumentList @("/c", "cd /d `"$MealPlannerFrontendDir`" && npm run dev") `
                    -WindowStyle Minimized
                Start-Sleep -Seconds 2
            }
        }
    }
}

Start-Process $HubUrl
