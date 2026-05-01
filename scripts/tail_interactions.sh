#!/bin/bash

LOG_FILE="/home/cloudstaff/cloudstaff/logs/interactions.json"

if [ ! -f "$LOG_FILE" ]; then
    echo "interactions.json not found!"
    exit 1
fi

tail -f "$LOG_FILE" | while read -r line; do

    TIMESTAMP=$(echo "$line" | jq -r '.timestamp')
    SENDER=$(echo "$line" | jq -r '.sender_last4')
    MESSAGE=$(echo "$line" | jq -r '.message')
    RESPONSE=$(echo "$line" | jq -r '.response')
    ESCALATED=$(echo "$line" | jq -r '.escalated')
    MOCK=$(echo "$line" | jq -r '.mock_mode')

    CYAN="\e[96m"
    GREEN="\e[92m"
    YELLOW="\e[93m"
    RED="\e[91m"
    RESET="\e[0m"

    ICON="✓"
    COLOR=$GREEN

    if [ "$ESCALATED" = "true" ]; then
        ICON="⚠"
        COLOR=$RED
    elif [ "$MOCK" = "true" ]; then
        ICON="●"
        COLOR=$YELLOW
    fi

    echo -e "${CYAN}${TIMESTAMP} [${SENDER}]${RESET} ${COLOR}${ICON} ${MESSAGE}${RESET}"
done
