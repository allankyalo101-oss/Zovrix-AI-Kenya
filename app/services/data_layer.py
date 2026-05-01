"""
data_layer.py — Sarah's Supabase Data Access Layer

Changes in this version:
    3. fetch_available_batches() — reads production_runs where status=ready
       and quantity_planned > quantity_actual (cookies still available).
       Sarah uses this to answer "what's available today?" from real batch data.

    4. fetch_low_inventory() — reads inventory items below reorder_threshold.
       Sarah uses this to avoid promising flavours that can't be baked.

    5. build_sarah_context() and build_sarah_context_async() both now include:
         "batch_context"     — formatted string for Groq system prompt
         "inventory_context" — formatted string for Groq system prompt
         "raw_batches"       — list for orchestrator logic
         "raw_inventory"     — list for orchestrator logic

All original working logic strictly retained.
"""

import os
import time
import asyncio
from typing import Optional

# ── CACHE ─────────────────────────────────────────────────────────────────────
_product_cache: list       = []
_product_cache_time: float = 0
_batch_cache: list         = []
_batch_cache_time: float   = 0
_inventory_cache: list     = []
_inventory_cache_time: float = 0

PRODUCT_CACHE_TTL   = 300   # 5 minutes
BATCH_CACHE_TTL     = 120   # 2 minutes — batches change during the day
INVENTORY_CACHE_TTL = 600   # 10 minutes — stock changes less often

# ── SUPABASE CLIENT SINGLETON ─────────────────────────────────────────────────
_supabase_client = None

def _get_supabase_client():
    """Return a singleton Supabase client with service key fallback."""
    global _supabase_client
    if _supabase_client:
        return _supabase_client
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY") or ""
        if not url or not key:
            print("[DATA] Supabase credentials missing — data layer unavailable")
            return None
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        print(f"[DATA] Supabase client creation failed: {repr(e)}")
        return None


# ── CACHE INVALIDATION ────────────────────────────────────────────────────────
def invalidate_product_cache():
    global _product_cache_time
    _product_cache_time = 0

def invalidate_batch_cache():
    global _batch_cache_time
    _batch_cache_time = 0

def invalidate_inventory_cache():
    global _inventory_cache_time
    _inventory_cache_time = 0


# ── PRODUCTS ──────────────────────────────────────────────────────────────────
def fetch_products() -> list:
    """Fetch all available products from Supabase, cached 5 minutes."""
    global _product_cache, _product_cache_time
    now = time.time()
    if _product_cache and (now - _product_cache_time) < PRODUCT_CACHE_TTL:
        return _product_cache

    client = _get_supabase_client()
    if not client:
        return _product_cache

    try:
        result = client.table("products") \
            .select("id, name, price, description, stock_quantity, available, image_emoji, rating") \
            .eq("available", True) \
            .order("id", desc=False) \
            .execute()

        _product_cache      = getattr(result, "data", []) or []
        _product_cache_time = now
        print(f"[DATA] Products fetched: {len(_product_cache)} available")
        return _product_cache

    except Exception as e:
        print(f"[DATA] Product fetch failed: {repr(e)}")
        return _product_cache


def format_product_catalogue(products: list) -> str:
    if not products:
        return "Product catalogue temporarily unavailable. Ask customer to check the website or try again shortly."

    lines = ["Available products:"]
    for p in products:
        stock        = p.get("stock_quantity")
        name         = p.get("name", "Unknown")
        price        = p.get("price", 0)
        desc         = p.get("description", "")

        if stock is not None and stock == 0:
            availability = "[OUT OF STOCK — do not offer this product]"
        elif stock is not None and stock <= 5:
            availability = f"[Only {stock} remaining — mention this]"
        else:
            availability = "[In stock]"

        desc_part = f" — {desc}" if desc else ""
        lines.append(f"  • {name}: KES {price}{desc_part} {availability}")

    return "\n".join(lines)


