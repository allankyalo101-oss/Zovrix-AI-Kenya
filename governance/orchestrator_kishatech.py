"""
orchestrator_kishatech.py — Kisha-Tech Electronics AI Enquiry Handler

Simpler than CloudOven orchestrator — no order flow, no STK push.
Sarah's job at Kisha-Tech:
    1. Answer stock enquiries ("do you have MCB 16A?")
    2. Quote prices from live Volta OS inventory
    3. Escalate bulk orders and delivery requests to owner
    4. Direct customers to walk in — opposite Manza College, Machakos

What this does NOT handle (Week 2):
    - WhatsApp receipts (manual via wa.me for now)
    - M-Pesa STK Push (no IntaSend account yet)
    - Customer registration
"""

from typing import Tuple

from app.services.openai_client import OpenAIService
from app.services.data_layer_kishatech import build_kishatech_context
from app.state.order_state import (
    get_session,
    update_session,
    append_to_history,
)
from governance.alerting import send_alert
from governance.ledger import append_to_ledger
from app.config import settings

service = OpenAIService()

CLIENT_ID = "kisha_tech"

# Keywords that always escalate immediately
ESCALATION_KEYWORDS = {
    "bulk", "wholesale", "jumla", "delivery", "deliver", "peleka",
    "installation", "install", "wiring", "complaint", "damaged",
    "refund", "negotiate", "discount", "bei gani wholesale",
}

# Greeting triggers
GREETING_KEYWORDS = {
    "hi", "hello", "hujambo", "habari", "karibu", "sasa", "mambo",
    "niambie", "naomba", "help", "assist",
}


def execute_kishatech_message(sender: str, message: str) -> Tuple[str, bool]:
    """
    Main entry point for Kisha-Tech WhatsApp messages.
    Returns (response_text, escalated_bool).
    """
    print(f">>> KTECH ORCHESTRATOR | sender: {sender[-4:]}")
    sender_last4 = sender[-4:] if sender else "0000"
    response  = "Asante for reaching out to Kisha-Tech Electronics! 🔧 This query needs the shop owner's attention. Please hold — they will respond shortly."
    escalated = True

    try:
        # 1. SESSION
        session = get_session(sender)

        msg_lower = message.lower().strip()

        # 2. IMMEDIATE ESCALATION — bulk / delivery / installation
        if any(kw in msg_lower for kw in ESCALATION_KEYWORDS):
            escalated = True
            topic = "bulk_order" if any(k in msg_lower for k in ["bulk","wholesale","jumla"]) else \
                    "delivery"   if any(k in msg_lower for k in ["delivery","deliver","peleka"]) else \
                    "installation"
            response = _escalation_response(topic)
            append_to_history(sender, "user", message)
            append_to_history(sender, "assistant", response)
            append_to_ledger(
                sender=sender_last4, message=message,
                response=response, escalated=True, client_id=CLIENT_ID
            )
            print(f"[KISHATECH] Immediate escalation: {topic}")
            return response, True

        # 3. BUILD DATA CONTEXT — live inventory from Kisha-Tech Supabase
        data_context = build_kishatech_context(sender)

        # 4. CONVERSATION HISTORY
        conversation_history = session.get("history", [])

        # 5. GROQ
        ai_result = service.generate_response(
            user_message=message,
            session=session,
            conversation_history=conversation_history,
            data_context=data_context,
            client_id=CLIENT_ID,
        )

        response  = ai_result.get("response", settings.ESCALATION_MESSAGE)
        escalated = ai_result.get("escalate", False)
        topic     = ai_result.get("topic", "unknown")

        # 6. If Groq itself flagged escalation (bulk, delivery detected in context)
        if escalated:
            print(f"[KISHATECH] Groq escalation: topic={topic}")

        # 7. HISTORY
        append_to_history(sender, "user", message)
        append_to_history(sender, "assistant", response)

        # 8. LEDGER
        append_to_ledger(
            sender=sender_last4, message=message,
            response=response, escalated=escalated, client_id=CLIENT_ID
        )

        print(f"[KISHATECH] Done | escalated={escalated} | topic={topic}")
        return response, escalated

    except Exception as e:
        print(f"[KISHATECH ERROR] {repr(e)}")
        try:
            send_alert(
                subject="Kisha-Tech orchestrator failure",
                message=f"Sender: {sender}\nMessage: {message}\nError: {repr(e)}"
            )
        except Exception:
            pass
        try:
            append_to_ledger(
                sender=sender_last4, message=message,
                response=response, escalated=True, client_id=CLIENT_ID
            )
        except Exception:
            pass
        return response, True


def _escalation_response(topic: str) -> str:
    """Return appropriate escalation message based on topic."""
    if topic == "bulk_order":
        return (
            "Asante for your interest! 🔧 For bulk/wholesale orders, "
            "I'll connect you with our shop owner directly — they'll give "
            "you the best deal. Please hold a moment."
        )
    if topic == "delivery":
        return (
            "Asante! We don't offer delivery currently — items are available "
            "for pickup at our shop opposite Manza College, Machakos. "
            "For large orders, I'll connect you with the owner to arrange something. Please hold."
        )
    if topic == "installation":
        return (
            "Asante! We sell electronics and hardware but don't offer installation services. "
            "We can recommend a local electrician — or if you have questions about products "
            "for your installation, I'm happy to help! 🔧"
        )
    return (
        "Asante for reaching out to Kisha-Tech Electronics! 🔧 "
        "This query needs the shop owner's attention. Please hold — they will respond shortly."
    )