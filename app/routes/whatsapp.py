"""
whatsapp.py — Twilio webhook router for Zovrix AI Kenya

Routes incoming WhatsApp messages to the correct client orchestrator
based on client_id (passed as URL param or resolved from phone number).

Supported clients:
    cloud_oven  → governance/orchestrator.py    (CloudOven cookies)
    kisha_tech      → governance/orchestrator_kishatech.py (Kisha-Tech electronics)

Daily message limit applies per client independently.
Owner escalation alert sent via Twilio when escalated=True.

URL routing:
    POST /webhook/whatsapp               → uses DEFAULT_CLIENT_ID from .env
    POST /webhook/whatsapp?client_id=kisha_tech  → Kisha-Tech
    POST /webhook/whatsapp?client_id=cloud_oven → CloudOven
"""

import os
import json
import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

from app.config import settings

router = APIRouter()

# ── Per-client daily message counter ─────────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

SOFT_LIMIT = 40
HARD_LIMIT = 50


def _log_path(client_id: str) -> Path:
    return LOG_DIR / f"interactions_{client_id}.json"


def _get_daily_count(client_id: str) -> int:
    log_path = _log_path(client_id)
    try:
        if not log_path.exists():
            return 0
        with open(log_path) as f:
            data = json.load(f)
        today = datetime.datetime.utcnow().date().isoformat()
        count = sum(
            1 for entry in data
            if entry.get("date", "")[:10] == today
        )
        return count
    except Exception:
        return 0


def _send_twilio_message(to: str, body: str):
    """Send a WhatsApp message via Twilio REST (for escalation alerts)."""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{to}" if not to.startswith("whatsapp:") else to,
            body=body,
        )
    except Exception as e:
        print(f"[TWILIO ALERT] Send failed: {repr(e)}")


# ── Owner WhatsApp numbers per client ─────────────────────────────────────────
OWNER_NUMBERS = {
    "cloud_oven": getattr(settings, "OWNER_WHATSAPP_NUMBER", ""),
    "kisha_tech":     getattr(settings, "OWNER_WHATSAPP_NUMBER", ""),
    # Both currently route to the same number (0742891721)
    # Update kisha_tech entry when Kisha-Tech gets its own number
}

ESCALATION_MESSAGES = {
    "cloud_oven": getattr(settings, "ESCALATION_MESSAGE", "Asante! Our team will be with you shortly."),
    "kisha_tech":     "Asante for reaching out to Kisha-Tech Electronics! 🔧 This query needs the shop owner's attention. Please hold — they will respond shortly.",
}


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form   = await request.form()
    sender = form.get("From", "")
    body   = form.get("Body", "").strip()

    # Resolve client_id — URL param takes priority, then default
    client_id = request.query_params.get("client_id") or \
                getattr(settings, "DEFAULT_CLIENT_ID", "cloud_oven")

    print(f"[WA] Incoming | client={client_id} | from={sender[-4:]} | msg={body[:60]}")

    twiml    = MessagingResponse()
    escalation_msg = ESCALATION_MESSAGES.get(client_id, ESCALATION_MESSAGES["cloud_oven"])

    # ── Daily limit check ────────────────────────────────────────────────────
    daily_count = _get_daily_count(client_id)
    print(f"[WA] Daily messages used: {daily_count}/{HARD_LIMIT} ({client_id})")

    if daily_count >= SOFT_LIMIT:
        msg = (
            "Samahani, tumfikia kikomo cha mazungumzo leo. "
            "Tafadhali jaribu tena kesho! 🙏"
            if daily_count < HARD_LIMIT
            else escalation_msg
        )
        twiml.message(msg)
        return Response(content=str(twiml), media_type="application/xml")

    # ── Route to correct orchestrator ────────────────────────────────────────
    try:
        if client_id == "kisha_tech":
            from governance.orchestrator_kishatech import execute_kishatech_message
            response_text, escalated = execute_kishatech_message(sender, body)
        else:
            # Default: CloudOven
            from governance.orchestrator import execute_message
            response_text, escalated = execute_message(sender, body, client_id=client_id)

    except Exception as e:
        print(f"[WA ERROR] Orchestrator failed: {repr(e)}")
        response_text = escalation_msg
        escalated     = True

    # ── Owner escalation alert ───────────────────────────────────────────────
    if escalated:
        owner_number = OWNER_NUMBERS.get(client_id, "")
        if owner_number:
            clean_sender = sender.replace("whatsapp:", "")
            shop_name = "Kisha-Tech Electronics" if client_id == "kisha_tech" else "CloudOven"
            alert_msg = (
                f"⚠️ {shop_name} — Sarah escalated a message.\n"
                f"From: {clean_sender}\n"
                f"Message: {body[:200]}"
            )
            _send_twilio_message(owner_number, alert_msg)

    twiml.message(response_text)
    return Response(content=str(twiml), media_type="application/xml")