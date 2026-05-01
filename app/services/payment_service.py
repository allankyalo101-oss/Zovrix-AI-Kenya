"""
payment_service.py — IntaSend STK Push for CloudOven WhatsApp orders.

Returns the full invoice_id on success (not just True/False)
so the orchestrator can insert the intasend_transactions row immediately.
"""

import re
import requests
from app.config import settings


def _normalise_phone(phone: str) -> str:
    cleaned = str(phone).strip()
    cleaned = cleaned.replace("whatsapp:", "").replace(" ", "")
    cleaned = cleaned.lstrip("+")
    if cleaned.startswith("0"):
        cleaned = "254" + cleaned[1:]
    if not re.match(r'^254[0-9]{9}$', cleaned):
        raise ValueError(f"Invalid phone number format: {phone} → {cleaned}")
    return cleaned


class PaymentService:
    def __init__(self):
        is_live = getattr(settings, "INTASEND_ENV", "sandbox") == "live"
        self.base_url   = "https://payment.intasend.com/api/v1/payment/collection/" if is_live \
                          else "https://sandbox.intasend.com/api/v1/payment/collection/"
        self.public_key = getattr(settings, "INTASEND_PUBLIC_KEY", "")
        self.secret_key = getattr(settings, "INTASEND_SECRET_KEY", "")

        print(f"[PAYMENT SERVICE] Mode: {'LIVE' if is_live else 'SANDBOX'}")
        print(f"[PAYMENT SERVICE] Public key: {self.public_key[:12]}..." if self.public_key else "[PAYMENT SERVICE] ⚠️ INTASEND_PUBLIC_KEY missing")
        print(f"[PAYMENT SERVICE] Secret key: {'✅ loaded' if self.secret_key else '❌ INTASEND_SECRET_KEY missing'}")

    def stk_push(self, phone_number: str, amount: int, reference: str = "CloudOvenOrder") -> dict | None:
        """
        Initiate M-Pesa STK Push via IntaSend.

        Returns:
            dict with invoice_id and state on success.
            None on failure.

        Changed from bool return so the orchestrator can insert
        the intasend_transactions row with the real invoice_id.
        """
        if not self.public_key or not self.secret_key:
            print("[PAYMENT] ❌ IntaSend keys missing")
            return None

        try:
            phone = _normalise_phone(phone_number)
        except ValueError as e:
            print(f"[PAYMENT] ❌ Phone normalisation failed: {e}")
            return None

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "public_key":   self.public_key,
            "method":       "M-PESA",
            "currency":     "KES",
            "amount":       int(amount),
            "phone_number": phone,
            "api_ref":      reference[:50],
            "comment":      "Payment for CloudOven order",
        }

        print(f"[PAYMENT] STK Push → {phone} | KES {amount} | ref={reference}")

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=12,
            )

            print(f"[PAYMENT] Status: {response.status_code}")
            print(f"[PAYMENT] Response: {response.text[:500]}")

            if response.status_code in (200, 201):
                data       = response.json()
                invoice_id = (data.get("invoice", {}) or {}).get("invoice_id") or data.get("id")
                state      = (data.get("invoice", {}) or {}).get("state", "PENDING")
                print(f"[PAYMENT] ✅ STK Push accepted | invoice_id={invoice_id}")
                return {
                    "invoice_id":   invoice_id,
                    "state":        state,
                    "raw_response": data,
                }
            else:
                print(f"[PAYMENT] ❌ STK Push rejected: {response.status_code} — {response.text[:200]}")
                return None

        except requests.Timeout:
            print("[PAYMENT] ❌ Request timed out")
            return None
        except Exception as e:
            print(f"[PAYMENT ERROR] {repr(e)}")
            return None