#!/usr/bin/env sh
# Build the frontend and run Local Chess Analyzer (macOS / Linux).
#   ./run.sh              build + serve on http://127.0.0.1:42069 (opens your browser)
#   ./run.sh --dev        hot-reload: backend on :42069, Vite on :5173
#   ./run.sh --no-build   skip the frontend build (reuse frontend/dist)
set -eu
cd "$(dirname "$0")"

need() { command -v "$1" >/dev/null 2>&1 || { echo "error: '$1' is required - $2" >&2; exit 1; }; }
need uv  "install from https://docs.astral.sh/uv/"
need npm "install Node 22 from https://nodejs.org/"

DEV=0; BUILD=1
for arg in "$@"; do
  case "$arg" in
    --dev) DEV=1 ;;
    --no-build) BUILD=0 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

echo "> backend dependencies"
( cd backend && uv sync --quiet )

echo "> stockfish"
( cd backend && uv run --no-sync fetch-stockfish )

echo "> frontend dependencies"
( cd frontend && npm install --no-audit --no-fund --loglevel=error )

if [ "$DEV" = 1 ]; then
  echo "> dev servers (Ctrl+C stops both)"
  trap 'kill 0' INT TERM EXIT
  ( cd backend && uv run --no-sync uvicorn lca.main:app --reload --port 42069 ) &
  ( cd frontend && npm run dev )
  exit 0
fi

if [ "$BUILD" = 1 ]; then
  echo "> frontend build"
  ( cd frontend && npm run build )
fi

echo "> starting - http://127.0.0.1:42069  (Ctrl+C to stop)"
cd backend && exec uv run --no-sync lca
