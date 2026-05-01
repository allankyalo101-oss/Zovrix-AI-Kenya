#!/bin/bash
# ============================================================
# expose.sh — Expose localhost:8000 to the internet via ngrok
# Twilio needs a public HTTPS URL to send webhook callbacks.
# WSL localhost is not reachable from Twilio directly.
#
# First-time setup:
#   1. Sign up free at https://ngrok.com
#   2. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
#   3. Run: ngrok config add-authtoken <your-token>
#   4. Then run this script: bash expose.sh
#
# After running, update BOTH Twilio consoles with:
#   CloudOven webhook:  https://<ngrok-url>/webhook/cloud_oven
#   Kisha-Tech webhook: https://<ngrok-url>/webhook/kisha_tech
#
# IMPORTANT: ngrok URL changes every restart on free plan.
# When you see the URL in terminal, update Twilio consoles immediately.
# ============================================================

# Check ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "[EXPOSE] ngrok not found. Installing..."
    # For Ubuntu/WSL
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update -qq && sudo apt install ngrok -y
fi

# Check uvicorn is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "[EXPOSE] Uvicorn not running. Start it first: bash start.sh"
    echo "[EXPOSE] Or in another terminal: source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "[EXPOSE] Uvicorn confirmed running on port 8000"
echo "[EXPOSE] Starting ngrok tunnel..."
echo ""
echo "============================================================"
echo "  After ngrok starts, copy the HTTPS URL shown below"
echo "  and update both Twilio consoles:"
echo ""
echo "  CloudOven:https://cloudoven-backend.onrender.com/webhook/whatsapp?client_id=cloud_oven
echo "  Kisha-Tech:https://kisha-tech-backend.onrender.com/webhook/whatsapp?client_id=kisha_tech
echo "============================================================"
echo ""

ngrok http 8000