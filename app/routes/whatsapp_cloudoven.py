"""
app/routes/whatsapp_cloudoven.py — CloudOven WhatsApp webhook

Twilio console for CloudOven account must point to:
  POST https://<render-url>/webhook/cloud_oven

Uses: CLOUDOVEN_TWILIO_SID, CLOUDOVEN_TWILIO_TOKEN, CLOUDOVEN_TWILIO_NUMBER
Falls back to TWILIO_* if client-specific vars not set.

Daily limit: SOFT_LIMIT=40 redirects to website, HARD_LIMIT=50 hard stop.
Escalation: WhatsApp alert + SMS to CLOUDOVEN_OWNER_WHATSAPP (+254712191702)
"""

import os
import json
import logging
import datetime
import traceback
import html
from pathlib import Path

from fastapi import APIRouter, Request, Response

logger = logging.getLogger("zovrix.cloudoven")
router = APIRouter()

CLIENT_ID   = "cloud_oven"
SOFT_LIMIT  = 40
HARD_LIMIT  = 50
LOG_DIR     = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# ── Credentials (CloudOven Twilio account) ────────────────
def _creds():
    sid    = os.getenv("CLOUDOVEN_TWILIO_SID")    or os.getenv("TWILIO_ACCOUNT_SID", "")
    token  = os.getenv("CLOUDOVEN_TWILIO_TOKEN")  or os.getenv("TWILIO_AUTH_TOKEN",  "")
    number = os.getenv("CLOUDOVEN_TWILIO_NUMBER") or os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    return sid, token, number

def _owner_number() -> str:
    n = os.getenv("CLOUDOVEN_OWNER_WHATSAPP") or os.getenv("OWNER_WHATSAPP_NUMBER", "")
    return n.replace("whatsapp:", "").strip()

def _website_url() -> str:
    return os.getenv("CLOUDOVEN_WEBSITE", "cloudoven.vercel.app")

# ── Daily counter ─────────────────────────────────────────
def _get_daily_count() -> int:
    path = LOG_DIR / f"interactions_{CLIENT_ID}.json"
    try:
        if not path.exists():
            return 0
        data  = json.loads(path.read_text())
        today = datetime.datetime.utcnow().date().isoformat()
        return sum(1 for e in data if str(e.get("date",""))[:10] == today)
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
        path.write_text(json.dumps(data[-500:]))  # keep last 500
    except Exception:
        pass

# ── Twilio outbound (escalation alert) ───────────────────
def _send_alert(to: str, body: str):
    sid, token, from_number = _creds()
    if not all([sid, token, from_number]):
        logger.warning("[CloudOven] Twilio creds missing — cannot send escalation alert")
        return
    try:
        from twilio.rest import Client
        client  = Client(sid, token)
        to_wa   = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        from_wa = from_number if from_number.startswith("whatsapp:") else f"whatsapp:{from_number}"
        msg = client.messages.create(body=body, from_=from_wa, to=to_wa)
        logger.info(f"[CloudOven] Escalation alert sent SID={msg.sid}")
    except Exception as e:
        logger.error(f"[CloudOven] Escalation WhatsApp failed: {repr(e)}")
    # SMS fallback
    try:
        from twilio.rest import Client
        client   = Client(sid, token)
        sms_from = from_number.replace("whatsapp:", "")
        sms_to   = to.replace("whatsapp:", "")
        if not sms_to.startswith("+"): sms_to = "+" + sms_to
        sms = client.messages.create(body=body[:160], from_=sms_from, to=sms_to)
        logger.info(f"[CloudOven] SMS fallback sent SID={sms.sid}")
    except Exception as e:
        logger.warning(f"[CloudOven] SMS fallback failed: {repr(e)}")

# ── TwiML helper ──────────────────────────────────────────
def _twiml(message: str) -> Response:
    escaped = html.escape(str(message))
    body    = f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n  <Message>{escaped}</Message>\n</Response>'
    return Response(content=body, media_type="application/xml")

# ── Limit response ────────────────────────────────────────
def _limit_response() -> str:
    url = _website_url()
    return (
        f"Habari! Sarah amefika kikomo chake cha ujumbe leo. 🙏\n\n"
        f"Unaweza kuendelea kununua moja kwa moja kwenye website yetu:\n"
        f"👉 {url}\n\n"
        f"Tutarudi kesho asubuhi. Asante kwa uvumilivu wako!"
    )

# ── Main webhook ──────────────────────────────────────────
@router.post("/cloud_oven")
async def cloudoven_webhook(request: Request):
    logger.info(">>> CloudOven webhook hit")

    sender_number = ""
    message       = ""
    response_text = ""
    escalated     = True

    try:
        form          = dict(await request.form())
        message       = form.get("Body", "").strip()
        raw_sender    = form.get("From", "")
        sender_number = raw_sender.replace("whatsapp:", "").strip()

        logger.info(f"[CloudOven] From={sender_number[-4:]} | Msg={message[:60]}")

        # Daily limit
        daily_count = _get_daily_count()
        logger.info(f"[CloudOven] Daily count: {daily_count}/{HARD_LIMIT}")

        if daily_count >= SOFT_LIMIT:
            logger.info(f"[CloudOven] Soft cutoff reached — redirecting to website")
            response_text = _limit_response()
            _log_interaction(sender_number[-4:], message, response_text, False)
            return _twiml(response_text)

        # Orchestrator
        logger.info("[CloudOven] Calling orchestrator...")
        from governance.orchestrator import execute_message
        response_text, escalated = execute_message(
            sender=sender_number,
            message=message,
            client_id=CLIENT_ID,
        )
        logger.info(f"[CloudOven] Done | escalated={escalated}")

    except Exception:
        logger.error(f"[CloudOven] Crash:\n{traceback.format_exc()}")
        from app.config import settings
        response_text = getattr(settings, "ESCALATION_MESSAGE",
                                "Asante for reaching out to CloudOven 😊 Let me check that with our team and get back to you shortly.")
        escalated = True

    # Safety net
    if not response_text or not str(response_text).strip():
        response_text = "Karibu CloudOven! Ninaweza kukusaidia vipi? 🍪"
        escalated = True

    # Truncate
    if len(response_text) > 1500:
        response_text = response_text[:1497] + "..."

    # Escalation alert
    if escalated and sender_number and message:
        owner = _owner_number()
        if owner:
            _send_alert(owner,
                f"🔴 CloudOven Sarah escalation\n"
                f"Customer: {sender_number}\n"
                f"Message: {message[:200]}\n"
                f"Sarah replied: {response_text[:200]}\n"
                f"Reply: wa.me/{sender_number.lstrip('+')}"
            )

    _log_interaction(
        sender_number[-4:] if sender_number else "????",
        message, response_text, escalated,
    )

    logger.info(f"[CloudOven] Sending TwiML ({len(response_text)} chars)")
    return _twiml(response_text)