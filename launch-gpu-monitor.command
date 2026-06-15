#!/bin/zsh
set -e

SCRIPT_DIR="${0:A:h}"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/local-resource-monitor-backend"
FRONTEND_DIR="$PROJECT_ROOT/gpu-monitor-frontend-inspect"
BACKEND_PORT="8765"
FRONTEND_PORT="8000"
APP_URL="http://127.0.0.1:${FRONTEND_PORT}/Resource%20Monitor.live.html"
LOG_DIR="$PROJECT_ROOT/.gpu-monitor-logs"
BACKEND_PYTHON="$BACKEND_DIR/.venv/bin/python"
if [[ ! -x "$BACKEND_PYTHON" ]]; then
  BACKEND_PYTHON="$(command -v python3)"
fi
BACKEND_PID=""
FRONTEND_PID=""

mkdir -p "$LOG_DIR"

port_is_listening() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

cleanup() {
  echo ""
  echo "Stopping GPU Monitor services..."
  if [[ -n "$BACKEND_PID" ]]; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$FRONTEND_PID" ]]; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup INT TERM EXIT

start_backend() {
  if port_is_listening "$BACKEND_PORT"; then
    echo "Backend already running on port $BACKEND_PORT"
    return
  fi

  echo "Starting backend on http://127.0.0.1:$BACKEND_PORT"
  cd "$BACKEND_DIR"
  "$BACKEND_PYTHON" -m resource_monitor_backend --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
  BACKEND_PID="$!"
}

start_frontend() {
  if port_is_listening "$FRONTEND_PORT"; then
    echo "Frontend server already running on port $FRONTEND_PORT"
    return
  fi

  echo "Starting frontend on http://127.0.0.1:$FRONTEND_PORT"
  cd "$FRONTEND_DIR"
  python3 -m http.server "$FRONTEND_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
  FRONTEND_PID="$!"
}

wait_for_url() {
  local url="$1"
  local label="$2"
  for i in {1..30}; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "$label is ready"
      return
    fi
    sleep 0.3
  done

  echo "$label did not become ready. Check logs in $LOG_DIR"
}

start_backend
start_frontend

wait_for_url "http://127.0.0.1:${BACKEND_PORT}/health" "Backend"
wait_for_url "$APP_URL" "Frontend"

echo "Opening $APP_URL"
open "$APP_URL"

echo ""
echo "GPU Monitor is running."
echo "Logs: $LOG_DIR"
echo "Keep this window open while using the app."
echo "Close this window or press Ctrl+C to stop the local services."

while true; do
  sleep 3600
done
