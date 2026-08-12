#!/bin/bash
set -euo pipefail

PORT=8000

if lsof -ti tcp:"$PORT" >/dev/null 2>&1; then
  echo "Stopping process on port $PORT..."
  kill $(lsof -ti tcp:"$PORT")
  sleep 1
  echo "Stopped."
else
  echo "No process is listening on port $PORT."
fi
