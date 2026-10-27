<#
.SYNOPSIS
    MathMotion Studio launcher.

.DESCRIPTION
    Determines the project root from this script's own location, verifies
    Windows/PowerShell and the required Python version, creates the virtual
    environment if missing, installs backend (and optional render) dependencies
    when needed, verifies the local port is free, starts the backend with the
    virtual environment's interpreter, waits for the health endpoint, and opens
    the default browser. Child processes started here are tracked and shut down
    cleanly on exit or Ctrl+C. The script never requires administrator rights
    and never kills an unrelated process that happens to hold the port.

.PARAMETER Setup
    Only create the virtual environment and install dependencies, then exit.
    Does not start the server or open a browser.

.PARAMETER Dev
    Run the backend with reload enabled for development.

.PARAMETER Diagnostics
    Report environment and dependency status (Python, FFmpeg, Manim, LaTeX,
    port, directories) without starting the server.

.PARAMETER Port
    Override the TCP port (default 8765). Must be free unless -ForcePort.

.PARAMETER SkipRenderDeps
    Do not attempt to install the optional Manim render dependencies.

.PARAMETER NoBrowser
    Start the server but do not open a browser.

.EXAMPLE
    .\run.ps1
    .\run.ps1 -Setup
    .\run.ps1 -Dev
    .\run.ps1 -Diagnostics
    .\run.ps1 -Port 9000
#>
[CmdletBinding()]
param(
    [switch]$Setup,
    [switch]$Dev,
    [switch]$Diagnostics,
    [int]$Port = 0,
    [switch]$SkipRenderDeps,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'

# --- 1. Project root from this script's own location -------------------------
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
$BackendDir  = Join-Path $ProjectRoot 'backend'
$VenvDir     = Join-Path $ProjectRoot '.venv'
$VenvPython  = Join-Path $VenvDir 'Scripts\python.exe'

# Resolve the port: -Port argument, else MATHMOTION_PORT env, else 8765.
if ($Port -le 0) {
    $envPort = $env:MATHMOTION_PORT
    if ($envPort -and [int]::TryParse($envPort, [ref]$null)) { $Port = [int]$envPort }
    else { $Port = 8765 }
}
$Host127 = '127.0.0.1'
$AppUrl  = "http://$Host127`:$Port"
$HealthUrl = "$AppUrl/api/v1/health"

function Write-Step($msg)  { Write-Host "  [..] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "  [ok] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "  [!!] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "  [XX] $msg" -ForegroundColor Red }

# --- 2. Platform / PowerShell requirements ----------------------------------
Write-Host "`nMathMotion Studio" -ForegroundColor White
Write-Host ("-" * 40)

if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Err "PowerShell 5.1 or newer is required (found $($PSVersionTable.PSVersion))."
    Write-Host "    Update PowerShell: https://aka.ms/powershell-download"
    exit 1
}
if (-not $IsWindows -and $env:OS -ne 'Windows_NT') {
    Write-Warn "This launcher targets Windows. On other platforms run the backend directly."
}

# --- 3. Detect Python (prefer py -3.11 launcher, then python) ---------------
Write-Step 'Checking Python...'
$PythonExe = $null
$PythonVersion = $null

function Get-PyVersion($exe) {
    try {
        $v = & $exe -c "import sys; print('%d.%d' % (sys.version_info[0], sys.version_info[1]))" 2>$null
        return "$v".Trim()
    } catch { return $null }
}

# Try the Windows py launcher at 3.11 first.
$pyLauncher = Get-Command 'py' -ErrorAction SilentlyContinue
if ($pyLauncher) {
    $v = Get-PyVersion 'py -3.11'
    if ($v -eq '3.11') {
        # Confirm the real interpreter path the launcher resolves to.
        $real = (& py -3.11 -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1).Trim()
        if ($real -and (Test-Path $real)) { $PythonExe = $real; $PythonVersion = $v }
    }
}
if (-not $PythonExe) {
    foreach ($cand in @('python', 'python3')) {
        $cmd = Get-Command $cand -ErrorAction SilentlyContinue
        if ($cmd) {
            $v = Get-PyVersion $cmd.Source
            if ($v -and [version]$v -ge [version]'3.11') { $PythonExe = $cmd.Source; $PythonVersion = $v; break }
        }
    }
}
if (-not $PythonExe) {
    Write-Err "Python 3.11+ was not found."
    Write-Host "    Install Python 3.11: https://www.python.org/downloads/ (check 'Add to PATH')"
    Write-Host "    Then re-run: .\run.ps1"
    exit 1
}
Write-Ok "Python $PythonVersion at $PythonExe"

# --- 4. FFmpeg and optional LaTeX (informational) ---------------------------
$ffmpeg = Get-Command 'ffmpeg' -ErrorAction SilentlyContinue
if ($ffmpeg) { Write-Ok "FFmpeg found: $($ffmpeg.Source)" }
else { Write-Warn 'FFmpeg not on PATH - video encoding will fail. Install: winget install ffmpeg' }
$latex = Get-Command 'latex' -ErrorAction SilentlyContinue
if ($latex) { Write-Ok 'LaTeX found (optional: MathTex typography available).' }
else { Write-Warn 'LaTeX not installed (optional). Text fallback will be used for formulas.' }

# --- 5-7. Virtual environment and dependencies ------------------------------
function Ensure-Venv {
    if (-not (Test-Path $VenvPython)) {
        Write-Step "Creating virtual environment at $VenvDir ..."
        & $PythonExe -m venv $VenvDir
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython)) {
            Write-Err 'Failed to create the virtual environment.'
            exit 1
        }
        Write-Ok 'Virtual environment created.'
        return $true   # freshly created -> always install
    }
    Write-Ok 'Virtual environment present.'
    return $false
}

