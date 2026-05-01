"""
order_state.py — Per-sender session memory for CloudOven WhatsApp conversations.

Tracks:
    - Order state (cookie type, quantity, location, stage)
    - Full conversation history (role/content pairs for Groq)
    - Customer identity (name, preferences from Supabase lookup)
    - Session timestamps for TTL expiry

TTL: 2 hours of inactivity clears the session.
"""

import time
from typing import Optional

# In-memory session store — keyed by sender phone number
_sessions: dict = {}

SESSION_TTL_SECONDS = 7200  # 2 hours


def _default_session(sender: str) -> dict:
    return {
        # Order flow state
        "cookie_type": None,
        "quantity": None,
        "location": None,
        "stage": "start",                # start | type_selected | quantity_selected | location_selected | awaiting_payment

        # Customer identity (populated from Supabase on first message)
        "customer_name": None,
        "customer_email": None,
        "customer_id": None,
        "identity_loaded": False,

        # Conversation history — full list of {role, content} dicts
        # Passed directly to Groq as the messages array
        "history": [],

        # Session metadata
        "sender": sender,
        "created": time.time(),
        "last_active": time.time(),
        "message_count": 0,
    }


def get_session(sender: str) -> dict:
    """
    Retrieve the session for a sender.
    Creates a new session if none exists or TTL has expired.
    """
    now = time.time()
    session = _sessions.get(sender)

    if session:
        # Expire stale sessions
        if (now - session.get("last_active", 0)) > SESSION_TTL_SECONDS:
            del _sessions[sender]
            session = None

    if not session:
        session = _default_session(sender)
        _sessions[sender] = session

    session["last_active"] = now
    session["message_count"] += 1
    return session


def update_session(sender: str, updates: dict) -> dict:
    """
    Apply a dict of updates to a session and persist it.
    Returns the updated session.
    """
    session = get_session(sender)
    session.update(updates)
    _sessions[sender] = session
    return session


def append_to_history(sender: str, role: str, content: str):
    """
    Append a single message to the conversation history.

    Args:
        sender:  Phone number key.
        role:    "user" or "assistant"
        content: Message text.
    """
    session = get_session(sender)
    session["history"].append({"role": role, "content": content})

    # Cap history at 20 turns to avoid prompt bloat
    if len(session["history"]) > 40:
        # Keep first 2 (context anchors) + last 38
        session["history"] = session["history"][:2] + session["history"][-38:]

    _sessions[sender] = session


def reset_session(sender: str):
    """
    Fully clear a session after order completion or explicit reset.
    """
    if sender in _sessions:
        del _sessions[sender]


def get_active_session_count() -> int:
    """Return the number of active sessions. Used by audit reports."""
    return len(_sessions)