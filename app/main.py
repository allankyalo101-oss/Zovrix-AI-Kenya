"""
app/main.py — Zovrix AI Kenya FastAPI entry point

Architecture:
  /webhook/cloud_oven  → CloudOven (Twilio account #1)
  /webhook/kisha_tech  → Kisha-Tech (Twilio account #2)
  /health              → uptime check

Each client has its own Twilio credentials in .env.
Twilio console for each account points to its specific endpoint.
"""

import logging
import os
from dotenv import load_dotenv

load_dotenv()

# ── Logging — visible in uvicorn stdout ───────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("zovrix")

from fastapi import FastAPI
from sqlalchemy import create_engine, text

from app.routes.whatsapp_cloudoven  import router as cloudoven_router
from app.routes.whatsapp_kishatech  import router as kishatech_router

app = FastAPI(title="Zovrix AI Kenya", version="2.0")

# ── Mount client routers at clean paths ───────────────────
# Twilio CloudOven webhook URL:  https://<render>/webhook/cloud_oven
# Twilio Kisha-Tech webhook URL: https://<render>/webhook/kisha_tech
app.include_router(cloudoven_router, prefix="/webhook")
app.include_router(kishatech_router, prefix="/webhook")

# ── Health ────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status":   "ok",
        "service":  "Zovrix AI Kenya",
        "clients":  ["cloud_oven", "kisha_tech"],
        "version":  "2.0",
    }

@app.get("/")
def root():
    return {"message": "Zovrix AI Kenya — Sarah is ready"}

# ── DB test (keep for diagnostics) ───────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        @app.get("/db-test")
        def db_test():
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    return {"status": "connected", "result": result.scalar()}
            except Exception as e:
                return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.warning(f"DB engine init failed (non-fatal): {e}")
else:
    logger.info("DATABASE_URL not set — db-test endpoint disabled")