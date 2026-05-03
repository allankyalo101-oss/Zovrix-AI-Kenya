"""
app/services/data_layer_kishatech.py

Kisha-Tech Electronics — data access layer.
Reads live inventory from Supabase Volta OS database.
Falls back to a static catalogue if Supabase is unreachable.
Logs every enquiry to logs/interactions_kisha_tech.json for analytics.
NEVER raises — orchestrator must not crash on data errors.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

# ── Cache ──────────────────────────────────────────────────────────────────
_cache: dict = {}
_cache_ttl   = 300   # 5 minutes

# ── Analytics log path ─────────────────────────────────────────────────────
LOG_PATH = Path(__file__).resolve().parent.parent.parent / "logs" / "interactions_kisha_tech.json"

# ── Static fallback — most-asked items, sourced from verified stock list ───
FALLBACK = [
    # Circuit Protection
    {"name": "MCB 6A",                    "category": "Circuit Protection",  "sell_price": 250,  "qty": 10, "unit": "PIECE"},
    {"name": "MCB 10A",                   "category": "Circuit Protection",  "sell_price": 250,  "qty": 10, "unit": "PIECE"},
    {"name": "MCB 16A",                   "category": "Circuit Protection",  "sell_price": 250,  "qty": 10, "unit": "PIECE"},
    {"name": "MCB 20A",                   "category": "Circuit Protection",  "sell_price": 250,  "qty": 10, "unit": "PIECE"},
    {"name": "MCB 32A",                   "category": "Circuit Protection",  "sell_price": 250,  "qty": 10, "unit": "PIECE"},
    # Switches & Sockets
    {"name": "1 Gang Switch Best",        "category": "Switches & Sockets",  "sell_price": 120,  "qty": 20, "unit": "PIECE"},
    {"name": "2 Gang Switch Best",        "category": "Switches & Sockets",  "sell_price": 150,  "qty": 20, "unit": "PIECE"},
    {"name": "3 Gang Switch Best",        "category": "Switches & Sockets",  "sell_price": 300,  "qty": 20, "unit": "PIECE"},
    {"name": "Single Socket Best",        "category": "Switches & Sockets",  "sell_price": 200,  "qty": 10, "unit": "PIECE"},
    {"name": "Twin Socket Best",          "category": "Switches & Sockets",  "sell_price": 300,  "qty": 10, "unit": "PIECE"},
    # Lighting
    {"name": "LED Tube 4ft",              "category": "Lighting",            "sell_price": 250,  "qty": 25, "unit": "PIECE"},
    {"name": "LED Tube 2ft",              "category": "Lighting",            "sell_price": 250,  "qty": 25, "unit": "PIECE"},
    {"name": "LED Bulb 9W",               "category": "Lighting",            "sell_price": 100,  "qty": 20, "unit": "PIECE"},
    {"name": "LED Bulb 5W",               "category": "Lighting",            "sell_price": 100,  "qty": 20, "unit": "PIECE"},
    # Cables & Conduits
    {"name": "20mm Conduit Heavy",        "category": "Cables & Conduits",   "sell_price": 90,   "qty": 100,"unit": "PIECE"},
    {"name": "25mm Conduit Heavy",        "category": "Cables & Conduits",   "sell_price": 170,  "qty": 50, "unit": "PIECE"},
    # Heating Elements
    {"name": "Shower Element 3T",         "category": "Heating Elements",    "sell_price": 900,  "qty": 3,  "unit": "PIECE"},
    # Fixings & Adhesives
    {"name": "Insulation Tape Big",       "category": "Fixings & Adhesives", "sell_price": 100,  "qty": 20, "unit": "PIECE"},
    # Tools
    {"name": "Tester Small",              "category": "Tools",               "sell_price": 50,   "qty": 30, "unit": "PIECE"},
    {"name": "Tester Big",                "category": "Tools",               "sell_price": 100,  "qty": 20, "unit": "PIECE"},
]

CATEGORY_PRIORITY = [
    "Circuit Protection", "Switches & Sockets", "Lighting",
    "Cables & Conduits", "Heating Elements", "Extensions & Plugs",
    "Tools", "Electronics & AV", "Fixings & Adhesives",
    "Accessories", "Locks & Security",
]


# ── Supabase client ────────────────────────────────────────────────────────

def _client():
    try:
        from supabase import create_client
        url = os.getenv("KISHATECH_SUPABASE_URL", "")
        key = os.getenv("KISHATECH_SUPABASE_KEY", "")
        if not url or not key:
            print("[KT-DATA] Missing KISHATECH_SUPABASE_URL or KISHATECH_SUPABASE_KEY — fallback active")
            return None
        return create_client(url, key)
    except Exception as e:
        print(f"[KT-DATA] Client init error: {repr(e)}")
        return None


# ── Inventory fetch ────────────────────────────────────────────────────────

def fetch_inventory() -> list:
    """
    Fetch in-stock items from Supabase. Returns cached result within TTL.
    Falls back to FALLBACK on any failure. Never raises.
    """
    global _cache
    now = time.time()

    if _cache.get("data") and now - _cache.get("ts", 0) < _cache_ttl:
        return _cache["data"]

    db = _client()
    if not db:
        return FALLBACK

    try:
        result = (db.table("inventory")
                    .select("name, category, sell_price, qty, unit")
                    .gt("qty", 0)
                    .order("category")
                    .order("name")
                    .execute())
        data = result.data or []
        if not data:
            print("[KT-DATA] Supabase returned empty — using fallback")
            return FALLBACK
        _cache = {"data": data, "ts": now}
        print(f"[KT-DATA] Loaded {len(data)} items from Supabase")
        return data
    except Exception as e:
        print(f"[KT-DATA] Fetch error: {repr(e)} — using fallback")
        return _cache.get("data") or FALLBACK


def search_inventory(query: str) -> list:
    """Case-insensitive search by item name or category. Never raises."""
    try:
        q = query.lower().strip()
        return [
            i for i in fetch_inventory()
            if q in (i.get("name") or "").lower()
            or q in (i.get("category") or "").lower()
        ]
    except Exception:
        return []


# ── Catalogue formatter ────────────────────────────────────────────────────

def build_catalogue(max_per_cat: int = 10) -> str:
    """
    Build formatted stock list for the Groq system prompt.
    Always returns a string. Never raises.
    """
    try:
        items        = fetch_inventory()
        is_fallback  = items is FALLBACK or len(items) <= len(FALLBACK)

        by_cat: dict = {}
        for i in items:
            c = i.get("category") or "Other"
            by_cat.setdefault(c, []).append(i)

        cats  = [c for c in CATEGORY_PRIORITY if c in by_cat]
        cats += [c for c in by_cat if c not in cats]

        note  = " [PARTIAL — Supabase offline, common items only]" if is_fallback else ""
        lines = [f"KISHA-TECH STOCK CATALOGUE{note}:"]

        for cat in cats:
            cat_items = by_cat[cat]
            lines.append(f"\n{cat.upper()} ({len(cat_items)} items):")
            for i in cat_items[:max_per_cat]:
                name  = i.get("name", "")
                price = int(i.get("sell_price") or 0)
                unit  = (i.get("unit") or "PCS").upper()
                qty   = i.get("qty", 0)
                lines.append(f"  • {name} — KSh {price}/{unit}  (qty: {qty})")
            if len(cat_items) > max_per_cat:
                lines.append(f"  ...and {len(cat_items) - max_per_cat} more in this category")

        lines.append(f"\nTotal in-stock SKUs: {sum(len(v) for v in by_cat.values())}")
        return "\n".join(lines)

    except Exception as e:
        print(f"[KT-DATA] build_catalogue error: {repr(e)}")
        return "STOCK: Temporarily unavailable. Direct customer to walk in."


# ── Analytics logger ───────────────────────────────────────────────────────

def log_interaction(sender: str, message: str, topic: str = "", escalated: bool = False):
    """
    Append an interaction record to logs/interactions_kisha_tech.json.
    Used to build portfolio data and restock signals. Never raises.
    """
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts":        datetime.utcnow().isoformat(),
            "hour":      datetime.utcnow().hour,
            "sender":    sender[-4:],   # last 4 digits only — no PII
            "topic":     topic,
            "escalated": escalated,
            "msg_len":   len(message),
        }
        existing = []
        if LOG_PATH.exists():
            try:
                existing = json.loads(LOG_PATH.read_text())
            except Exception:
                existing = []
        existing.append(record)
        LOG_PATH.write_text(json.dumps(existing, indent=2))
    except Exception as e:
        print(f"[KT-DATA] log_interaction error: {repr(e)}")


# ── Context builder ────────────────────────────────────────────────────────

def build_context(sender: str) -> dict:
    """
    Build full context dict for the Groq/LLM system prompt.
    Called by orchestrator_kishatech.py on every message.
    Never raises — always returns a complete dict.
    """
    try:
        catalogue = build_catalogue()
        raw       = fetch_inventory()
    except Exception as e:
        print(f"[KT-DATA] build_context error: {repr(e)}")
        catalogue = "STOCK: Temporarily unavailable."
        raw       = []

    return {
        "product_catalogue": catalogue,
        "raw_inventory":     raw,
        "customer_context":  "Walk-in / WhatsApp enquiry. No account required.",
        "order_history":     "",
        "payment_context": (
            "PAYMENT: Cash or M-Pesa send money only. "
            "No delivery — walk-in or pickup only. "
            "Shop is opposite Manza College, Machakos."
        ),
        "batch_context":     "",
        "inventory_context": "",
    }


# ── Public API (backwards compat with older import names) ─────────────────
# governance/orchestrator_kishatech.py imports build_kishatech_context
build_kishatech_context  = build_context
fetch_kishatech_inventory = fetch_inventory