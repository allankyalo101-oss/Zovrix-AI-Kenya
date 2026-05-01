"""
app/routes/whatsapp_kishatech.py — Kisha-Tech WhatsApp webhook

Twilio console for Kisha-Tech account must point to:
  POST https://<ngrok-or-render-url>/webhook/kisha_tech

Owner number: +254115998028 (Kisha-Tech dedicated line, WhatsApp pending registration)
"""

import os
import json
import logging
import datetime
import traceback
import html
from pathlib import Path

from fastapi import APIRouter, Request, Response

logger    = logging.getLogger("zovrix.kishatech")
router    = APIRouter()

CLIENT_ID  = "kisha_tech"
SOFT_LIMIT = 40
HARD_LIMIT = 50
LOG_DIR    = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def _creds():
    sid    = os.getenv("KISHATECH_TWILIO_SID")    or os.getenv("TWILIO_ACCOUNT_SID",    "")
    token  = os.getenv("KISHATECH_TWILIO_TOKEN")  or os.getenv("TWILIO_AUTH_TOKEN",      "")
    number = os.getenv("KISHATECH_TWILIO_NUMBER") or os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    return sid, token, number

def _owner_number() -> str:
    n = (os.getenv("KISHATECH_OWNER_WHATSAPP")
         or os.getenv("OWNER_WHATSAPP_NUMBER", "+254115998282"))
    return n.replace("whatsapp:", "").strip()

def _get_daily_count() -> int:
    path = LOG_DIR / f"interactions_{CLIENT_ID}.json"
    try:
        if not path.exists():
            return 0
        data  = json.loads(path.read_text())
        today = datetime.datetime.utcnow().date().isoformat()
        return sum(1 for e in data if str(e.get("date", ""))[:10] == today)
    except Exception:
        return 0

def _log_interaction(sender_last4: str, message: str, response: str, escalated: bool):
    path = LOG_DIR / f"interactions_{CLIENT_ID}.json"
    try:
        data = json.loads(path.read_text()) if path.exists() else []
    except Exception:
        data = []
    data.append({
        "date":      datetime.datetime.utcnow().isoformat(),
        "sender":    sender_last4,
        "msg_len":   len(message),
        "resp_len":  len(response),
        "escalated": escalated,
    })
    try:
        path.write_text(json.dumps(data[-500:]))
    except Exception:
        pass

def _send_alert(to: str, body: str):
    sid, token, from_number = _creds()
    if not all([sid, token, from_number]):
        logger.warning("[KishaTech] Twilio creds missing — cannot send escalation alert")
        return
    try:
        from twilio.rest import Client
        client  = Client(sid, token)
        to_wa   = to   if to.startswith("whatsapp:")          else f"whatsapp:{to}"
        from_wa = from_number if from_number.startswith("whatsapp:") else f"whatsapp:{from_number}"
        msg = client.messages.create(body=body, from_=from_wa, to=to_wa)
        logger.info(f"[KishaTech] Alert sent SID={msg.sid} to {to[-4:]}")
    except Exception as e:
        logger.error(f"[KishaTech] Alert failed: {repr(e)}")

def _twiml(message: str) -> Response:
    escaped = html.escape(str(message))
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n  <Message>{escaped}</Message>\n</Response>',
        media_type="application/xml",
    )

def _limit_response() -> str:
    return (
        "Habari! Tumefika kikomo cha mazungumzo leo. 🙏\n\n"
        "Tafadhali tembelea duka letu:\n"
        "📍 Opposite Manza College, Machakos Kenya Israel\n\n"
        "Au tutumie ujumbe kesho asubuhi. Asante!"
    )

@router.post("/kisha_tech")
async def kishatech_webhook(request: Request):
    logger.info(">>> Kisha-Tech webhook hit")

    sender_number = ""
    message       = ""
    response_text = ""
    escalated     = True

    try:
        form          = dict(await request.form())
        message       = form.get("Body", "").strip()
        sender_number = form.get("From", "").replace("whatsapp:", "").strip()
        logger.info(f"[KishaTech] From=...{sender_number[-4:]} | Msg={message[:60]}")

        daily_count = _get_daily_count()
        logger.info(f"[KishaTech] Daily: {daily_count}/{HARD_LIMIT}")

        if daily_count >= SOFT_LIMIT:
            response_text = _limit_response()
            _log_interaction(sender_number[-4:], message, response_text, False)
            return _twiml(response_text)

        logger.info("[KishaTech] Calling orchestrator...")
        from governance.orchestrator_kishatech import execute_kishatech_message
        response_text, escalated = execute_kishatech_message(sender_number, message)
        logger.info(f"[KishaTech] Done | escalated={escalated}")

    except Exception:
        logger.error(f"[KishaTech] Crash:\n{traceback.format_exc()}")
        response_text = (
            "Asante for reaching out to Kisha-Tech Electronics! 🔧 "
            "This query needs the shop owner's attention. Please hold."
        )
        escalated = True

    if not response_text or not str(response_text).strip():
        response_text = "Karibu Kisha-Tech! 🔧 Unahitaji nini leo?"
        escalated = True

    if len(response_text) > 1500:
        response_text = response_text[:1497] + "..."

    if escalated and sender_number and message:
        owner = _owner_number()
        if owner:
            _send_alert(owner,
                f"🔴 Kisha-Tech — Sarah escalated\n"
                f"Customer: {sender_number}\n"
                f"Message: {message[:200]}\n"
                f"Sarah: {response_text[:200]}\n"
                f"Reply: wa.me/{sender_number.lstrip('+')}"
            )

    _log_interaction(sender_number[-4:] if sender_number else "????",
                     message, response_text, escalated)
    logger.info(f"[KishaTech] TwiML sent ({len(response_text)} chars)")
    return _twiml(response_text)