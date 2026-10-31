#!/usr/bin/env bash
# Start the API on port 8000 and the Vite dev server on port 5173.
set -euo pipefail
cd "$(dirname "$0")"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

cleanup() {
  trap - INT TERM EXIT
  kill 0 2>/dev/null || true
}
trap cleanup INT TERM EXIT

uvicorn app.main:app --reload --port 8000 &
(cd frontend && npm run dev) &
wait
