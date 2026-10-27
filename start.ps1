<#
.SYNOPSIS
    MathMotion Studio frontend dev-server launcher (Vite).

.DESCRIPTION
    Starts the Vite development server for the React frontend on the loopback
    interface (default port 5173), after verifying that Node.js and npm are
    installed and that the frontend dependencies are present. The dev server
    proxies /api to the backend (default http://127.0.0.1:8765), so the
    backend started by run.ps1 must be running for the UI to work. Child
    processes started here are tracked and shut down cleanly on exit or
    Ctrl+C. The script never requires administrator rights and never kills
    an unrelated process that happens to hold the port.

    Use run.ps1 for the normal (production-style) start, which serves the
    built frontend from the backend itself. This script is for development
    with hot module replacement.

.PARAMETER Port
    Override the TCP port (default 5173). Must be free.

.PARAMETER Setup
    Only install frontend dependencies (npm ci), then exit. Does not start
    the dev server.

.PARAMETER NoBrowser
    Start the dev server but do not open a browser.

.PARAMETER BackendOrigin
    The backend origin the dev server proxies /api to
    (default http://127.0.0.1:8765, or MATHMOTION_BACKEND_ORIGIN).

.EXAMPLE
    .\start.ps1
    .\start.ps1 -Setup
    .\start.ps1 -NoBrowser
    .\start.ps1 -Port 5174
#>
[CmdletBinding()]
param(
    [int]$Port = 0,
    [switch]$Setup,
    [switch]$NoBrowser,
    [string]$BackendOrigin = ''
)

$ErrorActionPreference = 'Stop'

# --- 1. Project root from this script's own location -------------------------
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
$FrontendDir = Join-Path $ProjectRoot 'frontend'
$ViteJs     = Join-Path $FrontendDir 'node_modules\vite\bin\vite.js'

if ($Port -le 0) {
    $envPort = $env:MATHMOTION_FRONTEND_PORT
    if ($envPort -and [int]::TryParse($envPort, [ref]$null)) { $Port = [int]$envPort }
    else { $Port = 5173 }
}
if (-not $BackendOrigin) {
    if ($env:MATHMOTION_BACKEND_ORIGIN) { $BackendOrigin = $env:MATHMOTION_BACKEND_ORIGIN }
    else { $BackendOrigin = 'http://127.0.0.1:8765' }
}
$Host127 = '127.0.0.1'
$DevUrl  = "http://$Host127`:$Port"

function Write-Step($msg)  { Write-Host "  [..] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "  [ok] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "  [!!] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "  [XX] $msg" -ForegroundColor Red }

# --- 2. Requirements ---------------------------------------------------------
Write-Host "`nMathMotion Studio - frontend dev server" -ForegroundColor White
Write-Host ("-" * 40)

if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Err "PowerShell 5.1 or newer is required (found $($PSVersionTable.PSVersion))."
    exit 1
}
if (-not (Test-Path (Join-Path $FrontendDir 'package.json'))) {
    Write-Err "frontend/package.json was not found. Run this script from the repository root."
    exit 1
}

Write-Step 'Checking Node.js and npm...'
$node = Get-Command 'node' -ErrorAction SilentlyContinue
$npm  = Get-Command 'npm' -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) {
    Write-Err 'Node.js and npm are required for the frontend dev server but were not found.'
    Write-Host '    Install Node.js 20 or newer: https://nodejs.org/ (LTS)'
    Write-Host '    Then re-run: .\start.ps1'
    exit 1
}
$nodeVersion = (& node --version 2>$null).Trim()
Write-Ok "Node.js $nodeVersion at $($node.Source)"

# --- 3. Dependencies ---------------------------------------------------------
function Install-FrontendDeps {
    Write-Step 'Installing frontend dependencies (npm ci)...'
    Push-Location $FrontendDir
    try {
        & npm ci --no-audit --no-fund 2>&1 | ForEach-Object { "$_" }
        if ($LASTEXITCODE -ne 0) {
            Write-Err 'Failed to install frontend dependencies.'
            Write-Host "    Try manually: cd frontend; npm ci"
            exit 1
        }
    } finally { Pop-Location }
    Write-Ok 'Frontend dependencies installed.'
}

$nodeModules = Join-Path $FrontendDir 'node_modules'
if ($Setup) {
    Install-FrontendDeps
    Write-Host "`nSetup complete. Start the dev server with: .\start.ps1" -ForegroundColor Green
    exit 0
}
if (-not (Test-Path (Join-Path $nodeModules '.package-lock.json'))) {
    Install-FrontendDeps
} else {
    Write-Ok 'Frontend dependencies present.'
}

# --- 4. Backend proxy target (informational) ---------------------------------
try {
    $bh = Invoke-WebRequest -Uri "$BackendOrigin/api/v1/health" -UseBasicParsing -TimeoutSec 3
    if ($bh.StatusCode -eq 200) { Write-Ok "Backend reachable at $BackendOrigin (proxy target)." }
    else { Write-Warn "Backend at $BackendOrigin answered with $($bh.StatusCode); /api calls may fail." }
} catch {
    Write-Warn "Backend not reachable at $BackendOrigin - /api calls will fail until it runs (start it with .\run.ps1)."
}

# --- 5. Verify the port is free ---------------------------------------------
Write-Step "Checking that $Host127`:$Port is available..."
try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
    $listener.Start()
    $listener.Stop()
    Write-Ok "Port $Port is free."
} catch {
    Write-Err "Port $Port is in use."
    Write-Host '    The dev server uses strictPort and will refuse to start. Try: .\start.ps1 -Port 5174'
    Write-Host '    This script will not kill an unrelated process holding the port.'
    exit 1
}

