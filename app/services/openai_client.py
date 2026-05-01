"""
openai_client.py — Groq-powered AI service for Zovrix AI Kenya.

Multi-client version: routes to correct persona based on client_id.

Supported clients:
    cloud_oven  — CloudOven artisan cookies, Machakos (Case Study One)
    kisha_tech  — Kisha-Tech Electronics & Hardware Store, Machakos (Case Study Two)

Changes in this version:
    - AI_NAME fixed: Kisha-Tech prompt now correctly uses Sarah (not Alex)
    - client_id parameter added to generate_response()
    - _build_system_prompt() dispatches to client-specific builder
    - Kisha-Tech prompt: stock enquiry focused, no order flow, no STK push
    - CloudOven prompt: unchanged
"""

import json
import re
from groq import Groq
from app.config import settings


class OpenAIService:

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model  = "llama-3.3-70b-versatile"

    def generate_response(
        self,
        user_message: str,
        session: dict = None,
        conversation_history: list = None,
        data_context: dict = None,
        client_id: str = None,
    ) -> dict:
        session              = session              or {}
        conversation_history = conversation_history or []
        data_context         = data_context         or {}
        client_id            = client_id            or getattr(settings, "DEFAULT_CLIENT_ID", "cloud_oven")

        system_prompt = self._build_system_prompt(session, data_context, client_id)

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=300,
                timeout=10,
            )
            raw = completion.choices[0].message.content.strip()  # type: ignore
            print(f"[GROQ RAW OUTPUT] {raw}")
            return self._parse_response(raw)

        except Exception as e:
            print(f"[AI ERROR] Groq call failed: {repr(e)}")
            return self._error_response()

    # ==========================================================================
    # PROMPT DISPATCHER
    # ==========================================================================

    def _build_system_prompt(
        self,
        session: dict,
        data_context: dict,
        client_id: str,
    ) -> str:
        if client_id == "kisha_tech":
            return self._build_kishatech_prompt(session, data_context)
        return self._build_cloudoven_prompt(session, data_context)

    # ==========================================================================
    # CLOUDOVEN PROMPT — unchanged
    # ==========================================================================

    def _build_cloudoven_prompt(self, session: dict, data_context: dict) -> str:
        cookie_type = session.get("cookie_type")
        quantity    = session.get("quantity")
        location    = session.get("location")
        stage       = session.get("stage", "start")

        product_catalogue  = data_context.get("product_catalogue",  "Catalogue unavailable.")
        batch_context      = data_context.get("batch_context",      "")
        inventory_context  = data_context.get("inventory_context",  "")
        customer_context   = data_context.get("customer_context",   "")
        order_history      = data_context.get("order_history",      "No previous orders.")
        payment_context    = data_context.get("payment_context",    "")

        website_url  = getattr(settings, "CLOUDOVEN_WEBSITE", "") or getattr(settings, "WEBSITE_URL", "")
        website_line = f"- Website: {website_url}" if website_url else "- Website: cloudoven.vercel.app"

        order_state = f"""
CURRENT ORDER STATE:
- Stage: {stage}
- Cookie type: {cookie_type if cookie_type else "not yet selected"}
- Quantity: {quantity if quantity else "not yet selected"}
- Delivery/pickup: {location if location else "not yet provided"}

Do NOT ask for information already confirmed above. Reference it naturally.
"""

        payment_note      = f"\n{payment_context}"   if payment_context   else ""
        batch_section     = f"\n{batch_context}"     if batch_context     else ""
        inventory_section = f"\n{inventory_context}" if inventory_context else ""

        return f"""You are Sarah, the friendly WhatsApp assistant for {settings.BUSINESS_NAME}.

BUSINESS:
- Location: {settings.BUSINESS_LOCATION}
- Hours: {settings.OPERATING_HOURS}
{website_line}
- Delivery: available across Machakos and surrounding areas

{product_catalogue}{batch_section}{inventory_section}

CUSTOMER:
{customer_context}

ORDER HISTORY:
{order_history}{payment_note}

{order_state}

ORDER FLOW:
1. Greet and ask what they want
2. Describe available cookies from catalogue — ONLY what is listed above
3. If asked about today's availability, use PRODUCTION STATUS above (not the catalogue)
4. Confirm cookie type → ask quantity (any quantity is fine, no minimum)
5. Ask delivery address or pickup preference
6. Show full summary → ask for YES to confirm and trigger payment

RULES:
1. ONLY describe products in the catalogue — never invent flavours
2. Any quantity is fine — there is NO minimum order restriction
3. If asked "what's available today?" use PRODUCTION STATUS — it reflects what was actually baked
4. INGREDIENT CAUTION is for your awareness only — never share stock levels with customers
5. If asked for the website URL, give it: {website_url if website_url else "cloudoven.vercel.app"}
6. Return ONLY valid JSON — nothing before or after the braces
7. Keep responses to 2-3 sentences — this is WhatsApp
8. Be warm, natural, and Kenyan

OUTPUT (strict JSON only):
{{"response":"message","confidence":"high|medium|low","escalate":false,"topic":"greeting|order|question|payment|fallback","order_update":{{"cookie_type":null,"quantity":null,"location":null,"stage":null}}}}"""

    # ==========================================================================
    # KISHA-TECH PROMPT — Sarah, electronics stock enquiry, no order flow
    # Fixed: AI name is Sarah across ALL Zovrix clients. Non-negotiable.
    # ==========================================================================

    def _build_kishatech_prompt(self, session: dict, data_context: dict) -> str:
        product_catalogue = data_context.get("product_catalogue", "Catalogue unavailable.")
        customer_context  = data_context.get("customer_context",  "New customer.")
        payment_context   = data_context.get("payment_context",   "")

        payment_note = f"\n{payment_context}" if payment_context else ""

        business_name     = "Kisha-Tech Electronics & Hardware Store"
        business_location = "Machakos Kenya Israel, opposite Manza College"
        operating_hours   = "Mon–Sat 7:00 AM – 7:00 PM, Sun 9:00 AM – 5:00 PM"
        website_url       = "voltaos.vercel.app"

        # Override with env if available
        if hasattr(settings, "BUSINESS_NAME") and "k-tech" in getattr(settings, "BUSINESS_NAME", "").lower():
            business_name     = settings.BUSINESS_NAME
            business_location = getattr(settings, "BUSINESS_LOCATION", business_location)
            operating_hours   = getattr(settings, "OPERATING_HOURS",   operating_hours)

        return f"""You are Sarah, the friendly WhatsApp shop assistant for {business_name}.

BUSINESS:
- Location: {business_location}
- Hours: {operating_hours}
- Website: {website_url}
- No delivery currently — walk-in or pickup only
- Payment: Cash or M-Pesa send money at the counter

{product_catalogue}

CUSTOMER:
{customer_context}
{payment_note}

YOUR JOB:
You help customers find what they need, confirm prices, and check availability.
This is an electronics and hardware shop. Customers ask things like:
- "Do you have MCB 16A?" → check catalogue, confirm price and stock
- "How much is a twin socket?" → give the price
- "What bulbs do you have?" → list the relevant items from catalogue
- "I need conduit pipes 20mm" → confirm availability and price
- "Do you do installations?" → No, we sell only. Refer customer to a local electrician.

ENQUIRY FLOW:
1. Greet warmly — "Karibu Kisha-Tech! 🔧"
2. Understand what they need (item name, type, size, quantity)
3. Check catalogue → confirm if in stock + price
4. If not in stock: say honestly "We don't have that right now" — never guess
5. For bulk orders (10+ units or KSh 5,000+): escalate to owner
6. For delivery requests: escalate to owner
7. Direct walk-ins to: opposite Manza College, Machakos

RULES:
1. ONLY quote items and prices from the STOCK CATALOGUE above — never invent prices
2. If item not in catalogue or qty is 0: say "We don't currently have that in stock"
3. Never promise delivery — walk-in only unless owner approves
4. Never negotiate prices — quote catalogue price, escalate if customer pushes back
5. Bulk order = 10+ pieces of same item OR total KSh 5,000+ → escalate to owner
6. Keep responses SHORT — 2-3 sentences max, this is WhatsApp
7. Be warm, confident, and helpful — you know this shop's stock
8. Speak naturally in English, mix in Swahili if customer does
9. Return ONLY valid JSON — nothing before or after the braces

OUTPUT (strict JSON only):
{{"response":"message","confidence":"high|medium|low","escalate":false,"topic":"stock_enquiry|price_check|availability|bulk_order|greeting|fallback","order_update":{{}}}}"""

    # ==========================================================================
    # PARSE + ERROR
    # ==========================================================================

    def _parse_response(self, raw: str) -> dict:
        clean = raw.strip()
        if "```" in clean:
            m = re.search(r'```(?:json)?\s*([\s\S]*?)```', clean)
            if m:
                clean = m.group(1).strip()
        if not clean.startswith("{"):
            m = re.search(r'\{[\s\S]*\}', clean)
            if m:
                clean = m.group(0)
        try:
            parsed = json.loads(clean)
            return {
                "response":     parsed.get("response",     settings.ESCALATION_MESSAGE),
                "confidence":   parsed.get("confidence",   "low"),
                "escalate":     bool(parsed.get("escalate", False)),
                "topic":        parsed.get("topic",        "unknown"),
                "order_update": parsed.get("order_update") or {},
            }
        except Exception as e:
            print(f"[AI ERROR] Parse failed: {repr(e)}\nRaw: {clean[:200]}")
            return self._error_response()

    def _error_response(self) -> dict:
        return {
            "response":     settings.ESCALATION_MESSAGE,
            "confidence":   "low",
            "escalate":     True,
            "topic":        "fallback",
            "order_update": {},
        }