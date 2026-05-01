#!/bin/bash
# ============================================================
# start.sh — Zovrix AI Kenya server startup (WSL + venv)
# Run: bash start.sh
# Logs: logs/uvicorn.log (also prints to terminal)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Activate venv ─────────────────────────────────────────
if [ ! -f "venv/bin/activate" ]; then
  echo "[START] ERROR: venv not found at $SCRIPT_DIR/venv"
  echo "[START] Run: python3 -m venv venv && pip install -r requirements.txt"
  exit 1
fi
source venv/bin/activate
echo "[START] venv activated"

# ── Create logs dir ───────────────────────────────────────
mkdir -p logs

# ── Kill any existing uvicorn on port 8000 ────────────────
existing=$(lsof -ti:8000 2>/dev/null || true)
if [ -n "$existing" ]; then
  echo "[START] Killing existing process on port 8000 (PID $existing)"
  kill -9 $existing 2>/dev/null || true
  sleep 1
fi

# ── Verify import ─────────────────────────────────────────
echo "[START] Verifying app import..."
python -c "from app.main import app; print('[START] Import OK')" || {
  echo "[START] IMPORT FAILED — check app/main.py"
  exit 1
}

# ── Start uvicorn ─────────────────────────────────────────
echo "[START] Starting uvicorn on port 8000..."
echo "[START] Logs: logs/uvicorn.log + terminal"
echo "[START] Health: curl http://localhost:8000/health"
echo "[START] CloudOven webhook: POST /webhook/cloud_oven"
echo "[START] Kisha-Tech webhook: POST /webhook/kisha_tech"
echo "============================================================"

# Tee output to both terminal and log file
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level info \
  --access-log \
  2>&1 | tee -a logs/uvicorn.log