# --- 6. Start the dev server -------------------------------------------------
$env:MATHMOTION_BACKEND_ORIGIN = $BackendOrigin
$devServerProc = $null

Write-Step "Starting Vite on $DevUrl (proxying /api to $BackendOrigin) ..."
$devServerProc = Start-Process -FilePath $node.Source `
    -ArgumentList @($ViteJs, '--port', "$Port", '--strictPort', '--host', $Host127) `
    -WorkingDirectory $FrontendDir `
    -PassThru -NoNewWindow

# --- 7. Wait for the dev server to answer ------------------------------------
Write-Step 'Waiting for the dev server...'
$ready = $false
$deadline = (Get-Date).AddSeconds(60)
while ((Get-Date) -lt $deadline) {
    if ($devServerProc.HasExited) {
        Write-Err "The dev server exited early (code $($devServerProc.ExitCode))."
        Write-Host '    Run: cd frontend; npm run dev   to see the full error output.'
        break
    }
    try {
        $resp = Invoke-WebRequest -Uri $DevUrl -UseBasicParsing -TimeoutSec 3
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}
if ($ready) { Write-Ok "Dev server ready at $DevUrl" }
elseif (-not $devServerProc.HasExited) {
    Write-Err 'The dev server did not become ready in 60s. It is still running; check the log above.'
}

# --- 8. Open the default browser ---------------------------------------------
if ($ready -and -not $NoBrowser) {
    Write-Step 'Opening your browser...'
    try { Start-Process $DevUrl } catch { Write-Warn "Could not open a browser automatically. Visit $DevUrl" }
}

Write-Host "`n  Dev server: $DevUrl" -ForegroundColor White
Write-Host "  Backend:    $BackendOrigin (start with .\run.ps1 if not running)" -ForegroundColor White
Write-Host "  Process:    PID $($devServerProc.Id)" -ForegroundColor White
Write-Host "  Stop:       Press Ctrl+C in this window, or run .\stop.ps1 -Frontend`n" -ForegroundColor White

# --- 9. Track the child and shut down cleanly on exit / interrupt ------------
$cleanupBlock = {
    if ($global:DevServerProc -and -not $global:DevServerProc.HasExited) {
        try { Stop-Process -Id $global:DevServerProc.Id -Force -ErrorAction SilentlyContinue } catch {}
    }
}
$global:DevServerProc = $devServerProc

Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action $cleanupBlock | Out-Null
try {
    while (-not $devServerProc.HasExited) { Start-Sleep -Seconds 1 }
} finally {
    & $cleanupBlock
    Write-Host "`nDev server stopped." -ForegroundColor DarkGray
}
