<#
.SYNOPSIS
    Clean generated artifacts for MathMotion Studio.

.DESCRIPTION
    Removes runtime data (the local SQLite database, logs, job scratch dirs)
    and/or generated videos from output/. Each target is opt-in via a switch so
    nothing is deleted by accident. The virtual environment and node_modules are
    only removed with -Everything. This never touches source files.

.PARAMETER Data
    Remove the local database, logs, and job scratch directories under data/.

.PARAMETER Output
    Remove generated videos and media under output/.

.PARAMETER Everything
    All of the above, plus .venv and frontend/node_modules.

.EXAMPLE
    .\scripts\cleanup.ps1 -Data
    .\scripts\cleanup.ps1 -Output
    .\scripts\cleanup.ps1 -Everything
#>
[CmdletBinding()]
param(
    [switch]$Data,
    [switch]$Output,
    [switch]$Everything
)

$ErrorActionPreference = 'SilentlyContinue'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Write-Ok($m)  { Write-Host "  [ok] $m" -ForegroundColor Green }
function Write-Skip($m) { Write-Host "  [--] $m" -ForegroundColor DarkGray }

if (-not ($Data -or $Output -or $Everything)) {
    Write-Host "`nNothing selected. Pass -Data, -Output, or -Everything." -ForegroundColor Yellow
    Write-Host "  -Data      remove the local database, logs, and job scratch dirs"
    Write-Host "  -Output    remove generated videos under output/"
    Write-Host "  -Everything  all of the above plus .venv and node_modules`n"
    exit 0
}
if ($Everything) { $Data = $true; $Output = $true }

Write-Host "`nMathMotion Studio - cleanup" -ForegroundColor White
Write-Host ("-" * 40)

if ($Data) {
    $dataDir = Join-Path $ProjectRoot 'data'
    foreach ($sub in @('logs', 'jobs', 'sources')) {
        $p = Join-Path $dataDir $sub
        if (Test-Path $p) { Remove-Item $p -Recurse -Force; Write-Ok "removed data\$sub" }
        else { Write-Skip "data\$sub (not present)" }
    }
    $db = Join-Path $dataDir 'mathmotion.db'
    if (Test-Path $db) { Remove-Item $db -Force; Write-Ok 'removed data\mathmotion.db' }
    else { Write-Skip 'data\mathmotion.db (not present)' }
    $rs = Join-Path $dataDir 'run-state.json'
    if (Test-Path $rs) { Remove-Item $rs -Force; Write-Ok 'removed data\run-state.json' }
}

if ($Output) {
    $outDir = Join-Path $ProjectRoot 'output'
    if (Test-Path $outDir) {
        $files = Get-ChildItem $outDir -Recurse -File -ErrorAction SilentlyContinue
        if ($files) {
            $files | Remove-Item -Force
            Write-Ok "removed $($files.Count) generated file(s) under output/"
        } else { Write-Skip 'output/ (empty)' }
    } else { Write-Skip 'output/ (not present)' }
}

if ($Everything) {
    $venv = Join-Path $ProjectRoot '.venv'
    if (Test-Path $venv) { Remove-Item $venv -Recurse -Force; Write-Ok 'removed .venv' }
    else { Write-Skip '.venv (not present)' }
    $nm = Join-Path $ProjectRoot 'frontend\node_modules'
    if (Test-Path $nm) { Remove-Item $nm -Recurse -Force; Write-Ok 'removed frontend\node_modules' }
    else { Write-Skip 'frontend\node_modules (not present)' }
    Write-Host "  [!!] Re-run .\run.ps1 -Setup (or scripts\setup.ps1) before starting again." -ForegroundColor Yellow
}

Write-Host ""
