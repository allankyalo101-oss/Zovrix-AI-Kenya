#!/usr/bin/env python3
"""
onboard_client.py — Zovrix AI Kenya Client Onboarding Script

Usage:
    python onboard_client.py

Prompts for client details and generates:
    clients/{client_id}/profile.env    — business profile for Sarah
    clients/{client_id}/responses.py   — custom response patterns (optional)

After running:
    1. Review and edit clients/{client_id}/profile.env
    2. Point Sarah's data layer at the client's Supabase instance (if applicable)
    3. Restart the service: ./start_sarah.sh
    4. Test with: send a WhatsApp message to the sandbox number

The client_id becomes the routing key. When Twilio receives a message,
the orchestrator loads the matching client profile by client_id.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────
CLIENTS_DIR = Path(__file__).parent / "clients"
SARAH_VERSION_OPTIONS = ["lite", "standard", "pro"]
PRICING = {
    "lite":     {"setup": 0,      "monthly": 7500,  "pilot": 3000},
    "standard": {"setup": 8000,   "monthly": 15000, "pilot": None},
    "pro":      {"setup": 10000,  "monthly": 25000, "pilot": None},
}

# ── Helpers ───────────────────────────────────────────────────────────────
def prompt(label: str, default: str = "", required: bool = True) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        val = input(f"  {label}{suffix}: ").strip()
        if not val and default:
            return default
        if val:
            return val
        if not required:
            return ""
        print("    ⚠️  This field is required.")

def prompt_choice(label: str, options: list, default: str = "") -> str:
    display = " / ".join(f"[{o}]" if o == default else o for o in options)
    while True:
        val = input(f"  {label} ({display}): ").strip().lower()
        if not val and default:
            return default
        if val in options:
            return val
        print(f"    ⚠️  Must be one of: {', '.join(options)}")

def slugify(text: str) -> str:
    """Convert business name to safe client_id."""
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower().strip())
    return slug.strip("_")[:40]

def banner(text: str):
    print(f"\n{'─' * 50}")
    print(f"  {text}")
    print(f"{'─' * 50}")

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print("\n" + "═" * 50)
    print("  Zovrix AI Kenya — Client Onboarding")
    print("  Sarah configuration generator")
    print("═" * 50)

    # ── 1. Business identity ──────────────────────────────────────────────
    banner("1 / 6 · Business Identity")
    business_name     = prompt("Business name (e.g. Acacia Boutique)")
    business_type     = prompt("Business type (e.g. boutique, bakery, pharmacy)")
    country           = prompt("Country", "Kenya")
    city              = prompt("City / town")
    location          = prompt("Specific location (street, landmark)")
    website           = prompt("Website URL", required=False)
    whatsapp_number   = prompt("Business WhatsApp number (e.g. 254712345678)")

    client_id_suggestion = slugify(business_name)
    client_id = prompt(f"Client ID (unique slug)", default=client_id_suggestion)

    # ── 2. Hours and availability ─────────────────────────────────────────
    banner("2 / 6 · Operating Hours")
    operating_hours = prompt("Operating hours", "8:00 AM – 7:00 PM daily")
    days_open       = prompt("Days open", "Monday to Sunday")

    # ── 3. Products and pricing ───────────────────────────────────────────
    banner("3 / 6 · Products & Pricing")
    print("  Enter products one per line. Press Enter on an empty line when done.")
    print("  Format: Product Name · KSh Price  (e.g. Silk Blouse · KSh 2500)")
    products = []
    i = 1
    while True:
        p = input(f"  Product {i}: ").strip()
        if not p:
            break
        products.append(p)
        i += 1

    # ── 4. Delivery and payment ───────────────────────────────────────────
    banner("4 / 6 · Fulfilment & Payment")
    default_fulfillment = prompt_choice("Default fulfilment", ["pickup", "delivery", "both"], "pickup")
    payment_methods     = prompt("Payment methods", "M-Pesa STK Push via website, cash at pickup")
    delivery_notes      = prompt("Delivery notes (e.g. free within 5km)", required=False)

    # ── 5. Brand voice ────────────────────────────────────────────────────
    banner("5 / 6 · Brand Voice")
    brand_tone    = prompt("Brand tone", "warm, professional, friendly")
    language      = prompt("Language style", "natural Kenyan English with Swahili touches")
    escalation_to = prompt("Escalation contact (name or number)", whatsapp_number)

    # ── 6. Sarah tier ─────────────────────────────────────────────────────
    banner("6 / 6 · Sarah Configuration")
    sarah_version = prompt_choice("Sarah tier", SARAH_VERSION_OPTIONS, "standard")
    has_website   = prompt_choice("Does client have a website with Supabase backend?", ["yes", "no"], "no")
    supabase_url  = prompt("Client Supabase URL", required=False) if has_website == "yes" else ""
    supabase_key  = prompt("Client Supabase service key", required=False) if has_website == "yes" else ""

    # ── Build paths ───────────────────────────────────────────────────────
    client_dir = CLIENTS_DIR / client_id
    if client_dir.exists():
        print(f"\n⚠️  Directory {client_dir} already exists.")
        overwrite = input("  Overwrite? (yes/no): ").strip().lower()
        if overwrite != "yes":
            print("  Aborted.")
            sys.exit(0)
    client_dir.mkdir(parents=True, exist_ok=True)

    # ── Build profile.env ─────────────────────────────────────────────────
    product_lines = "\n".join(
        f"PRODUCT_{i+1}={p}" for i, p in enumerate(products)
    ) if products else "# No products added yet — add PRODUCT_1=Name · KSh Price"

    pricing = PRICING[sarah_version]
    pricing_note = (
        f"KSh {pricing['pilot']:,} first month → KSh {pricing['monthly']:,}/month"
        if pricing.get("pilot")
        else f"Setup KSh {pricing['setup']:,} · KSh {pricing['monthly']:,}/month"
    )

    profile_content = f"""# ============================================================