function Install-BackendDeps {
    Write-Step 'Installing backend dependencies...'
    & $VenvPython -m pip install --quiet --upgrade pip | Out-Null
    & $VenvPython -m pip install --quiet -r (Join-Path $BackendDir 'requirements.txt')
    if ($LASTEXITCODE -ne 0) {
        Write-Err 'Failed to install backend dependencies.'
        Write-Host "    Try manually: $VenvPython -m pip install -r backend\requirements.txt"
        exit 1
    }
    Write-Ok 'Backend dependencies installed.'
}

function Install-RenderDeps {
    # Optional: Manim. A failure here is a warning, never fatal.
    $reqRender = Join-Path $BackendDir 'requirements-render.txt'
    if (-not (Test-Path $reqRender)) { return }
    Write-Step 'Installing optional render dependencies (Manim)...'
    & $VenvPython -m pip install --quiet -r $reqRender
    if ($LASTEXITCODE -ne 0) {
        Write-Warn 'Manim install failed - rendering will be unavailable. Validation and prompts still work.'
    } else {
        Write-Ok 'Render dependencies installed.'
    }
}

$created = Ensure-Venv
$stampPath = Join-Path $VenvDir '.deps-installed'
$wantInstall = $created
if (-not $wantInstall) {
    # Reinstall if any requirements file is newer than the install stamp.
    $stampTime = if (Test-Path $stampPath) { (Get-Item $stampPath).LastWriteTime } else { [datetime]::MinValue }
    foreach ($f in @('requirements.txt', 'requirements-render.txt')) {
        $p = Join-Path $BackendDir $f
        if ((Test-Path $p) -and (Get-Item $p).LastWriteTime -gt $stampTime) { $wantInstall = $true }
    }
}
if ($wantInstall) {
    Install-BackendDeps
    if (-not $SkipRenderDeps) { Install-RenderDeps }
    Set-Content -Path $stampPath -Value (Get-Date).ToString('o')
} else {
    Write-Ok 'Dependencies up to date.'
}

if ($Setup) {
    Write-Host "`nSetup complete. Start the app with: .\run.ps1" -ForegroundColor Green
    exit 0
}

