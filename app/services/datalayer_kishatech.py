"""
data_layer_kishatech.py — Kisha-Tech Electronics data access layer

Reads from Kisha-Tech's own Supabase project (Volta OS database).
Falls back to a static catalogue when Supabase is unavailable so
Sarah always responds rather than escalating on a connection error.

Tables used: inventory (name, category, sell_price, qty, unit)
Financial tables are NOT read — owner-only.
"""

import os
import time
from typing import Optional

# ── Cache ─────────────────────────────────────────────────────
_inventory_cache: dict  = {}
_cache_ttl: int         = 300  # 5 minutes

# ── Static fallback catalogue ─────────────────────────────────
# Used when Supabase is unreachable. Covers the most common
# customer enquiries so Sarah is never completely blind.
STATIC_FALLBACK = [
    {"name":"MCB 6A",             "category":"Circuit Protection",  "sell_price":250,  "qty":10, "unit":"PIECE"},
    {"name":"MCB 10A",            "category":"Circuit Protection",  "sell_price":250,  "qty":10, "unit":"PIECE"},
    {"name":"MCB 16A",            "category":"Circuit Protection",  "sell_price":250,  "qty":10, "unit":"PIECE"},
    {"name":"MCB 20A",            "category":"Circuit Protection",  "sell_price":250,  "qty":10, "unit":"PIECE"},
    {"name":"MCB 32A",            "category":"Circuit Protection",  "sell_price":250,  "qty":10, "unit":"PIECE"},
    {"name":"1 Gang Switch Best", "category":"Switches & Sockets",  "sell_price":120,  "qty":20, "unit":"PIECE"},
    {"name":"2 Gang Switch Best", "category":"Switches & Sockets",  "sell_price":150,  "qty":20, "unit":"PIECE"},
    {"name":"3 Gang Switch Best", "category":"Switches & Sockets",  "sell_price":300,  "qty":20, "unit":"PIECE"},
    {"name":"Single Socket Best", "category":"Switches & Sockets",  "sell_price":200,  "qty":10, "unit":"PIECE"},
    {"name":"Twin Socket Best",   "category":"Switches & Sockets",  "sell_price":300,  "qty":10, "unit":"PIECE"},
    {"name":"LED Tube 4ft",       "category":"Lighting",            "sell_price":250,  "qty":25, "unit":"PIECE"},
    {"name":"LED Tube 2ft",       "category":"Lighting",            "sell_price":250,  "qty":25, "unit":"PIECE"},
    {"name":"LED Bulb 9W",        "category":"Lighting",            "sell_price":100,  "qty":20, "unit":"PIECE"},
    {"name":"LED Bulb 5W",        "category":"Lighting",            "sell_price":100,  "qty":20, "unit":"PIECE"},
    {"name":"Insulation Tape Big","category":"Fixings & Adhesives", "sell_price":100,  "qty":20, "unit":"PIECE"},
    {"name":"20mm Conduit Heavy", "category":"Cables & Conduits",   "sell_price":90,   "qty":100,"unit":"PIECE"},
    {"name":"25mm Conduit Heavy", "category":"Cables & Conduits",   "sell_price":170,  "qty":50, "unit":"PIECE"},
    {"name":"Tester Small",       "category":"Tools",               "sell_price":50,   "qty":30, "unit":"PIECE"},
    {"name":"Tester Big",         "category":"Tools",               "sell_price":100,  "qty":20, "unit":"PIECE"},
]

def _get_client():
    """Get Kisha-Tech Supabase client. Returns None if credentials missing."""
    try:
        from supabase import create_client
        url = os.getenv("KISHATECH_SUPABASE_URL", "")
        key = os.getenv("KISHATECH_SUPABASE_KEY", "")
        if not url or not key:
            print("[KISHATECH DB] Missing KISHATECH_SUPABASE_URL or KISHATECH_SUPABASE_KEY — using static fallback")
            return None
        return create_client(url, key)
    except Exception as e:
        print(f"[KISHATECH DB] Client error: {repr(e)}")
        return None