# {business_name} — Zovrix AI Kenya Client Profile
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
# Client ID: {client_id}
# Sarah tier: {sarah_version.title()} ({pricing_note})
# ============================================================

# ── Identity ────────────────────────────────────────────────
CLIENT_ID={client_id}
CLIENT_NAME={business_name}
BUSINESS_NAME={business_name}
BUSINESS_TYPE={business_type}
COUNTRY={country}
CITY={city}

# ── Contact & Location ──────────────────────────────────────
BUSINESS_LOCATION={location}, {city}
WHATSAPP_NUMBER={whatsapp_number}
ESCALATION_NUMBER={escalation_to}
LOCATION={location}
{f'WEBSITE_URL={website}' if website else '# WEBSITE_URL='}

# ── Hours ───────────────────────────────────────────────────
OPERATING_HOURS={operating_hours}
DAYS_OPEN={days_open}

# ── Products & Pricing ──────────────────────────────────────
{product_lines}

# ── Fulfilment ──────────────────────────────────────────────
DEFAULT_FULFILLMENT={default_fulfillment}
PAYMENT_METHODS={payment_methods}
{f'DELIVERY_NOTES={delivery_notes}' if delivery_notes else '# DELIVERY_NOTES='}

# ── Brand Voice ─────────────────────────────────────────────
BRAND_TONE={brand_tone}
LANGUAGE_STYLE={language}
SARAH_PERSONA=warm, knowledgeable — speaks like a trusted team member

# ── Escalation ──────────────────────────────────────────────
ESCALATION_TRIGGER=complaint, refund, custom order, bulk order, specific question Sarah cannot answer
ESCALATION_MESSAGE=Let me connect you with our team directly. One moment.

# ── Database (fill in if client has Supabase backend) ───────
{f'SUPABASE_URL={supabase_url}' if supabase_url else '# SUPABASE_URL='}
{f'SUPABASE_SERVICE_KEY={supabase_key}' if supabase_key else '# SUPABASE_SERVICE_KEY='}

# ── Zovrix AI Kenya Config ───────────────────────────────────
ZOVRIX_CLIENT=true
SARAH_VERSION={sarah_version}
MOCK_MODE=false
ONBOARDED={datetime.now().strftime("%Y-%m-%d")}
"""

    profile_path = client_dir / "profile.env"
    profile_path.write_text(profile_content)

    # ── Build responses.py stub ───────────────────────────────────────────
    responses_content = f'''"""
responses.py — {business_name} custom response patterns
Generated by onboard_client.py on {datetime.now().strftime("%Y-%m-%d")}

Add intent-specific responses here.
Sarah will use these as supplementary context when the data layer
does not have a precise answer from the database.

Format:
    INTENT_NAME = "Response text"

Examples below — edit to match the client's voice.
"""

GREETING = "Habari! Welcome to {business_name}, how can I help you today?"

OUT_OF_STOCK = "That item is currently unavailable, but let me show you what we have."

DELIVERY_QUERY = "We deliver within {city}. Delivery details depend on your location — let me know where you are."

PAYMENT_QUERY = "We accept M-Pesa payments online and cash at our {location} location."

ESCALATION = "Let me connect you with our team directly for that. One moment."

CLOSING = "Asante for choosing {business_name}! Have a wonderful day."
'''

    responses_path = client_dir / "responses.py"
    responses_path.write_text(responses_content)

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "═" * 50)
    print("  ✅ Client onboarded successfully")
    print("═" * 50)
    print(f"\n  Client ID:    {client_id}")
    print(f"  Directory:    clients/{client_id}/")
    print(f"  Profile:      clients/{client_id}/profile.env")
    print(f"  Responses:    clients/{client_id}/responses.py")
    print(f"  Sarah tier:   {sarah_version.title()}")
    print(f"  Pricing:      {pricing_note}")
    print(f"\n  Next steps:")
    print(f"  1. Review clients/{client_id}/profile.env")
    print(f"  2. Edit clients/{client_id}/responses.py with client-specific language")
    if has_website == "yes" and (not supabase_url or not supabase_key):
        print(f"  3. ⚠️  Add Supabase credentials to profile.env")
    print(f"  4. Restart: ./start_sarah.sh")
    print(f"  5. Test with a WhatsApp message to the sandbox number")
    print(f"\n  Route Sarah to this client by setting:")
    print(f"  DEFAULT_CLIENT_ID={client_id}  (in .env)")
    print(f"  or via the webhook query param: ?client_id={client_id}")
    print()

if __name__ == "__main__":
    main()