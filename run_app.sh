#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
PORT=8000

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Virtual environment not found at $VENV_PYTHON"
  echo "Create it with: python3 -m venv .venv"
  exit 1
fi

if lsof -ti tcp:"$PORT" >/dev/null 2>&1; then
  echo "Port $PORT is already in use. Stopping existing process..."
  kill $(lsof -ti tcp:"$PORT")
  sleep 1
fi

cd "$BACKEND_DIR"

echo "Starting Parallax app..."
echo "Open: http://127.0.0.1:$PORT"
exec "$VENV_PYTHON" -m uvicorn main:app --host 127.0.0.1 --port "$PORT"
