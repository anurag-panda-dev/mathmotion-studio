<#
.SYNOPSIS
    Environment and dependency diagnostics for MathMotion Studio.

.DESCRIPTION
    Reports the status of every dependency the app relies on - Python version,
    virtual environment, backend packages, FFmpeg, optional LaTeX, optional
    Manim, port availability, and directory sizes - without starting the server.
    Everything reported is measured, never assumed.

.EXAMPLE
    .\scripts\diagnostics.ps1
#>
[CmdletBinding()]
param(
    [int]$Port = 0
)

$ErrorActionPreference = 'SilentlyContinue'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir  = Join-Path $ProjectRoot 'backend'
$VenvDir     = Join-Path $ProjectRoot '.venv'
$VenvPython  = Join-Path $VenvDir 'Scripts\python.exe'

if ($Port -le 0) {
    $envPort = $env:MATHMOTION_PORT
    if ($envPort -and [int]::TryParse($envPort, [ref]$null)) { $Port = [int]$envPort }
    else { $Port = 8765 }
}

function Row($name, $status, $detail) {
    $color = switch ($status) {
        'ok'        { 'Green' }
        'warn'      { 'Yellow' }
        'missing'   { 'Red' }
        default     { 'Gray' }
    }
    $tag = $status.ToUpper().PadRight(7)
    Write-Host ("  {0} {1}" -f $tag, $name.PadRight(14)) -ForegroundColor $color -NoNewline
    if ($detail) { Write-Host $detail } else { Write-Host "" }
}

Write-Host "`nMathMotion Studio - diagnostics" -ForegroundColor White
Write-Host ("-" * 50)

# Python (venv).
if (Test-Path $VenvPython) {
    $v = (& $VenvPython -c 'import sys; print(str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]))' 2>$null)
    Row 'venv python' 'ok' "$v  ($VenvPython)"
} else {
    Row 'venv python' 'missing' "not created yet - run .\run.ps1 -Setup"
}

# Backend packages via the venv.
if (Test-Path $VenvPython) {
    $env:PYTHONPATH = $BackendDir
    & $VenvPython -c @"
import json, sys
sys.path.insert(0, r'$BackendDir')
from app.services import diagnostics
from app.core import config
s = config.get_settings()
print(json.dumps(diagnostics.health_payload(s)))
"@ | ForEach-Object {
        try {
            $h = $_ | ConvertFrom-Json
            foreach ($d in $h.dependencies) {
                $st = if ($d.available) { 'ok' } elseif ($d.name -eq 'latex') { 'warn' } else { 'missing' }
                $ver = ''
                if ($d.version) { $ver = [string]$d.version }
                $det = ''
                if ($d.detail) { $det = '-- ' + [string]$d.detail }
                $info = ($ver + ' ' + $det).Trim()
                Row $d.name $st $info
            }
            Row 'app version' 'ok' ("$($h.version)  (scene format $($h.scene_format_version))")
            $feStatus = if ($h.frontend_built) { 'ok' } else { 'warn' }
            $feDetail = if ($h.frontend_built) { 'built (dist/ present)' } else { 'not built -- backend serves a status page at /' }
            Row 'frontend' $feStatus $feDetail
        } catch {}
    }
}

# Port availability.
$conn = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
if ($conn.TcpTestSucceeded) { Row "port $Port" 'warn' 'in use - a server may already be running' }
else { Row "port $Port" 'ok' 'free' }

# Directory sizes.
function DirSize($path) {
    if (-not (Test-Path $path)) { return 0 }
    $bytes = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    if (-not $bytes) { return 0 }
    return [math]::Round($bytes / 1MB, 2)
}
Write-Host ""
Row 'data dir' 'ok' "$(DirSize (Join-Path $ProjectRoot 'data')) MB"
Row 'output dir' 'ok' "$(DirSize (Join-Path $ProjectRoot 'output')) MB"

Write-Host ""
