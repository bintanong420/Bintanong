# Starts the local research stack in dependency order and waits for each health check:
# Docker Desktop -> Gemma model container (:18088) -> research API (:8021) -> Next dev (:3216) -> optional ngrok.
# Already-healthy services are left running. Stop everything: .\scripts\start-bintanong.ps1 -Stop
# Machine-specific defaults point at the ignored workspace environment (venv, portable Node, hosted-560 starter).
param(
    [switch]$Stop,
    [switch]$Ngrok,
    [string]$Workspace = 'C:\Coding-projects\bintanong_workspace',
    [string]$EnvDir = "$Workspace\audit-evidence\p12-env-20261031",
    [string]$ApiStarter = "$Workspace\audit-evidence\p12-hosted-560-activation-20261030\start_hosted_research_api.py",
    [string]$ModelContainer = 'bintanong-p09-cuda-latency'
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$logs = "$Workspace\audit-evidence\launcher-logs"
$pidFile = "$logs\pids.txt"
New-Item -ItemType Directory -Force $logs | Out-Null

function Healthy($url) {
    try { (Invoke-WebRequest $url -TimeoutSec 3 -UseBasicParsing).StatusCode -eq 200 } catch { $false }
}

function WaitFor($name, $url, $seconds, $proc, $log) {
    $deadline = (Get-Date).AddSeconds($seconds)
    Write-Host "Waiting for $name ($url, up to $seconds s)..." -NoNewline
    while ((Get-Date) -lt $deadline) {
        if (Healthy $url) { Write-Host ' ready'; return }
        if ($proc -and $proc.HasExited) { break }
        Start-Sleep 3; Write-Host '.' -NoNewline
    }
    Write-Host ''
    if ($log -and (Test-Path $log)) { Get-Content $log -Tail 30 | Write-Host -ForegroundColor DarkGray }
    throw "$name did not become healthy. Log: $log"
}

function Launch($name, $exe, $arguments, $dir) {
    $out = "$logs\$name.log"
    $p = Start-Process $exe -ArgumentList $arguments -WorkingDirectory $dir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $out -RedirectStandardError "$logs\$name.err.log"
    Add-Content $pidFile "$name $($p.Id)"
    return $p
}

if ($Stop) {
    if (Test-Path $pidFile) {
        foreach ($line in Get-Content $pidFile) {
            $name, $id = $line -split ' '
            if (Get-Process -Id $id -ErrorAction SilentlyContinue) { taskkill /PID $id /T /F | Out-Null; Write-Host "stopped $name ($id)" }
        }
        Remove-Item $pidFile
    }
    docker stop $ModelContainer 2>$null | Out-Null
    Write-Host "stopped $ModelContainer (Docker Desktop left running)"
    return
}

$py = "$EnvDir\venv\Scripts\python.exe"
$node = "$EnvDir\node\node-v24.21.0-win-x64\node.exe"
foreach ($f in $py, $node, $ApiStarter, "$repo\.env", "$repo\frontend\.env.local", "$repo\frontend\node_modules\next") {
    if (-not (Test-Path $f)) { throw "Missing prerequisite: $f" }
}

# 1. Docker Desktop
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Starting Docker Desktop...'
    Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
    $deadline = (Get-Date).AddSeconds(180)
    do { Start-Sleep 5; docker info *> $null } until ($LASTEXITCODE -eq 0 -or (Get-Date) -gt $deadline)
    if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop did not start within 180 s.' }
}

# 2. Model (Gemma via llama.cpp CUDA). Never pulls an image.
if (-not (Healthy 'http://127.0.0.1:18088/health')) {
    docker container inspect $ModelContainer *> $null
    if ($LASTEXITCODE -eq 0) { docker start $ModelContainer | Out-Null }
    else {
        $env:MODELS_DIR = "$Workspace/MODELS"
        docker compose -f "$repo\docker\bintu-cuda.compose.yaml" up -d --pull never bintu_cuda
        if ($LASTEXITCODE -ne 0) { throw 'Model container failed to start (image missing? it is never pulled implicitly).' }
    }
    WaitFor 'model' 'http://127.0.0.1:18088/health' 300 $null $null
} else { Write-Host 'model already healthy' }

# 3. Research API (loads encoder, curricula and ledgers; ~2-3 min cold)
if (-not (Healthy 'http://127.0.0.1:8021/health/live')) {
    $api = Launch 'backend' $py @('-X', 'utf8', "`"$ApiStarter`"") $repo
    WaitFor 'backend' 'http://127.0.0.1:8021/health/live' 600 $api "$logs\backend.err.log"
} else { Write-Host 'backend already healthy' }

# 4. Frontend. -H is required: without it Next blocks /_next/hmr and the page reloads in a loop.
if (-not (Healthy 'http://127.0.0.1:3216')) {
    $web = Launch 'frontend' $node @('node_modules/next/dist/bin/next', 'dev', '-H', '127.0.0.1', '-p', '3216') "$repo\frontend"
    WaitFor 'frontend' 'http://127.0.0.1:3216' 180 $web "$logs\frontend.log"
} else { Write-Host 'frontend already healthy' }

# 5. Optional public tunnel. Guests are public while it runs; no per-client rate limit is configured.
if ($Ngrok) { Launch 'ngrok' 'ngrok' @('http', '3216', '--log', 'stdout') $repo | Out-Null; Write-Host 'ngrok started (see launcher-logs\ngrok.log for the URL)' }

Write-Host "`nBintanong is up: http://127.0.0.1:3216  (API :8021, model :18088). Logs: $logs"