# ── AVAILABLE BATCHES ─────────────────────────────────────────────────────────
def fetch_available_batches() -> list:
    """
    Fetch today's ready batches from production_runs.

    A batch is 'available' when:
      - status = 'ready'
      - quantity_planned > quantity_actual (cookies remain unsold)

    Sarah uses this to tell customers what is physically ready for pickup
    or delivery today, rather than guessing from the product catalogue.
    Cached 2 minutes — batches change during the day as stock sells out.
    """
    global _batch_cache, _batch_cache_time
    now = time.time()
    if _batch_cache and (now - _batch_cache_time) < BATCH_CACHE_TTL:
        return _batch_cache

    client = _get_supabase_client()
    if not client:
        return _batch_cache

    try:
        result = client.table("production_runs") \
            .select("id, recipe_name, quantity_planned, quantity_actual, status, batch_date, oven_used, notes") \
            .eq("status", "ready") \
            .order("batch_date", desc=False) \
            .execute()

        all_ready = getattr(result, "data", []) or []

        # Only include batches that still have stock remaining
        available = [
            b for b in all_ready
            if (b.get("quantity_planned") or 0) > (b.get("quantity_actual") or 0)
        ]

        # Attach remaining count to each batch for easy formatting
        for b in available:
            b["quantity_remaining"] = (
                (b.get("quantity_planned") or 0) - (b.get("quantity_actual") or 0)
            )

        _batch_cache      = available
        _batch_cache_time = now
        print(f"[DATA] Batches fetched: {len(available)} ready with stock")
        return _batch_cache

    except Exception as e:
        print(f"[DATA] Batch fetch failed: {repr(e)}")
        return _batch_cache


def format_batch_context(batches: list) -> str:
    """
    Format available batches for Sarah's Groq system prompt.

    Tells Sarah exactly what was baked today and how many remain.
    This is the ground truth for availability — not the product catalogue.
    """
    if not batches:
        return (
            "PRODUCTION STATUS: No batches are ready for pickup or delivery right now. "
            "If a customer asks about availability, tell them honestly and suggest they "
            "check back later or place a pre-order via the website."
        )

    lines = ["PRODUCTION STATUS — Ready for pickup/delivery today:"]
    for b in batches:
        name      = b.get("recipe_name") or "Cookie batch"
        remaining = b.get("quantity_remaining", 0)
        date      = (b.get("batch_date") or "")[:10]
        notes     = b.get("notes", "")

        note_part = f" ({notes})" if notes else ""
        lines.append(
            f"  • {name}: {remaining} available{note_part} "
            f"[batch date: {date}]"
        )

    lines.append(
        "Use this to confirm availability before promising a customer "
        "their preferred flavour is in stock."
    )
    return "\n".join(lines)


# ── INVENTORY (INGREDIENTS) ───────────────────────────────────────────────────
def fetch_low_inventory() -> list:
    """
    Fetch ingredients that are at or below their reorder threshold.

    Sarah uses this context passively — she does not recite stock levels
    to customers, but she avoids promising flavours whose key ingredients
    are critically low. The orchestrator can also use this to flag issues.
    Cached 10 minutes.
    """
    global _inventory_cache, _inventory_cache_time
    now = time.time()
    if _inventory_cache and (now - _inventory_cache_time) < INVENTORY_CACHE_TTL:
        return _inventory_cache

    client = _get_supabase_client()
    if not client:
        return _inventory_cache

    try:
        result = client.table("inventory") \
            .select("id, name, unit, quantity_available, reorder_threshold") \
            .order("name") \
            .execute()

        all_items = getattr(result, "data", []) or []

        # Filter to items at or below threshold (where threshold is set)
        low = [
            item for item in all_items
            if (item.get("reorder_threshold") or 0) > 0
            and (item.get("quantity_available") or 0) <= (item.get("reorder_threshold") or 0)
        ]

        _inventory_cache      = low
        _inventory_cache_time = now

        if low:
            names = [i.get("name", "?") for i in low]
            print(f"[DATA] Low inventory: {', '.join(names)}")
        else:
            print(f"[DATA] Inventory: all items adequately stocked")

        return _inventory_cache

    except Exception as e:
        print(f"[DATA] Inventory fetch failed: {repr(e)}")
        return _inventory_cache


def format_inventory_context(low_items: list) -> str:
    """
    Format low-stock ingredients as a caution note for Sarah's system prompt.

    Sarah does not mention ingredient stock to customers — she uses this
    context to avoid over-promising on flavours that may not be bakeable.
    """
    if not low_items:
        return "INGREDIENT STOCK: All key ingredients are adequately stocked."

    out_of_stock = [i for i in low_items if (i.get("quantity_available") or 0) <= 0]
    running_low  = [i for i in low_items if (i.get("quantity_available") or 0) > 0]

    lines = ["INGREDIENT CAUTION (do not share with customers):"]

    if out_of_stock:
        names = ", ".join(i.get("name", "?") for i in out_of_stock)
        lines.append(
            f"  OUT OF STOCK: {names}. "
            f"Avoid promising flavours that require these ingredients."
        )

    if running_low:
        names = ", ".join(i.get("name", "?") for i in running_low)
        lines.append(
            f"  RUNNING LOW: {names}. "
            f"These may run out before the next restock."
        )

    return "\n".join(lines)


