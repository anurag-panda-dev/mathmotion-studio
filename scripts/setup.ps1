<#
.SYNOPSIS
    One-time setup for MathMotion Studio.

.DESCRIPTION
    Creates the Python virtual environment, installs backend dependencies and
    the optional Manim render dependencies, and prepares the data/output
    directories. This is the same setup run.ps1 performs, exposed on its own so
    it can be run ahead of time or in CI.

.EXAMPLE
    .\scripts\setup.ps1
    .\scripts\setup.ps1 -SkipRenderDeps
#>
[CmdletBinding()]
param(
    [switch]$SkipRenderDeps
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir  = Join-Path $ProjectRoot 'backend'
$VenvDir     = Join-Path $ProjectRoot '.venv'
$VenvPython  = Join-Path $VenvDir 'Scripts\python.exe'

function Write-Step($m) { Write-Host "  [..] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "  [ok] $m" -ForegroundColor Green }
function Write-Err($m)  { Write-Host "  [XX] $m" -ForegroundColor Red }

Write-Host "`nMathMotion Studio - setup" -ForegroundColor White
Write-Host ("-" * 40)

# Locate Python 3.11+.
$PythonExe = $null
$py = Get-Command 'py' -ErrorAction SilentlyContinue
if ($py) {
    $real = (& py -3.11 -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1)
    if ($real -and (Test-Path $real.Trim())) { $PythonExe = $real.Trim() }
}
if (-not $PythonExe) {
    foreach ($c in @('python', 'python3')) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd) {
            $v = (& $cmd.Source -c 'import sys; print(str(sys.version_info[0]) + "." + str(sys.version_info[1]))' 2>$null)
            if ($v -and [version]"$v".Trim() -ge [version]'3.11') { $PythonExe = $cmd.Source; break }
        }
    }
}
if (-not $PythonExe) {
    Write-Err 'Python 3.11+ not found. Install from https://www.python.org/downloads/'
    exit 1
}
Write-Ok "Python: $PythonExe"

# Create the venv.
if (-not (Test-Path $VenvPython)) {
    Write-Step "Creating venv at $VenvDir ..."
    & $PythonExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { Write-Err 'venv creation failed.'; exit 1 }
    Write-Ok 'venv created.'
} else {
    Write-Ok 'venv present.'
}

# Install dependencies.
Write-Step 'Installing backend dependencies...'
& $VenvPython -m pip install --quiet --upgrade pip | Out-Null
& $VenvPython -m pip install --quiet -r (Join-Path $BackendDir 'requirements.txt')
if ($LASTEXITCODE -ne 0) { Write-Err 'backend dependency install failed.'; exit 1 }
Write-Ok 'backend dependencies installed.'

if (-not $SkipRenderDeps) {
    $render = Join-Path $BackendDir 'requirements-render.txt'
    if (Test-Path $render) {
        Write-Step 'Installing optional render dependencies (Manim)...'
        & $VenvPython -m pip install --quiet -r $render
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [!!] Manim install failed - rendering unavailable, validation/prompt still work." -ForegroundColor Yellow
        } else {
            Write-Ok 'render dependencies installed.'
        }
    }
}

# Stamp for run.ps1's incremental-install check.
Set-Content -Path (Join-Path $VenvDir '.deps-installed') -Value (Get-Date).ToString('o')

# Prepare runtime directories (harmless if present).
foreach ($d in @('data', 'data\logs', 'data\jobs', 'data\sources', 'output')) {
    $p = Join-Path $ProjectRoot $d
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}
Write-Ok 'runtime directories ready.'

Write-Host "`nSetup complete. Start with: .\run.ps1" -ForegroundColor Green
