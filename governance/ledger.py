"""
Structured Interaction Ledger

Purpose:
- Maintain append-only, time-indexed log of all message interactions.
- Formalises the current logs/interactions.json approach for governance.

Responsibilities:
- Append interactions safely.
- Record sender (last 4 digits), client_id, message, response, escalation status, and timestamp.
- Backward compatible with existing logs.

Excludes:
- Real-time analytics or reporting (handled elsewhere).
- Direct access by client-facing routes.
"""

import json
import os
from datetime import datetime
from pathlib import Path  # corrected import

# Resolve project root dynamically
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = BASE_DIR / "logs" / "interactions.json"

def append_to_ledger(sender: str, message: str, response: str, escalated: bool, client_id: str = None):
    """
    Append a structured interaction to the ledger.

    Args:
        sender (str): Sender last 4 digits.
        message (str): Incoming message.
        response (str): Response sent.
        escalated (bool): Whether message triggered escalation.
        client_id (str, optional): Client identifier.
    """
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": sender,
        "client_id": client_id or "default",
        "message": message,
        "response": response,
        "escalated": escalated
    }

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)  # replaced LEDGER_FILE with LOG_FILE

    with open(LOG_FILE, "a", encoding="utf-8") as f:        # replaced LEDGER_FILE with LOG_FILE
        f.write(json.dumps(record) + "\n")