# ── CUSTOMER PROFILE ──────────────────────────────────────────────────────────
def fetch_customer_by_phone(phone: str) -> Optional[dict]:
    """
    Look up a customer in Supabase by phone number (multi-format).

    Returns {"needs_signup": True} when number is not registered,
    None when Supabase is unreachable (don't block ordering on infra failure).
    """
    if not phone:
        return None

    client = _get_supabase_client()
    if not client:
        return None

    cleaned = phone.strip().replace(" ", "")
    formats = {cleaned, cleaned.lstrip("+")}
    if cleaned.startswith("+254"):
        formats.update({"0" + cleaned[4:]})
    if cleaned.startswith("254"):
        formats.update({"+" + cleaned, "0" + cleaned[3:]})
    if cleaned.startswith("0"):
        formats.update({"254" + cleaned[1:], "+254" + cleaned[1:]})

    try:
        result = client.table("profiles") \
            .select("id, full_name, email, phone, created_at") \
            .in_("phone", list(formats)) \
            .limit(1) \
            .execute()

        users = getattr(result, "data", []) or []
        if users:
            user = users[0]
            print(f"[DATA] Customer found: {user.get('full_name')} ({phone[-4:]})")
            return {
                "customer_id":    user.get("id"),
                "customer_name":  user.get("full_name"),
                "customer_email": user.get("email"),
                "customer_phone": user.get("phone"),
                "customer_since": user.get("created_at", "")[:10],
                "needs_signup":   False,
            }

        print(f"[DATA] No account found for {phone[-4:]} — needs signup")
        return {"needs_signup": True}

    except Exception as e:
        print(f"[DATA] Customer lookup failed: {repr(e)}")
        return None


def format_customer_context(customer: Optional[dict]) -> str:
    if not customer or customer.get("needs_signup"):
        return (
            "IMPORTANT: This customer does NOT have a CloudOven account. "
            "They cannot complete payment without signing up first. "
            "If they try to order, direct them to sign up at cloudoven.vercel.app before proceeding."
        )
    if not customer.get("customer_name"):
        return "Customer not registered in the system. Treat as a new customer."

    name  = customer.get("customer_name", "")
    since = customer.get("customer_since", "")
    since_part = f" (customer since {since})" if since else ""
    return f"Registered customer: {name}{since_part}. Use their name warmly."


