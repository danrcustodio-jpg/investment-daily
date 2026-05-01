param(
    [switch]$SkipQA,
    [switch]$SkipReports,
    [switch]$SkipEvalSnapshot,
    [switch]$SkipGateCheck,
    [string]$EvalLabel = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $PSScriptRoot
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source

if (-not $PythonExe) {
    Write-Error "Python is not available on PATH."
    exit 1
}

function Invoke-Step {
    param(
        [string]$Name,
        [string[]]$Args
    )

    $startedAt = Get-Date
    Write-Host ""
    Write-Host ("=== {0} === [{1}]" -f $Name, $startedAt.ToString("HH:mm:ss")) -ForegroundColor Cyan
    & $PythonExe @Args
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step failed: $Name (exit code $LASTEXITCODE)"
        exit $LASTEXITCODE
    }
    $endedAt = Get-Date
    $elapsed = New-TimeSpan -Start $startedAt -End $endedAt
    Write-Host (
        "Done: {0} [{1}] ({2:mm\:ss})" -f
        $Name,
        $endedAt.ToString("HH:mm:ss"),
        $elapsed
    ) -ForegroundColor DarkGray
}

Push-Location $ScriptDir
try {
    Write-Host ""
    Write-Host "Running Investment Daily full cycle..." -ForegroundColor Green

    Invoke-Step -Name "Strategy smoke test" -Args @("tests/test_strategy.py")
    Invoke-Step -Name "Newsletter smoke test" -Args @("tests/test_run.py")
    Invoke-Step -Name "Alert smoke test" -Args @("tests/test_alerts.py")

    if (-not $SkipQA) {
        Invoke-Step -Name "QA scenario suite" -Args @("tests/qa_scenarios.py")
    } else {
        Write-Host ""
        Write-Host "Skipping QA scenario suite." -ForegroundColor Yellow
    }

    if (-not $SkipReports) {
        Invoke-Step -Name "Generate alerts report" -Args @("generate_reports.py", "--alerts")
        Invoke-Step -Name "Generate newsletter report" -Args @("generate_reports.py", "--newsletter")
    } else {
        Write-Host ""
        Write-Host "Skipping report generation." -ForegroundColor Yellow
    }

    $evalLabelUsed = $null
    if (-not $SkipEvalSnapshot) {
        $evalLabelUsed = $EvalLabel
        if (-not $evalLabelUsed) {
            $evalLabelUsed = "run_" + (Get-Date -Format "yyyyMMdd_HHmmss")
        }
        Invoke-Step -Name "Write eval snapshot" -Args @("scripts/write_eval_snapshot.py", "--label", $evalLabelUsed)
    } else {
        Write-Host ""
        Write-Host "Skipping eval snapshot." -ForegroundColor Yellow
    }

    if (-not $SkipGateCheck) {
        if ($evalLabelUsed) {
            $snapRel = Join-Path "evals" "runs" | Join-Path -ChildPath "$evalLabelUsed.json"
            Invoke-Step -Name "Check eval gates" -Args @("scripts/check_eval_gates.py", "--snapshot", $snapRel)
        } else {
            Invoke-Step -Name "Check eval gates (latest snapshot)" -Args @("scripts/check_eval_gates.py", "--latest")
        }
    } else {
        Write-Host ""
        Write-Host "Skipping eval gate check." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Full cycle completed successfully." -ForegroundColor Green
} finally {
    Pop-Location
}
