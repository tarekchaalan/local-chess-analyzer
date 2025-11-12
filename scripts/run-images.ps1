#!/usr/bin/env pwsh
Param(
  [string]$ImageOwner = $env:IMAGE_OWNER,
  [string]$Tag = $env:TAG
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host $msg }
function Write-Err($msg) { Write-Host $msg -ForegroundColor Red }

# Ensure Docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Err "Docker is not installed or not in PATH. Please install Docker Desktop and retry."
  exit 1
}

function Start-DockerDesktop {
  try {
    $paths = @(
      Join-Path $Env:ProgramFiles "Docker\Docker\Docker Desktop.exe"),
      (Join-Path ${Env:ProgramFiles(x86)} "Docker\Docker\Docker Desktop.exe")
    foreach ($p in $paths) {
      if ($p -and (Test-Path $p)) {
        Start-Process -FilePath $p | Out-Null
        return
      }
    }
    # Fallback by app name (if registered)
    Start-Process -FilePath "Docker Desktop" -ErrorAction SilentlyContinue | Out-Null
  } catch {
    # ignore
  }
}

function Start-DockerIfNeeded {
  param([int]$TimeoutSec = 120)
  try {
    docker info | Out-Null
    return $true
  } catch {
    Write-Info "Attempting to start Docker Desktop..."
    Start-DockerDesktop
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
      try {
        docker info | Out-Null
        return $true
      } catch {
        Start-Sleep -Seconds 2
      }
    }
    return $false
  }
}

if (-not (Start-DockerIfNeeded -TimeoutSec 120)) {
  Write-Err "Docker daemon not running. Start Docker Desktop and retry."
  exit 1
}

# Defaults
if (-not $ImageOwner) { $ImageOwner = "tarekchaalan" }
if (-not $Tag) { $Tag = "latest" }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path


# Try to run the Bash script if available (Git Bash)
$Bash = Get-Command bash -ErrorAction SilentlyContinue
if ($Bash) {
  Write-Info "Detected Bash. Delegating to scripts/run-images.sh..."
  # Convert Windows path to a Git Bash/MSYS-friendly path and invoke via login shell
  function Convert-ToMsysPath([string]$winPath) {
    if ($winPath -match '^[A-Za-z]:\\') {
      $drive = $winPath.Substring(0,1).ToLower()
      $rest = $winPath.Substring(2).Replace('\','/')
      return "/$drive/$rest"
    }
    return $winPath.Replace('\','/')
  }
  $msysDir = Convert-ToMsysPath $ScriptDir
  $cmd = "cd '$msysDir' && IMAGE_OWNER='$ImageOwner' TAG='$Tag' bash ./run-images.sh"
  & $Bash -lc "$cmd"
  exit $LASTEXITCODE
}

# Try WSL
$WSL = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($WSL) {
  Write-Info "No Bash found in PATH. Falling back to WSL..."
  $winPath = Join-Path $ScriptDir "run-images.sh"
  # Convert to WSL path
  $wslPath = & wsl.exe wslpath -a "$winPath"
  if (-not $wslPath) {
    Write-Err "Failed to convert path to WSL path."
    exit 1
  }
  $wslDir = & wsl.exe dirname "$wslPath"
  # Build env prefix for WSL
  $envPrefix = ""
  if ($ImageOwner) { $envPrefix += " IMAGE_OWNER='$ImageOwner'" }
  if ($Tag) { $envPrefix += " TAG='$Tag'" }
  $cmd = "cd '$wslDir' &&$envPrefix bash ./run-images.sh"
  & wsl.exe bash -lc "$cmd"
  exit $LASTEXITCODE
}

Write-Err "Neither Git Bash (bash) nor WSL was found."
Write-Host "Install Git for Windows (which includes Git Bash) or WSL, then retry." -ForegroundColor Yellow
exit 1


