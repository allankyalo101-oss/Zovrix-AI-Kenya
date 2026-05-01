"""
Execution Orchestrator — CloudOven Edition v10

Additions in this version (surgical only — all v9 logic preserved):

    1. SIGNUP GATE — if data_layer returns needs_signup=True and the
       conversation is heading toward payment, Sarah intercepts and
       sends the CloudOven signup link before any order is created.
       Unregistered customers cannot place WhatsApp orders.

    2. STK PUSH HISTORY CONTEXT — after every STK push, a system note
       is appended to conversation history so Groq knows a push was sent.
       Prevents Groq from lying "I haven't sent anything yet."

    3. AIRTEL / NON-SAFARICOM DETECTION — STK push only works on
       Safaricom numbers. If the sender's number starts with an Airtel
       or other non-Safaricom prefix, Sarah redirects to the website
       for payment instead of attempting a push that will never arrive.
"""

import time
import datetime
import json
import os
from typing import Tuple, Optional

from app.config import settings
from app.services.openai_client import OpenAIService
from app.services.payment_service import PaymentService
from app.services.data_layer import (
    fetch_customer_by_phone,
    build_sarah_context,
    fetch_transaction_by_order,
)

from governance.integrity import validate_client_profile
from governance.alerting import send_alert
from governance.ledger import append_to_ledger

from app.state.order_state import (
    get_session,
    update_session,
    append_to_history,
)

service         = OpenAIService()
payment_service = PaymentService()

PRICE_PER_COOKIE     = 150
PAYMENT_READY_STAGES = {"payment", "location_selected", "delivery", "pickup"}
CONFIRMATION_WORDS   = {
    "yes", "yeah", "yep", "yap", "confirm", "ok", "okay", "okey",
    "sawa", "ndio", "sure", "proceed", "go ahead", "correct",
    "it is correct", "yes it is correct", "yes please", "yes.",
    "yes, it is correct", "affirmative", "alright", "let's go",
    "do it", "send it", "pay", "continue",
}

ORDER_ID_KEYWORDS = {
    "order id", "order-id", "orderid", "my order id",
    "what is my order", "order number", "order ref",
    "namba ya order", "order namba",
}

CANCEL_KEYWORDS = {
    "cancel", "cancel order", "cancel my order", "futa order",
    "nilifuta", "sitaki", "stop order", "don't want", "dont want",
    "cancel the order", "cancel pending", "cancel it",
}

# Safaricom Kenya number prefixes (3 digits after country code 254)
SAFARICOM_PREFIXES = {
    "700", "701", "702", "703", "704", "705", "706", "707", "708", "709",
    "710", "711", "712", "713", "714", "715", "716", "717", "718", "719",
    "720", "721", "722", "723", "724", "725", "726", "727", "728", "729",
    "740", "741", "742", "743", "744", "745", "746", "747", "748", "749",
    "757", "758", "759", "768", "769",
    "790", "791", "792", "793", "794", "795", "796", "797", "798", "799",
    "110", "111", "112", "113", "114", "115", "116", "117", "118", "119",
}

CLOUDOVEN_WEBSITE = "cloudoven.vercel.app"


def _is_safaricom_number(phone: str) -> bool:
    cleaned = phone.replace("+", "").replace(" ", "").replace("-", "")
    if cleaned.startswith("254") and len(cleaned) == 12:
        return cleaned[3:6] in SAFARICOM_PREFIXES
    if cleaned.startswith("0") and len(cleaned) == 10:
        return cleaned[1:4] in SAFARICOM_PREFIXES
    return False


def _is_confirmation(message: str) -> bool:
    msg = message.lower().strip().rstrip(".")
    if msg in CONFIRMATION_WORDS:
        return True
    for word in ("yes", "okay", "ok", "sawa", "ndio", "yep", "sure"):
        if msg.startswith(word):
            return True
    return False


def _get_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
        if not url or not key:
            print("[DB] Missing SUPABASE_URL or key")
            return None
        return create_client(url, key)
    except Exception as e:
        print(f"[DB] Supabase client error: {repr(e)}")
        return None