# --- 4b. Diagnostics mode ---------------------------------------------------
if ($Diagnostics) {
    Write-Host "`nDiagnostics" -ForegroundColor White
    Write-Host ("-" * 40)
    Write-Step 'Collecting dependency status from the backend...'
    $py = $VenvPython
    $env:PYTHONPATH = $BackendDir
    & $py -c "import json,sys; sys.path.insert(0, r'$BackendDir'); from app.services import diagnostics; from app.core import config; s=config.get_settings(); print(json.dumps({'health': diagnostics.health_payload(s)}, indent=2))"
    if ($LASTEXITCODE -ne 0) { Write-Warn 'Could not collect diagnostics from the backend.' }
    # Port availability
    $conn = Test-NetConnection -ComputerName $Host127 -Port $Port -WarningAction SilentlyContinue
    if ($conn.TcpTestSucceeded) { Write-Warn "Port $Port is already in use (a server may already be running)." }
    else { Write-Ok "Port $Port is free." }
    exit 0
}

# --- 9. Verify the port is free ---------------------------------------------
Write-Step "Checking that $Host127`:$Port is available..."
$listener = $null
try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
    $listener.Start()
    $listener.Stop()
    Write-Ok "Port $Port is free."
} catch {
    Write-Err "Port $Port is in use."
    Write-Host "    Another server may already be running. Try: .\run.ps1 -Port 8766"
    Write-Host "    This script will not kill an unrelated process holding the port."
    exit 1
}

# --- 10. Start the backend --------------------------------------------------
$env:PYTHONPATH = $BackendDir
$env:MATHMOTION_PORT = "$Port"
$env:MATHMOTION_HOST = $Host127

$mainPy = Join-Path $BackendDir 'app\main.py'
$childProcs = @()
$backendProc = $null

Write-Step "Starting backend on $AppUrl ..."
if ($Dev) {
    & $VenvPython -m pip install --quiet uvicorn 2>$null | Out-Null
    $backendProc = Start-Process -FilePath $VenvPython `
        -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', $Host127, '--port', "$Port", '--reload', '--app-dir', $BackendDir) `
        -PassThru -NoNewWindow
} else {
    $backendProc = Start-Process -FilePath $VenvPython `
        -ArgumentList @($mainPy) `
        -PassThru -NoNewWindow `
        -WorkingDirectory $BackendDir
}
$childProcs += $backendProc

# --- 11. Wait for the health endpoint ---------------------------------------
Write-Step 'Waiting for the health endpoint...'
$ready = $false
$deadline = (Get-Date).AddSeconds(60)
while ((Get-Date) -lt $deadline) {
    if ($backendProc.HasExited) {
        Write-Err "The backend exited early (code $($backendProc.ExitCode))."
        Write-Host "    Run .\run.ps1 -Diagnostics to check dependencies."
        break
    }
    try {
        $resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 3
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}
if ($ready) { Write-Ok "Backend ready at $AppUrl" }
else {
    if (-not $backendProc.HasExited) {
        Write-Err 'Backend did not become healthy in 60s. It is still running; check the log above.'
    }
}

# --- 12. Open the default browser -------------------------------------------
if ($ready -and -not $NoBrowser) {
    Write-Step 'Opening your browser...'
    try { Start-Process $AppUrl } catch { Write-Warn "Could not open a browser automatically. Visit $AppUrl" }
}

Write-Host "`n  App:      $AppUrl" -ForegroundColor White
Write-Host "  Health:   $HealthUrl" -ForegroundColor White
Write-Host "  Backend:  PID $($backendProc.Id)" -ForegroundColor White
Write-Host "  Stop:     Press Ctrl+C in this window, or run .\stop.ps1`n" -ForegroundColor White

# --- 14-15. Track children and shut down cleanly on exit / interrupt -------
$cleanupBlock = {
    if ($global:ChildProcs) {
        foreach ($p in $global:ChildProcs) {
            if ($p -and -not $p.HasExited) {
                try { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } catch {}
            }
        }
    }
}
$global:ChildProcs = $childProcs

Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action $cleanupBlock | Out-Null
try {
    # Hold the console until Ctrl+C or the backend exits.
    while (-not $backendProc.HasExited) { Start-Sleep -Seconds 1 }
} finally {
    & $cleanupBlock
    Write-Host "`nShutdown complete." -ForegroundColor DarkGray
}
