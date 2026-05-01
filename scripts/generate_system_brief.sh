#!/bin/bash

OUTPUT="system_brief_$(date +%Y%m%d_%H%M%S).txt"
ROOT="."

echo "========================================" | tee "$OUTPUT"
echo "CLOUDSTAFF — ARCHITECTURE INTELLIGENCE BRIEF" | tee -a "$OUTPUT"
echo "Timestamp: $(date)" | tee -a "$OUTPUT"
echo "Root Directory: $(realpath $ROOT)" | tee -a "$OUTPUT"
echo "========================================" | tee -a "$OUTPUT"
echo "" | tee -a "$OUTPUT"

########################################
# 1. SYSTEM STRUCTURE
########################################

echo "1. SYSTEM STRUCTURE" | tee -a "$OUTPUT"
echo "Directories discovered:" | tee -a "$OUTPUT"

find . -maxdepth 2 -type d | sort | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 2. CODEBASE DISCOVERY
########################################

echo "2. CODEBASE DISCOVERY" | tee -a "$OUTPUT"

TOTAL_FILES=$(find . -type f -name "*.py" | wc -l)
echo "Total Python files: $TOTAL_FILES" | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"
find . -type f -name "*.py" | sort | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 3. API SURFACE DETECTION
########################################

echo "3. API SURFACE DETECTION" | tee -a "$OUTPUT"

grep -R "@app." -n . 2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 4. INTEGRATION DETECTION
########################################

echo "4. INTEGRATIONS DETECTED" | tee -a "$OUTPUT"

echo "--- Twilio ---" | tee -a "$OUTPUT"
grep -R "twilio" -n . 2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

echo "--- OpenAI ---" | tee -a "$OUTPUT"
grep -R "openai" -n . 2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

echo "--- HTTP Clients ---" | tee -a "$OUTPUT"
grep -R "httpx\|requests" -n . 2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 5. AI / PROCESSING LAYER
########################################

echo "5. AI / PROCESSING LOGIC" | tee -a "$OUTPUT"

grep -R "def .*agent" -n . 2>/dev/null | tee -a "$OUTPUT"
grep -R "def .*process" -n . 2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 6. GOVERNANCE LAYER
########################################

echo "6. GOVERNANCE COMPONENTS" | tee -a "$OUTPUT"

ls governance 2>/dev/null | tee -a "$OUTPUT"

grep -R "ledger" -n governance 2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 7. DATA / CLIENT LAYER
########################################

echo "7. CLIENT DATA STRUCTURE" | tee -a "$OUTPUT"

ls clients 2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 8. ACTIVE SERVICES
########################################

echo "8. ACTIVE SERVICES" | tee -a "$OUTPUT"

echo "Uvicorn:" | tee -a "$OUTPUT"
pgrep -a uvicorn || echo "not running" | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

echo "Ngrok:" | tee -a "$OUTPUT"
pgrep -a ngrok || echo "not running" | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 9. NGROK PUBLIC ENDPOINT
########################################

echo "9. PUBLIC ENTRYPOINT" | tee -a "$OUTPUT"

curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null \
| python3 -c "import sys,json; d=json.load(sys.stdin); print(d['tunnels'][0]['public_url'] if d['tunnels'] else 'no tunnel')" \
2>/dev/null | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

########################################
# 10. ARCHITECTURE SUMMARY
########################################

echo "10. ARCHITECTURE SUMMARY" | tee -a "$OUTPUT"

echo "The system appears to contain:" | tee -a "$OUTPUT"

grep -R "FastAPI" -n . >/dev/null && echo "- API Layer (FastAPI detected)" | tee -a "$OUTPUT"
grep -R "twilio" -n . >/dev/null && echo "- Messaging Layer (Twilio integration)" | tee -a "$OUTPUT"
grep -R "openai" -n . >/dev/null && echo "- AI Reasoning Layer (OpenAI detected)" | tee -a "$OUTPUT"
[ -d governance ] && echo "- Governance Layer present" | tee -a "$OUTPUT"
[ -d clients ] && echo "- Client Data Layer present" | tee -a "$OUTPUT"

echo "" | tee -a "$OUTPUT"

echo "========================================" | tee -a "$OUTPUT"
echo "SYSTEM BRIEF COMPLETE" | tee -a "$OUTPUT"
echo "Saved to $OUTPUT" | tee -a "$OUTPUT"