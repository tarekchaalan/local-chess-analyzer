#!/usr/bin/env pwsh

Param(
  [string]$ImageOwner = $env:IMAGE_OWNER,
  [string]$Tag = $env:TAG
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host $msg }
function Write-Err($msg)  { Write-Host $msg -ForegroundColor Red }

# Ensure docker CLI exists
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Err "Docker is not installed or not in PATH. Install Docker Desktop and retry."
  exit 1
}

# Ensure Docker Desktop is running and in Linux engine
$dockerCli = Join-Path $Env:ProgramFiles "Docker\Docker\DockerCli.exe"
if (Test-Path $dockerCli) {
  try { & $dockerCli -SwitchLinuxEngine | Out-Null } catch { }
}

function Start-DockerDesktop {
  try {
    $paths = @(
      (Join-Path $Env:ProgramFiles        "Docker\Docker\Docker Desktop.exe"),
      (Join-Path ${Env:ProgramFiles(x86)} "Docker\Docker\Docker Desktop.exe")
    )
    foreach ($p in $paths) {
      if ($p -and (Test-Path $p)) {
        Start-Process -FilePath $p | Out-Null
        return
      }
    }
    # Fallback by app name
    Start-Process -FilePath "Docker Desktop" -ErrorAction SilentlyContinue | Out-Null
  } catch { }
}

function Set-DockerLinuxEngine {
  # If server is up but in Windows-engine mode, switch
  try {
    $serverOs = docker info -f '{{.Server.Os}}' 2>$null
    if ($serverOs -and $serverOs -ne 'linux') {
      Write-Info "Switching Docker Desktop to Linux engine..."
      $cli = Join-Path $Env:ProgramFiles "Docker\Docker\DockerCli.exe"
      if (Test-Path $cli) {
        & $cli -SwitchLinuxEngine | Out-Null
      }
    }
  } catch { }
}

function Start-DockerIfNeeded {
  param([int]$TimeoutSec = 180)
  try { docker info | Out-Null; Set-DockerLinuxEngine; return $true } catch { }
  Write-Info "Attempting to start Docker Desktop..."
  Start-DockerDesktop
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try {
      docker info | Out-Null
      Set-DockerLinuxEngine
      # re-check pipe after switch
      docker info | Out-Null
      return $true
    } catch {
      Start-Sleep -Seconds 2
    }
  }
  return $false
}

if (-not (Start-DockerIfNeeded -TimeoutSec 180)) {
  Write-Err "Docker daemon not running. Start Docker Desktop and retry."
  exit 1
}

# Defaults
if (-not $ImageOwner) { $ImageOwner = "tarekchaalan" }
if (-not $Tag)        { $Tag = "latest" }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Prefer Git Bash and run the shared bash launcher
$GitBashPathCandidates = @(
  (Join-Path $Env:ProgramFiles "Git\bin\bash.exe"),
  (Join-Path ${Env:ProgramFiles(x86)} "Git\bin\bash.exe")
)
$GitBash = $null
foreach ($p in $GitBashPathCandidates) { if (Test-Path $p) { $GitBash = $p; break } }
if (-not $GitBash) {
  $cmd = Get-Command bash -ErrorAction SilentlyContinue
  if ($cmd) { $GitBash = $cmd.Source }
}
if ($GitBash) {
  Write-Info "Detected Bash. Delegating to scripts/run-images.sh..."
  function Convert-ToMsysPath([string]$winPath) {
    if ($winPath -match '^[A-Za-z]:\\') {
      $drive = $winPath.Substring(0,1).ToLower()
      $rest  = $winPath.Substring(2).Replace('\','/')
      return "/$drive/$rest"
    }
    return $winPath.Replace('\','/')
  }
  $msysDir = Convert-ToMsysPath (Split-Path -Parent $MyInvocation.MyCommand.Path)
  $envLine = ""
  if ($ImageOwner) { $envLine += " IMAGE_OWNER='$ImageOwner'" }
  if ($Tag)        { $envLine += " TAG='$Tag'" }
  $cmd = @"
cd '$msysDir'
$envLine bash ./run-images.sh
"@
  & $GitBash -lc $cmd
  exit $LASTEXITCODE
}

# Fallback: WSL
$WSL = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($WSL) {
  Write-Info "No Bash found in PATH. Falling back to WSL..."
  $winPath = Join-Path $ScriptDir "run-images.sh"
  $wslPath = & wsl.exe wslpath -a "$winPath"
  if (-not $wslPath) { Write-Err "Failed to convert path to WSL path."; exit 1 }
  $wslDir  = & wsl.exe dirname "$wslPath"
  $envPref = ""
  if ($ImageOwner) { $envPref += " IMAGE_OWNER='$ImageOwner'" }
  if ($Tag)        { $envPref += " TAG='$Tag'" }
  $cmd = "cd '$wslDir' &&$envPref bash ./run-images.sh"
  & wsl.exe bash -lc "$cmd"
  exit $LASTEXITCODE
}

Write-Err "Neither Git Bash (bash) nor WSL was found."
Write-Host "Install Git for Windows (with Git Bash) or enable WSL, then retry." -ForegroundColor Yellow
exit 1
