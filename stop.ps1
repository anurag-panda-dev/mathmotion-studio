<#
.SYNOPSIS
    Stop a MathMotion Studio backend (run.ps1) and/or frontend dev server (start.ps1).

.DESCRIPTION
    Finds processes listening on the backend port (default 8765) and the
    frontend dev-server port (default 5173) and stops only those processes.
    It will not kill unrelated processes. If a port is not in use, it reports
    that nothing was running there. By default both services are stopped;
    use -Backend or -Frontend to target only one.

.PARAMETER Port
    The port the backend was started on (default 8765, or MATHMOTION_PORT).

.PARAMETER FrontendPort
    The port the frontend dev server was started on (default 5173, or
    MATHMOTION_FRONTEND_PORT).

.PARAMETER Backend
    Stop only the backend. Do not touch the frontend dev server.

.PARAMETER Frontend
    Stop only the frontend dev server. Do not touch the backend.

.EXAMPLE
    .\stop.ps1
    .\stop.ps1 -Backend
    .\stop.ps1 -Frontend
    .\stop.ps1 -Port 9000 -FrontendPort 5174
#>
[CmdletBinding()]
param(
    [int]$Port = 0,
    [int]$FrontendPort = 0,
    [switch]$Backend,
    [switch]$Frontend
)

$ErrorActionPreference = 'SilentlyContinue'

if ($Port -le 0) {
    $envPort = $env:MATHMOTION_PORT
    if ($envPort -and [int]::TryParse($envPort, [ref]$null)) { $Port = [int]$envPort }
    else { $Port = 8765 }
}
if ($FrontendPort -le 0) {
    $envPort = $env:MATHMOTION_FRONTEND_PORT
    if ($envPort -and [int]::TryParse($envPort, [ref]$null)) { $FrontendPort = [int]$envPort }
    else { $FrontendPort = 5173 }
}

# With neither switch: stop both. With -Backend: backend only. With -Frontend:
# frontend only. Both switches together: both (same as neither).
$stopBackend   = $Backend -or (-not $Frontend)
$stopFrontend  = $Frontend -or (-not $Backend)

function Write-Ok($msg)   { Write-Host "  [ok] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [!!] $msg" -ForegroundColor Yellow }

function Stop-PortListener([int]$listenPort, [string]$label) {
    $connections = Get-NetTCPConnection -LocalPort $listenPort -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        Write-Warn "Nothing is listening on port $listenPort ($label). Nothing to stop."
        return
    }
    foreach ($conn in $connections) {
        $procId = $conn.OwningProcess
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  [..] Stopping $label PID $procId ($($proc.ProcessName)) on port $listenPort ..."
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            # Stop-Process returns before full teardown; poll briefly for exit.
            $deadline = (Get-Date).AddSeconds(5)
            while ((Get-Date) -lt $deadline -and (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
                Start-Sleep -Milliseconds 200
            }
            if (-not (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
                Write-Ok "Stopped $label PID $procId."
            } else {
                Write-Warn "PID $procId did not stop. It may need elevation."
            }
        }
    }
}

if ($stopBackend)   { Stop-PortListener $Port 'backend' }
if ($stopFrontend)  { Stop-PortListener $FrontendPort 'frontend' }