def _create_whatsapp_order(session: dict, amount: int, items: list) -> Optional[str]:
    client = _get_supabase()
    if not client:
        return None
    try:
        user_id  = session.get("customer_id")
        location = session.get("location", "WhatsApp order")
        now      = datetime.datetime.utcnow().isoformat() + "Z"
        payload  = {
            "status":           "pending_payment",
            "amount":           amount,
            "items":            items,
            "delivery_address": location,
            "created_at":       now,
            "updated_at":       now,
        }
        if user_id:
            payload["user_id"] = user_id
        result = client.table("orders").insert(payload).execute()
        if result.data and len(result.data) > 0:
            order_id = result.data[0].get("id")
            if order_id:
                print(f"[DB] Order created: {order_id[:8]} | KES {amount}")
                return order_id
        print(f"[DB] Order insert returned no data: {result}")
        return None
    except Exception as e:
        print(f"[DB] Order creation failed: {repr(e)}")
        return None


def _insert_transaction(
    order_id: str,
    user_id: Optional[str],
    phone: str,
    amount: int,
    invoice_id: str,
    api_ref: str,
    raw_response: dict,
) -> bool:
    client = _get_supabase()
    if not client:
        return False
    try:
        cleaned = str(phone).replace("whatsapp:", "").replace("+", "").replace(" ", "")
        if cleaned.startswith("0"):
            cleaned = "254" + cleaned[1:]
        now     = datetime.datetime.utcnow().isoformat() + "Z"
        payload = {
            "order_id":     order_id,
            "phone":        cleaned,
            "amount":       amount,
            "currency":     "KES",
            "invoice_id":   invoice_id,
            "api_ref":      api_ref,
            "status":       "pending",
            "provider":     "intasend",
            "raw_response": raw_response,
            "created_at":   now,
            "updated_at":   now,
        }
        if user_id:
            payload["user_id"] = user_id
        result = client.table("intasend_transactions").insert(payload).execute()
        if result.data:
            print(f"[DB] intasend_transactions row inserted | invoice_id={invoice_id}")
            return True
        print(f"[DB] Transaction insert returned no data: {result}")
        return False
    except Exception as e:
        print(f"[DB] Transaction insert failed: {repr(e)}")
        return False


def _update_order_paid(order_id: str) -> bool:
    client = _get_supabase()
    if not client:
        return False
    try:
        client.table("orders") \
            .update({
                "status":     "paid",
                "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
            }) \
            .eq("id", order_id) \
            .eq("status", "pending_payment") \
            .execute()
        print(f"[DB] Order {order_id[:8]} marked paid")
        return True
    except Exception as e:
        print(f"[DB] Order update failed: {repr(e)}")
        return False


def _cancel_order(order_id: str) -> bool:
    client = _get_supabase()
    if not client:
        return False
    try:
        client.table("orders") \
            .update({
                "status":     "cancelled",
                "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
            }) \
            .eq("id", order_id) \
            .eq("status", "pending_payment") \
            .execute()
        print(f"[DB] Order {order_id[:8]} cancelled")
        return True
    except Exception as e:
        print(f"[DB] Order cancel failed: {repr(e)}")
        return False


