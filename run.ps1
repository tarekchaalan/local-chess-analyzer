# Build the frontend and run Local Chess Analyzer (Windows, PowerShell).
#   .\run.ps1              build + serve on http://127.0.0.1:42069 (opens your browser)
#   .\run.ps1 -Dev         hot-reload: backend on :42069, Vite on :5173
#   .\run.ps1 -NoBuild     skip the frontend build (reuse frontend\dist)
param([switch]$Dev, [switch]$NoBuild)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Need($cmd, $hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { Write-Error "'$cmd' is required — $hint" }
}
function Run($label, $dir, [scriptblock]$block) {
  Write-Host "> $label" -ForegroundColor Cyan
  Push-Location $dir
  try { & $block; if ($LASTEXITCODE) { throw "$label failed (exit $LASTEXITCODE)" } }
  finally { Pop-Location }
}

Need uv  'install from https://docs.astral.sh/uv/'
Need npm 'install Node 22 from https://nodejs.org/'

Run 'backend dependencies'  backend  { uv sync --quiet }
Run 'stockfish'             backend  { uv run --no-sync fetch-stockfish }
Run 'frontend dependencies' frontend { npm install --no-audit --no-fund --loglevel=error }

if ($Dev) {
  Write-Host '> dev servers (close this window to stop both)' -ForegroundColor Cyan
  $api = Start-Process -PassThru -NoNewWindow -WorkingDirectory backend uv -ArgumentList 'run','--no-sync','uvicorn','lca.main:app','--reload','--port','42069'
  try { Push-Location frontend; npm run dev } finally { Pop-Location; if (-not $api.HasExited) { Stop-Process -Id $api.Id } }
  exit 0
}

if (-not $NoBuild) { Run 'frontend build' frontend { npm run build } }

Write-Host '> starting — http://127.0.0.1:42069  (Ctrl+C to stop)' -ForegroundColor Cyan
Set-Location backend
uv run --no-sync lca