# ── ORDER HISTORY ─────────────────────────────────────────────────────────────
def fetch_customer_orders(customer_id: str, limit: int = 5) -> list:
    if not customer_id:
        return []

    client = _get_supabase_client()
    if not client:
        return []

    try:
        result = client.table("orders") \
            .select("id, status, amount, items, delivery_address, created_at") \
            .eq("user_id", customer_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        orders = getattr(result, "data", []) or []
        print(f"[DATA] Orders fetched for customer: {len(orders)}")
        return orders

    except Exception as e:
        print(f"[DATA] Order fetch failed: {repr(e)}")
        return []


def format_order_history(orders: list) -> str:
    if not orders:
        return "No previous orders."
    lines = [f"Recent orders ({len(orders)}):"]
    for o in orders[:3]:
        status = o.get("status", "unknown")
        amount = o.get("amount", 0)
        date   = o.get("created_at", "")[:10]
        items  = o.get("items", [])
        item_summary = ""
        if isinstance(items, list) and items:
            parts = [f"{i.get('quantity',1)}x {i.get('name','item')}" for i in items[:2]]
            item_summary = ", ".join(parts)
            if len(items) > 2:
                item_summary += f" +{len(items)-2} more"
        lines.append(f"  • {date}: {item_summary} — KES {amount} [{status}]")
    return "\n".join(lines)


# ── TRANSACTION STATUS ────────────────────────────────────────────────────────
def fetch_transaction_by_order(order_id: str) -> Optional[dict]:
    if not order_id:
        return None
    client = _get_supabase_client()
    if not client:
        return None
    try:
        result = client.table("intasend_transactions") \
            .select("invoice_id, status, mpesa_receipt, amount, failure_reason, updated_at") \
            .eq("order_id", order_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        txns = getattr(result, "data", []) or []
        if txns:
            txn = txns[0]
            print(f"[DATA] Transaction found for order {order_id[:8]}: {txn.get('status')}")
            return txn
        print(f"[DATA] No transaction found for order {order_id[:8]}")
        return None
    except Exception as e:
        print(f"[DATA] Transaction fetch failed: {repr(e)}")
        return None


def fetch_pending_payment_for_customer(customer_id: str) -> Optional[dict]:
    if not customer_id:
        return None
    client = _get_supabase_client()
    if not client:
        return None
    try:
        result = client.table("orders") \
            .select("id, amount, items, created_at") \
            .eq("user_id", customer_id) \
            .eq("status", "pending_payment") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        orders = getattr(result, "data", []) or []
        if orders:
            order = orders[0]
            print(f"[DATA] Pending order found for customer: {order['id'][:8]}")
            return order
        return None
    except Exception as e:
        print(f"[DATA] Pending order check failed: {repr(e)}")
        return None


def format_payment_context(pending_order: Optional[dict]) -> str:
    if not pending_order:
        return ""
    amount       = pending_order.get("amount", 0)
    items        = pending_order.get("items", [])
    order_id     = pending_order.get("id", "")[:8]
    item_summary = ""
    if isinstance(items, list) and items:
        item_summary = ", ".join(
            [f"{i.get('quantity',1)}x {i.get('name','item')}" for i in items]
        )
    return (
        f"UNPAID ORDER: Customer has a pending order (ref {order_id}) "
        f"for {item_summary} — KES {amount}. "
        f"If they mention payment or their order, reference this."
    )


# ── ASYNC HELPERS ─────────────────────────────────────────────────────────────
async def _run_async(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

async def fetch_products_async() -> list:
    return await _run_async(fetch_products)

async def fetch_available_batches_async() -> list:
    return await _run_async(fetch_available_batches)

async def fetch_low_inventory_async() -> list:
    return await _run_async(fetch_low_inventory)

async def fetch_customer_orders_async(customer_id: str) -> list:
    return await _run_async(fetch_customer_orders, customer_id)

async def fetch_pending_payment_for_customer_async(customer_id: str) -> Optional[dict]:
    return await _run_async(fetch_pending_payment_for_customer, customer_id)


# ── FULL CONTEXT BUNDLE ───────────────────────────────────────────────────────
def build_sarah_context(sender: str, customer: Optional[dict] = None) -> dict:
    """
    Sync context builder. Now includes production awareness:
      - batch_context:     what was baked and is ready today
      - inventory_context: which ingredients are running low
    """
    products    = fetch_products()
    batches     = fetch_available_batches()
    low_stock   = fetch_low_inventory()
    customer_id = customer.get("customer_id") if customer and not customer.get("needs_signup") else None
    orders      = fetch_customer_orders(customer_id) if customer_id else []
    pending     = fetch_pending_payment_for_customer(customer_id) if customer_id else None

    return {
        "product_catalogue":   format_product_catalogue(products),
        "batch_context":       format_batch_context(batches),
        "inventory_context":   format_inventory_context(low_stock),
        "customer_context":    format_customer_context(customer),
        "order_history":       format_order_history(orders),
        "payment_context":     format_payment_context(pending),
        "raw_products":        products,
        "raw_batches":         batches,
        "raw_inventory":       low_stock,
        "raw_orders":          orders,
        "raw_pending_order":   pending,
        "customer_registered": bool(
            customer
            and not customer.get("needs_signup")
            and customer.get("customer_id")
        ),
    }


async def build_sarah_context_async(sender: str, customer: Optional[dict] = None) -> dict:
    """
    Async context builder — fetches all sources concurrently.
    Products, batches, and inventory are fetched in parallel with
    customer-specific data to minimise latency.
    """
    customer_id = customer.get("customer_id") if customer and not customer.get("needs_signup") else None

    # Always fetch: products, batches, inventory
    base_tasks = [
        fetch_products_async(),
        fetch_available_batches_async(),
        fetch_low_inventory_async(),
    ]

    # Customer-specific tasks only if registered
    customer_tasks = []
    if customer_id:
        customer_tasks = [
            fetch_customer_orders_async(customer_id),
            fetch_pending_payment_for_customer_async(customer_id),
        ]

    all_results = await asyncio.gather(*base_tasks, *customer_tasks, return_exceptions=True)

    def safe(val):
        return val if not isinstance(val, Exception) else None

    products  = safe(all_results[0]) or []
    batches   = safe(all_results[1]) or []
    low_stock = safe(all_results[2]) or []
    orders    = safe(all_results[3]) if len(all_results) > 3 else []
    pending   = safe(all_results[4]) if len(all_results) > 4 else None

    return {
        "product_catalogue":   format_product_catalogue(products),
        "batch_context":       format_batch_context(batches),
        "inventory_context":   format_inventory_context(low_stock),
        "customer_context":    format_customer_context(customer),
        "order_history":       format_order_history(orders),
        "payment_context":     format_payment_context(pending),
        "raw_products":        products,
        "raw_batches":         batches,
        "raw_inventory":       low_stock,
        "raw_orders":          orders,
        "raw_pending_order":   pending,
        "customer_registered": bool(
            customer
            and not customer.get("needs_signup")
            and customer.get("customer_id")
        ),
    }