def _quick_response(sender: str, sender_last4: str, message: str,
                    response: str, client_id: str) -> Tuple[str, bool]:
    append_to_history(sender, "user", message)
    append_to_history(sender, "assistant", response)
    append_to_ledger(
        sender=sender_last4, message=message,
        response=response, escalated=False, client_id=client_id
    )
    return response, False


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def execute_message(sender: str, message: str, client_id: str = None) -> Tuple[str, bool]:
    print(">>> ORCHESTRATOR EXECUTING")
    sender_last4 = sender[-4:] if sender else "0000"
    response  = settings.ESCALATION_MESSAGE
    escalated = True

    try:
        # 1. GOVERNANCE
        validate_client_profile(client_id)

        # 2. SESSION
        session = get_session(sender)
        print(f"[ORCH] Session: {session}")

        # 3. CUSTOMER IDENTITY
        if not session.get("identity_loaded"):
            customer = fetch_customer_by_phone(sender)
            if customer:
                update_session(sender, {**customer, "identity_loaded": True})
            else:
                update_session(sender, {"identity_loaded": True})
            session = get_session(sender)

        # 4. DATA CONTEXT
        customer_data = {
            "customer_id":    session.get("customer_id"),
            "customer_name":  session.get("customer_name"),
            "customer_email": session.get("customer_email"),
            "needs_signup":   session.get("needs_signup", False),
        } if session.get("identity_loaded") else None

        data_context = build_sarah_context(sender, customer_data)

        msg_lower = message.lower().strip()

        # ── ORDER ID QUERY ────────────────────────────────────────────────────
        if any(kw in msg_lower for kw in ORDER_ID_KEYWORDS):
            current_order_id = session.get("current_order_id")
            if current_order_id:
                short_id = current_order_id[:8].upper()
                resp = (
                    f"Your order ID is {short_id} "
                    f"(full: {current_order_id}). "
                    f"Track your order at: {CLOUDOVEN_WEBSITE}"
                )
            else:
                resp = "You don't have an active order in this session. Tell me what cookies you'd like to start a new order!"
            return _quick_response(sender, sender_last4, message, resp, client_id)

        # ── CANCEL INTENT ─────────────────────────────────────────────────────
        if any(kw in msg_lower for kw in CANCEL_KEYWORDS):
            current_order_id = session.get("current_order_id")
            if current_order_id:
                cancelled = _cancel_order(current_order_id)
                if cancelled:
                    update_session(sender, {
                        "current_order_id": None,
                        "last_payment_ref": None,
                        "last_invoice_id":  None,
                        "stage":            "start",
                        "cookie_type":      None,
                        "quantity":         None,
                        "location":         None,
                    })
                    resp = f"Order {current_order_id[:8].upper()} cancelled. No payment will be taken. What else can I get for you? 🍪"
                else:
                    resp = "I wasn't able to cancel — the order may already be paid or processed. Please contact us directly for help."
            else:
                resp = "There's no active order to cancel. Let me know if you'd like to start a new order."
            return _quick_response(sender, sender_last4, message, resp, client_id)

        # 5. PAYMENT TRIGGER
        current_stage = session.get("stage", "start")
        order_ready = (
            session.get("cookie_type") and
            session.get("quantity") and
            session.get("location")
        )

        if order_ready and current_stage in PAYMENT_READY_STAGES and _is_confirmation(message):
            print(f"[ORCH] Payment trigger: stage={current_stage} | confirmed=True")

            # ADDITION 1: SIGNUP GATE
            if session.get("needs_signup"):
                resp = (
                    f"To order on WhatsApp you need a CloudOven account first — "
                    f"it only takes 2 minutes! 🍪\n\n"
                    f"👉 {CLOUDOVEN_WEBSITE}\n\n"
                    f"Sign up, then come back here and I'll complete your order instantly. "
                    f"Your cookie selection is saved!"
                )
                print("[ORCH] Signup gate triggered — customer has no account")
                return _quick_response(sender, sender_last4, message, resp, client_id)

            # ADDITION 3: NON-SAFARICOM GATE
            if not _is_safaricom_number(sender):
                resp = (
                    f"M-Pesa STK Push works with Safaricom numbers only. "
                    f"It looks like you're on Airtel or another network 📱\n\n"
                    f"You can complete your order and pay with Airtel Money "
                    f"directly on our website:\n"
                    f"👉 {CLOUDOVEN_WEBSITE}\n\n"
                    f"Your order: {session.get('quantity')}x "
                    f"{session.get('cookie_type')} → {session.get('location')} 🍪"
                )
                print(f"[ORCH] Non-Safaricom detected ({sender_last4}) — redirecting to website")
                return _quick_response(sender, sender_last4, message, resp, client_id)

            return _handle_payment(sender, session, sender_last4, message, client_id, data_context)

        # 6. PAYMENT STATUS CHECK
        payment_keywords = {
            "payment", "paid", "mpesa", "malipo", "order status",
            "my order", "nimesend", "nimelipa", "status ya order",
        }

        if any(kw in msg_lower for kw in payment_keywords):
            session_order_id = session.get("current_order_id")
            if session_order_id:
                txn = fetch_transaction_by_order(session_order_id)
                if txn:
                    status   = txn.get("status")
                    receipt  = txn.get("mpesa_receipt")
                    short_id = session_order_id[:8].upper()

                    if status == "complete":
                        _update_order_paid(session_order_id)
                        response = (
                            f"✅ Payment confirmed! M-Pesa receipt: {receipt}. "
                            f"Order ID: {short_id}. Your cookies are being prepared! 🍪"
                        ) if receipt else (
                            f"✅ Payment confirmed! Order ID: {short_id}. "
                            f"Your order is being processed. 🍪"
                        )
                    elif status == "pending":
                        response = (
                            f"Your payment for order {short_id} is still pending. "
                            f"Please complete the M-Pesa prompt on your phone. "
                            f"If you entered the wrong PIN, send 'resend'."
                        )
                    elif status == "failed":
                        response = (
                            f"❌ Payment failed for order {short_id}. "
                            f"Send 'resend' and I'll send a new M-Pesa request."
                        )
                    else:
                        response = f"Payment status for order {short_id}: {status}. Please contact us if you need help."

                    escalated = False
                    return _quick_response(sender, sender_last4, message, response, client_id)
                else:
                    return _quick_response(
                        sender, sender_last4, message,
                        "Waiting for payment confirmation. Please complete the M-Pesa prompt on your phone.",
                        client_id
                    )

        # Handle resend
        if "resend" in msg_lower and session.get("stage") == "payment_initiated":
            if not _is_safaricom_number(sender):
                return _quick_response(
                    sender, sender_last4, message,
                    f"STK Push is for Safaricom numbers only. Please pay via our website: 👉 {CLOUDOVEN_WEBSITE} 🍪",
                    client_id
                )
            print(f"[ORCH] Resend requested for sender {sender_last4}")
            return _handle_payment(sender, session, sender_last4, message, client_id, data_context)

        # 7. GROQ
        conversation_history = session.get("history", [])
        ai_result = service.generate_response(
            user_message=message,
            session=session,
            conversation_history=conversation_history,
            data_context=data_context,
        )

        response  = ai_result.get("response", settings.ESCALATION_MESSAGE)
        escalated = ai_result.get("escalate", False)

        # 8. ORDER UPDATES
        order_update = ai_result.get("order_update", {})
        if order_update:
            clean = {k: v for k, v in order_update.items() if v is not None}
            if clean:
                update_session(sender, clean)
                print(f"[ORCH] Session updated: {clean}")

        # 9. HISTORY
        append_to_history(sender, "user", message)
        append_to_history(sender, "assistant", response)

        # 10. LEDGER
        append_to_ledger(
            sender=sender_last4, message=message,
            response=response, escalated=escalated, client_id=client_id
        )

        print(f"[ORCH] Done | escalated={escalated} | stage={get_session(sender).get('stage')}")
        return response, escalated

    except Exception as e:
        print(f"[ORCH ERROR] {repr(e)}")
        try:
            send_alert(
                subject="CloudOven orchestrator failure",
                message=f"Sender: {sender}\nMessage: {message}\nError: {repr(e)}"
            )
        except Exception:
            pass
        try:
            append_to_ledger(
                sender=sender_last4, message=message,
                response=response, escalated=True, client_id=client_id
            )
        except Exception:
            pass
        return response, escalated


