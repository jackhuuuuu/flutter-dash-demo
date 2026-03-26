# scripts/run_local.ps1
# ─────────────────────────────────────────────────────────────────────────────
# Local Development Runner
#
# Kills any existing Streamlit processes on the target ports, then starts
# the FBI Hub and dashboard apps simultaneously.
#
# Run from the repo root:
#     .\scripts\run_local.ps1
#
# Apps:
#   FBI Hub                  → http://localhost:8501
#   Group Executive Report   → http://localhost:8502
#
# Press Ctrl+C to stop all apps.
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

# ── Port configuration ───────────────────────────────────────────────────────
# Add new apps here: @{ Port = <number>; Name = "<display name>"; Path = "<relative path from repo root>" }
$apps = @(
    @{ Port = 8501; Name = "FBI Hub";                 Path = "hub" },
    @{ Port = 8502; Name = "Group Executive Report";  Path = "apps/group_executive_report" }
)

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " FBI Hub — Local Development Runner" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Kill any existing processes on our ports ─────────────────────────────────
Write-Host "[*] Checking for existing processes..." -ForegroundColor Yellow
foreach ($app in $apps) {
    $port = $app.Port
    $lines = netstat -ano | Select-String "LISTENING" | Select-String ":$port "
    foreach ($line in $lines) {
        $procId = ($line -split '\s+')[-1]
        if ($procId -and $procId -ne "0") {
            Write-Host "    Killing PID $procId on port $port ($($app.Name))" -ForegroundColor DarkYellow
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}
Start-Sleep -Seconds 1

# ── Activate virtual environment ─────────────────────────────────────────────
$venvActivate = Join-Path $repoRoot ".venv/Scripts/Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
    & $venvActivate
}

# ── Ensure flutter_dash is installed ─────────────────────────────────────────
Write-Host "[*] Ensuring flutter_dash is installed..." -ForegroundColor Yellow
Push-Location $repoRoot
pip install -e . --quiet 2>$null
Pop-Location

# ── Start all apps ───────────────────────────────────────────────────────────
Write-Host ""
$jobs = @()
foreach ($app in $apps) {
    $idx = [array]::IndexOf($apps, $app) + 1
    Write-Host "[$idx] Starting $($app.Name) on http://localhost:$($app.Port)" -ForegroundColor Green
    $job = Start-Job -ScriptBlock {
        param($root, $venv, $appPath, $port)
        if (Test-Path $venv) { & $venv }
        Set-Location (Join-Path $root $appPath)
        streamlit run app.py --server.port $port --server.headless true
    } -ArgumentList $repoRoot, $venvActivate, $app.Path, $app.Port
    $jobs += $job
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
foreach ($app in $apps) {
    $padded = "$($app.Name):".PadRight(25)
    Write-Host " $padded http://localhost:$($app.Port)" -ForegroundColor White
}
Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Press Ctrl+C to stop all apps." -ForegroundColor Yellow
Write-Host ""

# ── Wait and forward output ──────────────────────────────────────────────────
try {
    while ($true) {
        foreach ($job in $jobs) {
            Receive-Job $job -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "`n[*] Stopping apps..." -ForegroundColor Yellow
    foreach ($job in $jobs) {
        Stop-Job $job -ErrorAction SilentlyContinue
        Remove-Job $job -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[*] All apps stopped." -ForegroundColor Green
}