def fetch_kishatech_inventory() -> list:
    """
    Fetch in-stock inventory from Volta OS Supabase.
    Returns static fallback if Supabase is unavailable.
    Never raises — orchestrator must not crash on data layer errors.
    """
    global _inventory_cache

    now = time.time()
    if _inventory_cache.get("data") and now - _inventory_cache.get("ts", 0) < _cache_ttl:
        return _inventory_cache["data"]

    client = _get_client()
    if not client:
        print("[KISHATECH DB] Using static fallback catalogue")
        return STATIC_FALLBACK

    try:
        result = client.table("inventory") \
            .select("name, category, sell_price, qty, unit") \
            .gt("qty", 0) \
            .order("category") \
            .order("name") \
            .execute()

        data = result.data or []
        if not data:
            print("[KISHATECH DB] Empty result — using static fallback")
            return STATIC_FALLBACK

        _inventory_cache = {"data": data, "ts": now}
        print(f"[KISHATECH DB] Inventory loaded: {len(data)} in-stock items")
        return data

    except Exception as e:
        print(f"[KISHATECH DB] Fetch error: {repr(e)} — using static fallback")
        return _inventory_cache.get("data") or STATIC_FALLBACK


def search_kishatech_inventory(query: str) -> list:
    """Search inventory by name or category. Always returns a list."""
    try:
        all_items = fetch_kishatech_inventory()
        q = query.lower().strip()
        return [
            item for item in all_items
            if q in (item.get("name") or "").lower()
            or q in (item.get("category") or "").lower()
        ]
    except Exception:
        return []


def build_kishatech_catalogue(max_items_per_category: int = 8) -> str:
    """
    Build formatted stock list for the Groq system prompt.
    Always returns a string — never raises.
    """
    try:
        all_items = fetch_kishatech_inventory()
        is_fallback = all_items is STATIC_FALLBACK or (
            len(all_items) <= len(STATIC_FALLBACK) and
            any(i.get("name") == "MCB 16A" for i in all_items)
        )

        by_cat: dict = {}
        for item in all_items:
            cat = item.get("category") or "Other"
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(item)

        PRIORITY = [
            "Circuit Protection", "Switches & Sockets", "Lighting",
            "Cables & Conduits", "Heating Elements", "Extensions & Plugs",
            "Tools", "Electronics & AV", "Fixings & Adhesives",
            "Accessories", "Locks & Security",
        ]
        ordered_cats = [c for c in PRIORITY if c in by_cat]
        ordered_cats += [c for c in by_cat if c not in ordered_cats]

        header = "STOCK CATALOGUE (items currently in stock)"
        if is_fallback:
            header += " — NOTE: Live Supabase unavailable, showing common items only"
        lines = [header + ":"]

        for cat in ordered_cats:
            items = by_cat[cat]
            lines.append(f"\n{cat.upper()} ({len(items)} items):")
            for item in items[:max_items_per_category]:
                name  = item.get("name", "")
                price = item.get("sell_price", 0)
                unit  = (item.get("unit") or "PCS").upper()
                qty   = item.get("qty", 0)
                lines.append(f"  • {name} — KSh {int(price)}/{unit} (qty: {qty})")
            if len(items) > max_items_per_category:
                lines.append(f"  ... and {len(items) - max_items_per_category} more in this category")

        total = sum(len(v) for v in by_cat.values())
        lines.append(f"\nTotal items in stock: {total}")
        return "\n".join(lines)

    except Exception as e:
        print(f"[KISHATECH DB] build_catalogue error: {repr(e)}")
        return "STOCK CATALOGUE: Temporarily unavailable. Direct customers to walk in."


def build_kishatech_context(sender: str) -> dict:
    """
    Build full data context dict for the Groq prompt.
    Never raises — always returns a complete dict.
    """
    try:
        catalogue = build_kishatech_catalogue()
        raw       = fetch_kishatech_inventory()
    except Exception as e:
        print(f"[KISHATECH DB] Context build error: {repr(e)}")
        catalogue = "STOCK CATALOGUE: Temporarily unavailable."
        raw       = []

    return {
        "product_catalogue": catalogue,
        "raw_inventory":     raw,
        "customer_context":  "New customer — no account required for enquiries.",
        "order_history":     "No order history.",
        "payment_context":   (
            "PAYMENT: Cash or M-Pesa send money only. "
            "No STK Push yet — customer pays at counter or sends M-Pesa manually. "
            "For orders: customer comes to shop, opposite Manza College, Machakos."
        ),
        "batch_context":     "",
        "inventory_context": "",
    }