# =============================================================================
# PAYMENT HANDLER
# =============================================================================

def _handle_payment(
    sender: str,
    session: dict,
    sender_last4: str,
    message: str,
    client_id: str,
    data_context: dict,
    max_retries: int = 3,
) -> Tuple[str, bool]:
    try:
        cookie_type   = session.get("cookie_type", "cookies")
        quantity      = int(session.get("quantity", 0))
        customer_name = session.get("customer_name", "")
        user_id       = session.get("customer_id")

        if not quantity:
            response = "I need to confirm how many cookies you want before processing payment."
            append_to_history(sender, "user", message)
            append_to_history(sender, "assistant", response)
            return response, False

        raw_products    = data_context.get("raw_products", [])
        price_per_unit  = PRICE_PER_COOKIE
        matched_product = None
        for p in raw_products:
            if cookie_type.lower() in p.get("name", "").lower():
                price_per_unit  = int(p.get("price", PRICE_PER_COOKIE))
                matched_product = p
                break

        amount    = quantity * price_per_unit
        name_part = f" {customer_name.split()[0]}," if customer_name else ","

        items = [{
            "name":        matched_product.get("name", cookie_type) if matched_product else cookie_type,
            "quantity":    quantity,
            "unit_price":  price_per_unit,
            "price":       price_per_unit,
            "image_emoji": matched_product.get("image_emoji", "🍪") if matched_product else "🍪",
        }]

        existing_order_id = session.get("current_order_id")
        if existing_order_id:
            order_id = existing_order_id
            api_ref  = f"CloudOven-{order_id}"
            print(f"[ORCH] Resending for existing order: {order_id[:8]}")
        else:
            order_id = _create_whatsapp_order(session, amount, items)
            if order_id:
                api_ref = f"CloudOven-{order_id}"
                update_session(sender, {"current_order_id": order_id})
                print(f"[ORCH] Order created: {order_id[:8]} | api_ref: {api_ref}")
            else:
                ts      = int(datetime.datetime.utcnow().timestamp())
                api_ref = f"CloudOven-{sender_last4}-{ts}"
                print(f"[ORCH] ⚠️ Order creation failed — fallback ref: {api_ref}")

        response  = ""
        escalated = True

        for attempt in range(1, max_retries + 1):
            try:
                result = payment_service.stk_push(
                    phone_number=sender,
                    amount=amount,
                    reference=api_ref,
                )

                if result and result.get("invoice_id"):
                    invoice_id = result["invoice_id"]
                    raw        = result.get("raw_response", {})

                    if order_id:
                        _insert_transaction(
                            order_id=order_id,
                            user_id=user_id,
                            phone=sender,
                            amount=amount,
                            invoice_id=invoice_id,
                            api_ref=api_ref,
                            raw_response=raw,
                        )

                    short_id = order_id[:8].upper() if order_id else "N/A"
                    response = (
                        f"💳 Perfect{name_part} M-Pesa STK Push of KES {amount} sent to your phone! "
                        f"Enter your M-Pesa PIN to complete. "
                        f"Order ID: {short_id}. "
                        f"Your {quantity} {cookie_type} "
                        f"{'cookies' if quantity > 1 else 'cookie'} "
                        f"will be ready once payment clears 🍪"
                    )
                    escalated = False
                    update_session(sender, {
                        "stage":            "payment_initiated",
                        "last_payment_ref": api_ref,
                        "last_invoice_id":  invoice_id,
                    })

                    # ADDITION 2: STK PUSH HISTORY CONTEXT
                    # Groq now knows a push was sent — cannot lie about it.
                    append_to_history(
                        sender, "assistant",
                        f"[SYSTEM: M-Pesa STK Push sent. Amount: KES {amount}. "
                        f"Phone ending {sender_last4}. Invoice: {invoice_id}. "
                        f"Order ID: {short_id}. Awaiting customer PIN entry.]"
                    )
                    break
                else:
                    raise RuntimeError("STK Push returned no invoice_id")

            except Exception as e:
                print(f"[PAYMENT] Attempt {attempt}/{max_retries} failed: {repr(e)}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                else:
                    response = (
                        f"⚠️ Could not send the payment request right now. "
                        f"Order: {quantity} {cookie_type} — KES {amount}. "
                        f"Please try again or visit {CLOUDOVEN_WEBSITE}."
                    )
                    escalated = True

        append_to_ledger(
            sender=sender_last4, message=message,
            response=response, escalated=escalated, client_id=client_id
        )
        return response, escalated

    except Exception as e:
        print(f"[PAYMENT ERROR] {repr(e)}")
        return "⚠️ Payment error. Please try again or call us directly.", True