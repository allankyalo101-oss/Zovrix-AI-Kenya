#!/bin/bash

OUTPUT="architecture_map.md"

echo "# CloudStaff System Architecture Map" > $OUTPUT
echo "" >> $OUTPUT
echo "Generated: $(date)" >> $OUTPUT
echo "" >> $OUTPUT

echo '```mermaid' >> $OUTPUT
echo "graph TD" >> $OUTPUT

########################################
# Detect major system components
########################################

if grep -R "FastAPI" -n . >/dev/null 2>&1; then
    echo "User --> API[FastAPI Server]" >> $OUTPUT
fi

if grep -R "twilio" -n . >/dev/null 2>&1; then
    echo "API --> WhatsApp[Twilio WhatsApp Gateway]" >> $OUTPUT
fi

if grep -R "openai" -n . >/dev/null 2>&1; then
    echo "API --> AI[AI Reasoning Engine]" >> $OUTPUT
fi

if [ -d governance ]; then
    echo "AI --> GOV[Governance Layer]" >> $OUTPUT
fi

if [ -f governance/orchestrator.py ]; then
    echo "GOV --> ORCH[Orchestrator]" >> $OUTPUT
fi

if [ -f governance/ledger.py ]; then
    echo "GOV --> LEDGER[Decision Ledger]" >> $OUTPUT
fi

if [ -d clients ]; then
    echo "API --> CLIENTS[Client Data Layer]" >> $OUTPUT
fi

if grep -R "reportlab" -n . >/dev/null 2>&1; then
    echo "AI --> PDF[Report Generator]" >> $OUTPUT
fi

echo '```' >> $OUTPUT

echo ""
echo "Architecture map written to $OUTPUT"